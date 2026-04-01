# ── Base image ────────────────────────────────────────────────────
FROM python:3.10-slim

# ── System dependencies (OpenCV headless needs libGL) ─────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies first (leverages Docker cache) ────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────────────────────────
COPY . .

# ── Ensure model directory exists ────────────────────────────────
RUN mkdir -p models

# ── Expose port ──────────────────────────────────────────────────
EXPOSE 5000

# ── Environment defaults ──────────────────────────────────────────
ENV MODEL_PATH=models/best.pt \
    PYTHONUNBUFFERED=1

# ── Launch Flask via Gunicorn (production-grade WSGI) ─────────────
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
