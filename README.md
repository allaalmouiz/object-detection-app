# 🔍 Object Detection Web App

A modern, AI-powered web application for real-time object detection — built with **Flask** and **YOLOv8**, deployable via **Docker**.

Upload any image and the app will identify objects, draw bounding boxes, and return confidence scores — all in a sleek dark-mode UI.

## APP Demo 
![App Demo](assets/App.gif)

---

## ✨ Features

- 🎯 **YOLOv8 inference** using custom-trained weights (`best.pt`)
- 🖼️ **Drag & drop** image upload with live preview
- 📊 **Detection results table** with confidence percentages and bars
- 🐳 **Docker-ready** with CPU-only PyTorch (lightweight image)
- 📱 **Responsive design** — works on desktop and mobile

---

## 📁 Project Structure

```
object-detection-app/
├── app.py              # Flask routes & upload logic
├── detector.py         # YOLOv8 model loading & inference
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition (CPU-only PyTorch)
├── model/
│   └── best.pt         # ← Your trained model weights (add separately)
├── static/
│   ├── css/style.css   # Dark-mode design system
│   ├── js/main.js      # Drag-drop, preview, loading spinner
│   └── uploads/        # Temporary image storage (auto-created)
└── templates/
    ├── index.html      # Upload page
    └── result.html     # Detection results page
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Your trained `best.pt` YOLOv8 weights file

### 1. Add your model weights

```bash
cp /path/to/your/best.pt model/best.pt
```

### 2. Run locally (without Docker)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install flask ultralytics Pillow opencv-python-headless

# Start the server
python app.py
```

Open **http://localhost:8080** in your browser.

### 3. Run with Docker

```bash
# Build the image
docker build -t object-detection-app .

# Run the container (mount your weights if not copied in)
docker run -p 5000:5000 -v $(pwd)/model:/app/model object-detection-app
```

Open **http://localhost:5000** in your browser.

---

## 🧪 How It Works

1. User uploads an image via the web UI
2. Flask saves it to `static/uploads/`
3. `detector.py` loads the YOLOv8 model and runs inference
4. The annotated result image is saved and displayed
5. Detected labels + confidence scores are shown in a table

---

## ⚙️ Configuration

| Setting | Default | Description |
|---|---|---|
| `MAX_CONTENT_LENGTH` | 16 MB | Max upload file size |
| Allowed extensions | png, jpg, jpeg | Accepted image formats |
| Confidence threshold | 0.25 | Min score for a detection to show |
| Port (local) | 8080 | Change in `app.py` |
| Port (Docker) | 5000 | Exposed in `Dockerfile` |

---

## 📦 Tech Stack

- **Backend**: Flask (Python)
- **Model**: Ultralytics YOLOv8
- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Container**: Docker with Python 3.10-slim base

---

## 📝 Notes

- The model file (`model/best.pt`) is excluded from git via `.gitignore` — add it manually before running.
- For production, replace Flask's dev server with **Gunicorn**: `gunicorn -w 2 -b 0.0.0.0:5000 app:app`
