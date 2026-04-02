"""
detector.py — Model loading and inference logic for the Object Detection app.
Kept separate from app.py to maintain a clean separation of concerns.
Uses Ultralytics YOLOv8 to run inference on uploaded images.
"""

import os
from ultralytics import YOLO

# ── Model loading ──────────────────────────────────────────────────────────────
# Build the model path relative to this file so it works correctly inside Docker
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

# Load the model once at module import time to avoid reloading on every request
# This variable is shared across all requests handled by the Flask process
_model = None


def get_model() -> YOLO:
    """
    Lazily load and cache the YOLOv8 model.
    Returns the loaded YOLO model instance.
    Raises FileNotFoundError if the weights file is missing.
    """
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model weights not found at '{MODEL_PATH}'. "
                "Please place your best.pt file in the model/ directory."
            )
        # Load the YOLOv8 model from the provided weights file
        _model = YOLO(MODEL_PATH)
    return _model


def run_detection(image_path: str, original_filename: str):
    """
    Run YOLOv8 inference on the given image and save the annotated result.

    Args:
        image_path (str): Absolute path to the uploaded input image.
        original_filename (str): The original filename (used to name the output).

    Returns:
        tuple:
            result_filename (str): Filename of the annotated output image
                                   (saved to the same uploads/ directory).
            detections (list[dict]): A list of detection results, each a dict:
                                     {"label": str, "confidence": float}
    """
    # ── 1. Load the model ────────────────────────────────────────────────────
    model = get_model()

    # ── 2. Run inference ─────────────────────────────────────────────────────
    # conf=0.25 is the default confidence threshold; set verbose=False for clean logs
    results = model(image_path, conf=0.25, verbose=False)

    # ── 3. Build the output image filename and path ──────────────────────────
    result_filename = f"result_{original_filename}"
    uploads_dir = os.path.dirname(image_path)
    result_path = os.path.join(uploads_dir, result_filename)

    # ── 4. Save the annotated (plotted) result image ─────────────────────────
    # results[0].plot() returns a BGR numpy array with bounding boxes drawn
    if results and len(results) > 0:
        import cv2
        annotated_frame = results[0].plot()
        cv2.imwrite(result_path, annotated_frame)
    else:
        # If inference returned nothing, copy the original image as the result
        import shutil
        shutil.copy(image_path, result_path)

    # ── 5. Extract detection labels and confidence scores ────────────────────
    detections = []

    if results and len(results) > 0:
        result = results[0]

        # result.boxes contains all detected bounding boxes
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                # cls is a tensor with the class index; names maps index → label
                class_index = int(box.cls[0].item())
                label = model.names.get(class_index, f"Class {class_index}")
                confidence = float(box.conf[0].item())

                detections.append({
                    "label": label,
                    "confidence": round(confidence * 100, 2),  # As percentage
                })

            # Sort by confidence descending so the most confident result is first
            detections.sort(key=lambda d: d["confidence"], reverse=True)

    # Return both the result filename and the list of detection dicts
    return result_filename, detections
