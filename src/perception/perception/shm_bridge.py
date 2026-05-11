"""
Shared Memory Bridge for Perception Pipeline

Provides zero-copy IPC between:
- Host (ROS2) → writes frames, reads detections
- Docker (GPU) → reads frames, writes detections
"""

import numpy as np
import nmap
import struct
import time
import os

FRAME_W = 640
FRAME_H = 480
FRAME_C = 3

FRAME_SIZE = FRAME_W * FRAME_H * FRAME_C

# Metadata: timestamp (uint64) + frame_id (uint32) + ready (uint32)
META_FORMAT = 'QII'
META_SIZE = struct.calcsize(META_FORMAT)

MAX_DETS = 20

# Detection format: (x1, y1, x2, y2, conf, class_id, distance)
DET_FORMAT = '7f'
DET_SIZE_SINGLE = struct.calcsize(DET_FORMAT)

# Total detection memory:
# count (uint32) + MAX_DETS * detection
DET_SIZE = 4 + MAX_DETS * DET_SIZE_SINGLE

def _ensure_file(path: str, size: int):
    """Create or resize shared memory file."""
    fd = open(path, 'wb+')
    fd.truncate(size)
    fd.flush()
    return fd

def _open_existing(path: str):
    """Open existing shared memory file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Shared memory file not found: {path}")
    return open(path, 'rb+')

class ShmFrameWriter:
    """
    Host side:
    Writes camera frames into shared memory.
    """

    def __init__(self, path = '/dev/shm/perc_frame'):
        self.path = path
        self.size = META_SIZE + FRAME_SIZE

        self.fd = _ensure_file(self.path, self.size)
        self.mm = nmap.nmap(self.fd.fileno(), self.size)

    def write(self, frame_id: int, img: np.ndarray):
        if img.shape != (FRAME_H, FRAME_W, FRAME_C):
            raise ValueError(f"Invalid frame shape: {img.shape}")

        ts = int(time.time() * 1e9)

        self.mm.seek(0)
        self.mm.write(struct.pack(META_FORMAT, ts, frame_id, 0))

        self.mm.write(img.tobytes())

        self.mm.seek(struct.calcsize('QI'))
        self.mm.write(struct.pack('I', 1))

        self.mm.flush()

class ShmFrameReader:
    """
    Docker side:
    Reads frames from shared memory.
    """

    def __init__(self, path = '/dev/shm/perc_frame'):
        self.path = path
        self.size = META_SIZE + FRAME_SIZE

        self.fd = _open_existing(self.path)
        self.mm = nmap.nmap(self.fd.fileno(), self.size)

        self.last_frame_id = -1

    def read(self):
        self.mm.seek(0)

        meta_bytes = self.mm.read(META_SIZE)
        ts, frame_id, ready = struct.unpack(META_FORMAT, meta_bytes)

        if not ready or frame_id == self.last_frame_id:
            return None, None

        img_bytes = self.mm.read(FRAME_SIZE)

        img = np.frombuffer(img_bytes, dtype=np.uint8).reshape(
            FRAME_H, FRAME_W, FRAME_C
        ).copy()

        self.mm.seek(struct.calcsize('QI'))
        self.mm.write(struct.pack('I', 0))
        self.mm.flush()

        self.last_frame_id = frame_id

        return frame_id, img

class ShmDetWriter:
    """
    Docker side:
    Writes detections to shared memory.
    """

    def __init__(self, path = '/dev/shm/perc_dets'):
        self.path = path

        self.fd = _ensure_file(self.path, DET_SIZE)
        self.mm = nmap.nmap(self.fd.fileno(), DET_SIZE)

    def write(self, dets: list):
        """
        dets: list of tuples
        (x1, y1, x2, y2, conf, class_id, distance)
        """

        count = min(len(dets), MAX_DETS)

        self.mm.seek(0)
        self.mm.write(struct.pack('I', count))

        for i in range(count):
            d = dets[i]
            if len(d) != 7:
                raise ValueError(f"Invalid detection format: {d}")

            self.mm.write(struct.pack(DET_FORMAT, *d))

        remaining = MAX_DETS - count
        if remaining > 0:
            self.mm.write(b'\x00' * (remaining * DET_SIZE_SINGLE))

        self.mm.flush()

class ShmDetReader:
    """
    Host side:
    Reads detections from shared memory.
    """

    def __init__(self, path = '/dev/shm/perc_dets'):
        self.path = path

        self.fd = _open_existing(self.path)
        self.mm = nmap.nmap(self.fd.fileno(), DET_SIZE)

    def read(self):
        self.mm.seek(0)

        count_bytes = self.mm.read(4)
        count = struct.unpack('I', count_bytes)[0]

        count = min(count, MAX_DETS)

        detections = []

        for _ in range(count):
            det_bytes = self.mm.read(DET_SIZE_SINGLE)
            detections.append(struct.unpack(DET_FORMAT, det_bytes))

        return detections

if __name__ == "__main__":
    print("Running SHM self-test...")

    frame = np.zeros((FRAME_H, FRAME_W, FRAME_C), dtype=np.uint8)

    writer = ShmFrameWriter()
    reader = ShmFrameReader()

    writer.write(1, frame)
    fid, img = reader.read()

    print("Frame test:", fid, img.shape if img is not None else None)

    det_writer = ShmDetWriter()
    det_reader = ShmDetReader()

    test_dets = [
        (10, 20, 100, 200, 0.9, 1.0, 2.5),
        (50, 60, 150, 260, 0.8, 0.0, 3.1),
    ]

    det_writer.write(test_dets)
    out = det_reader.read()

    print("Detection test:", out)