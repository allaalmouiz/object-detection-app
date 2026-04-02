"""
app.py — Main Flask application for the Object Detection Web App
Handles routing, file uploads, and rendering results.
Model logic is kept separate in detector.py.
"""

import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from detector import run_detection

# ── App configuration ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "object-detection-secret-key"  # Required for flash messages

# Build the uploads folder path relative to this file so it works in Docker
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# Create the uploads directory automatically if it doesn't already exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

# Only allow standard image formats
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Render the home page with the image upload form."""
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    """
    Accept a POST request with an uploaded image file.
    Run object detection and render result.html with:
      - the path to the annotated output image
      - a list of detection dicts: {"label": str, "confidence": float}
    """
    # ── 1. Validate that a file was included in the request ──────────────────
    if "image" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["image"]

    # An empty filename means the user didn't select a file
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    # ── 2. Validate file type ────────────────────────────────────────────────
    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload a PNG, JPG, or JPEG image.")
        return redirect(url_for("index"))

    try:
        # ── 3. Save the uploaded file securely ──────────────────────────────
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(input_path)

        # ── 4. Run detection via detector.py ────────────────────────────────
        result_filename, detections = run_detection(input_path, filename)

        # Build a URL-friendly path for the result image
        result_image_url = url_for(
            "static", filename=f"uploads/{result_filename}"
        )

        return render_template(
            "result.html",
            result_image=result_image_url,
            detections=detections,
            original_filename=filename,
        )

    except Exception as exc:
        # ── 5. Graceful error handling ───────────────────────────────────────
        return render_template(
            "result.html",
            error=str(exc),
            result_image=None,
            detections=[],
            original_filename=getattr(file, "filename", "unknown"),
        )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Bind to 0.0.0.0 so the app is reachable from outside the Docker container
    app.run(host="0.0.0.0", port=8080, debug=False)
