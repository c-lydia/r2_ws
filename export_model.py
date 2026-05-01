"""
Export Roboflow model to ONNX format.

Usage:
    python3 export_model.py
"""

import os
import subprocess
import sys

API_KEY = "G5APCSh23WuiAtf16uUD"
MODEL_ID = "project-mamra-king/2"
OUTPUT_DIR = "models"
FORMAT = "onnx"

def check_python_module(module_name):
    """Ensure required module is installed."""
    try:
        __import__(module_name)
    except ImportError:
        print(f"[ERROR] Missing module: {module_name}")
        print("Install it with:")
        print("    pip install inference-sdk")
        sys.exit(1)

def ensure_output_dir(path):
    """Create output directory if it doesn't exist."""
    if not os.path.exists(path):
        print(f"[INFO] Creating directory: {path}")
        os.makedirs(path, exist_ok=True)

def export_model():
    """Run Roboflow export via CLI."""
    cmd = [
        sys.executable, "-m", "inference", "export",
        "--model_id", MODEL_ID,
        "--api_key", API_KEY,
        "--format", FORMAT,
        "--output", OUTPUT_DIR
    ]

    print("[INFO] Exporting model to ONNX...")
    print(f"[INFO] Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("[ERROR] Export failed")
        sys.exit(e.returncode)

    print("[INFO] Export completed successfully")

def verify_output():
    """Check if ONNX file exists."""
    files = os.listdir(OUTPUT_DIR)
    onnx_files = [f for f in files if f.endswith(".onnx")]

    if not onnx_files:
        print("[ERROR] No ONNX file found in models/")
        sys.exit(1)

    print("[INFO] Exported ONNX model(s):")
    for f in onnx_files:
        path = os.path.join(OUTPUT_DIR, f)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  - {f} ({size_mb:.2f} MB)")

    print("\n[OK] Model export verified")

def main():
    print("=== Roboflow → ONNX Export ===")

    check_python_module("inference_sdk")
    ensure_output_dir(OUTPUT_DIR)

    export_model()
    verify_output()

if __name__ == "__main__":
    main()