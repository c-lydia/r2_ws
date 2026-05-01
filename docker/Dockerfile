FROM nvcr.io/nvidia/l4t-pytorch:r35.4.1-pth2.1-py3

WORKDIR /workspace 

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_common.txt
RUN pip install --no-cache-dir -r requirements_common.txt

COPY requirements_jetson.txt
RUN pip install --no-cache-dir \
    --index-url https://pypi.ngc.nvidia.com \
    onnxruntime-gpu

RUN pip install --no-cache-dir -r requirements_jetson.txt

COPY src/perception/perception/ /workspace/perception/
COPY models/ /workspace/models/

CMD ["python3", "/workspace/perception/inference_runner.py"]