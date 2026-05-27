# Troubleshooting — Target Setter (v2.0)

This page consolidates testing steps, common runtime warnings, troubleshooting commands, and known issues.

## Testing Notes

### Camera Testing

``` bash
# Check camera is publishing
ros2 topic list | grep image
ros2 topic hz /image_raw  # Should be ~30 Hz

# View camera feed
ros2 run image_view image_view_node --ros-args --remap image:=/image_raw
```

### Inference Warnings (Non-Fatal)

The following startup warnings are expected with the base YOLO model and can be ignored unless you need those optional models:

``` text
ModelDependencyMissing: Your `inference` configuration does not support SAM model.
ModelDependencyMissing: Your `inference` configuration does not support SAM3 model.
ModelDependencyMissing: Your `inference` configuration does not support Gaze Detection model.
ModelDependencyMissing: Your `inference` configuration does not support YoloWorld model.
DeprecationWarning: DepthProImageProcessorFast is deprecated.
FutureWarning: Importing from timm.models.layers is deprecated.
```

To enable optional backends:

``` bash
pip install 'inference[sam]'
pip install 'inference[gaze]'
pip install 'inference[yolo-world]'
```

Then set environment flags, e.g. `export CORE_MODEL_SAM_ENABLED=True`.

## Common Troubleshooting

### Robot does not move after sending waypoints

- Ensure UDP listener is running and receiving packets.
- Verify `/waypoint` is published: `ros2 topic echo /waypoint`.
- Check `/current_odom` is published by driver node.

### Robot moves in wrong direction

- Confirm odometry frame matches the app's global frame.
- Ensure initial pose matches app origin (0,0) or transform appropriately.

### Yaw incorrect

- Verify quaternion-to-yaw conversion and IMU consistency.

### Oscillation / Overshoot

- Reduce `K_P` in `robot_control.py` or adjust `A_MAX` ramp.

### Robot stops short

- Lower `ERROR_THRESHOLD` or `ARRIVAL_THRESHOLD` in control parameters.

### Paused state never resumes

- Check for external `_pause_robot` flags and ensure odometry topic is alive.

### `custom_messages` not found at build

- Ensure `custom_messages` (or `robot_interface`) package is present in workspace and run `colcon build`.

### Node aborts / Undefined symbol

- Usually a library/version mismatch — reinstall pinned versions: `pip install nvidia-cudnn-cu12==9.1.0.70`.

### High CPU temperature (80°C+)

- System likely fell back to CPU inference. Ensure perception uses CUDAExecutionProvider.

### Vision false positives

- Tighten HSV thresholds and reduce morphological kernel size (try `5x5`).

### CUDA / GPU errors

If you see `libcufft.so.11: cannot open shared object file` or `Failed to create CUDAExecutionProvider`:

- Install CUDA Toolkit 12.*: `sudo apt-get install cuda-toolkit-12-1`.
- Install cuDNN runtime: `pip install nvidia-cudnn-cu12==9.1.0.70`.
- Export GPU library path:

``` bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/.cv_env/lib/python3.10/site-packages/nvidia/cudnn/lib
```

- Fall back to CPU: `export FORCE_CPU=1`.

### Camera driver issues (usb_cam)

- Verify device: `ls -la /dev/video*`.
- Check recognition: `v4l2-ctl --list-devices`.
- Add user to `video` group: `sudo usermod -a -G video $USER` and re-login.
- Test with ffmpeg: `ffmpeg -f v4l2 -i /dev/video0 -frames 1 test.jpg`.

### Inference engine checks

- Confirm `MODEL_PATH`:

``` bash
echo $MODEL_PATH
ls -la $MODEL_PATH
```

- If TensorRT fails, ONNX Runtime fallback should still work (slower).
- Check output: `ros2 topic echo /detections | head -n 20`.

## Known Issues

- **Yaw error** — heading is off.
- **Residual position error** — steady-state P-controller error near the target.
- **Waypoint edit bug** — app-side bug; restart app and re-send as workaround.
- **No emergency stop on app** — implement `ESTOP` in app to send `/estop`.
- **Stale detections** — If inference lags >50ms, detections are dropped; tune `STALENESS_MS` in `shm_bridge.py`.
