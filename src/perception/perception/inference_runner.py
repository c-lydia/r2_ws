"""
Dual-backend inference runner:

Priority:
1. TensorRT (.engine)
2. ONNX Runtime fallback
"""

import os
import time
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    import tensorrt as trt
else:
    trt = None

try:
    import tensorrt as trt
except ImportError:
    trt = None

import pycuda.driver as cuda
import pycuda.autoinit


from shm_bridge import SHMFrameReader, SHMDetWriter

MODEL_PATH = os.environ.get("MODEL_PATH", "/workspace/models/yolov8n.onnx")
CONF_THRESH = float(os.environ.get("CONF_THRESH", 0.4))
LOG_INTERVAL = 30

class ONNXBackend:
    def __init__(self, path):
        import onnxruntime as ort

        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        try:
            self.session = ort.InferenceSession(path, providers=providers)
        except Exception:
            print("[ONNX] CUDA failed, using CPU")
            self.session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])

        self.input_name = self.session.get_inputs()[0].name

        print(f"[ONNX] Loaded: {path}")
        print(f"[ONNX] Providers: {self.session.get_providers()}")

    def infer(self, inp):
        return self.session.run(None, {self.input_name: inp})

class TensorRTBackend:
    def __init__(self, path):
        self.trt = trt
        self.cuda = cuda

        self.logger = trt.Logger(trt.Logger.WARNING)
        self.runtime = trt.Runtime(self.logger)

        print(f"[TensorRT] Loading engine: {path}")

        with open(path, "rb") as f:
            self.engine = self.runtime.deserialize_cuda_engine(f.read())

        if self.engine is None:
            raise RuntimeError("Failed to load TensorRT engine")

        self.context = self.engine.create_execution_context()
        self.stream = cuda.Stream()

        self.bindings = []
        self.host_inputs = []
        self.device_inputs = []
        self.host_outputs = []
        self.device_outputs = []

        for i in range(self.engine.num_bindings):
            shape = self.context.get_binding_shape(i)
            dtype = trt.nptype(self.engine.get_binding_dtype(i))
            size = int(np.prod(shape))

            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)

            self.bindings.append(int(device_mem))

            if self.engine.binding_is_input(i):
                self.host_inputs.append(host_mem)
                self.device_inputs.append(device_mem)
            else:
                self.host_outputs.append(host_mem)
                self.device_outputs.append(device_mem)

        print("[TensorRT] Ready")

    def infer(self, img):
        cuda = self.cuda

        host_in = self.host_inputs[0]

        rgb = img[:, :, ::-1]
        rgb = rgb.astype(np.float32) / 255.0
        chw = np.transpose(rgb, (2, 0, 1))

        np.copyto(host_in, chw.ravel())

        cuda.memcpy_htod_async(self.device_inputs[0], host_in, self.stream)

        self.context.execute_async_v2(
            bindings=self.bindings,
            stream_handle=self.stream.handle
        )

        outputs = []
        for host_out, device_out in zip(self.host_outputs, self.device_outputs):
            cuda.memcpy_dtoh_async(host_out, device_out, self.stream)
            outputs.append(host_out)

        self.stream.synchronize()

        out = outputs[0]
        return [out.reshape(1, -1, out.shape[0] // 84)]

def load_backend(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".engine":
        try:
            return TensorRTBackend(path)
        except Exception as e:
            print(f"[WARN] TensorRT failed: {e}")
            print("[INFO] Falling back to ONNX...")

    return ONNXBackend(path)

def preprocess(img):
    img = img[:, :, ::-1]
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    return np.expand_dims(img, 0)

def postprocess(outputs, conf_thresh):
    preds = outputs[0]

    if preds.ndim != 3:
        print("[WARN] Bad shape:", preds.shape)
        return []

    preds = preds[0].T

    dets = []

    for p in preds:
        scores = p[4:]
        cls = int(np.argmax(scores))
        conf = float(scores[cls])

        if conf < conf_thresh:
            continue

        cx, cy, w, h = p[:4]

        dets.append((
            float(cx - w / 2),
            float(cy - h / 2),
            float(cx + w / 2),
            float(cy + h / 2),
            conf,
            float(cls),
            -1.0
        ))

    return dets

def main():
    print("[inference_runner] Starting...")

    frame_reader = SHMFrameReader()
    det_writer = SHMDetWriter()

    backend = load_backend(MODEL_PATH)

    print("[inference_runner] Warming up...")
    dummy = np.zeros((1, 3, 480, 640), dtype=np.float32)

    for _ in range(5):
        try:
            backend.infer(dummy)
        except Exception:
            pass

    print("[inference_runner] Ready")

    frame_count = 0

    while True:
        frame_id, img = frame_reader.read()

        if img is None:
            time.sleep(0.001)
            continue

        t0 = time.perf_counter()

        try:
            inp = preprocess(img)
            outputs = backend.infer(inp)
            dets = postprocess(outputs, CONF_THRESH)
        except Exception as e:
            print("[ERROR]", e)
            continue

        det_writer.write(dets)

        dt = (time.perf_counter() - t0) * 1000
        frame_count += 1

        if frame_count % LOG_INTERVAL == 0:
            print(f"[frame={frame_id}] dets={len(dets)} {dt:.1f}ms")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[inference_runner] stopped")