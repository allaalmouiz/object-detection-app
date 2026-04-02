# ── Base image ─────────────────────────────────────────────────────────────────
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# ── Install system-level dependencies needed by OpenCV ─────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ─────────────────────────────────────────────────
COPY requirements.txt .

# Step 1: Install CPU-only PyTorch and TorchVision from the official CPU wheel index.
# This avoids pulling in the much larger CUDA-enabled builds and keeps the image leaner.
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Step 2: Install the remaining Python packages (Flask, Ultralytics, Pillow, OpenCV)
RUN pip install --no-cache-dir flask ultralytics Pillow opencv-python-headless

# ── Copy application source code ────────────────────────────────────────────────
# NOTE: The model weights file (model/best.pt) is NOT copied here intentionally.
# You should either:
#   a) Mount it at runtime:  docker run -v /your/local/model:/app/model ...
#   b) Copy it manually before building: COPY model/best.pt model/best.pt
# This keeps the Docker image generic and shareable without embedding large weights.
COPY . .

# ── Create the uploads directory (in case it was not committed) ─────────────────
RUN mkdir -p static/uploads

# ── Expose the Flask port ───────────────────────────────────────────────────────
EXPOSE 5000

# ── Start the Flask application ─────────────────────────────────────────────────
CMD ["python", "app.py"]
