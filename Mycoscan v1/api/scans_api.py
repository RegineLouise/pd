# api/scans_api.py
import os
import io
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import Scan
from extensions import db

# Optional ML helpers (import at runtime via package)
try:
    from Models.visualizer import draw_segmentation, draw_grid
    from Models.osi_score import compute_osi
except Exception:
    draw_segmentation = None
    draw_grid = None
    compute_osi = None

import cv2
import numpy as np

bp = Blueprint("scans_api", __name__)

def _image_url(filename):
    if not filename:
        return None
    return f"/static/uploads/scans/{filename}"

@bp.route("/api/scans", methods=["GET"])
def list_scans():
    # newest first
    scans = Scan.query.order_by(Scan.created_at.desc()).all()
    return jsonify([
        {
            "id": s.id,
            "patient_name": s.patient_name,
            "notes": s.notes,
            "condition": s.condition,
            "severity": s.severity,
            "created_at": s.created_at.isoformat(),
            "image_url": _image_url(s.image_filename),
            "analyzed": s.analyzed,
        }
        for s in scans
    ])

@bp.route("/api/scans", methods=["POST"])
def save_scan():
    # Accepts multipart/form-data
    patient_name = request.form.get("patient_name")
    notes = request.form.get("notes")
    condition = request.form.get("condition") or "Onychomycosis"
    severity = request.form.get("severity") or ("N/A" if condition == "Healthy" else "Mild")
    image = request.files.get("image")

    # Debug information
    print(f"DEBUG SCAN API: patient_name='{patient_name}', image={image is not None}")
    print(f"DEBUG SCAN API: form data keys: {list(request.form.keys())}")
    print(f"DEBUG SCAN API: files keys: {list(request.files.keys())}")

    if not patient_name or not image:
        error_msg = "Missing patient name or image"
        if not patient_name:
            error_msg += " (patient_name is missing)"
        if not image:
            error_msg += " (image is missing)"
        print(f"DEBUG SCAN API: Error - {error_msg}")
        return jsonify({"error": error_msg}), 400

    filename = secure_filename(image.filename)
    upload_dir = os.path.join(current_app.static_folder, "uploads", "scans")
    os.makedirs(upload_dir, exist_ok=True)
    image.save(os.path.join(upload_dir, filename))

    new_scan = Scan(
        patient_name=patient_name,
        notes=notes,
        image_filename=filename,
        condition=condition,
        severity=severity,
        analyzed=True,
        created_at=datetime.utcnow(),
    )
    db.session.add(new_scan)
    db.session.commit()

    return jsonify({
        "id": new_scan.id,
        "patient_name": new_scan.patient_name,
        "notes": new_scan.notes,
        "condition": new_scan.condition,
        "severity": new_scan.severity,
        "created_at": new_scan.created_at.isoformat(),
        "image_url": _image_url(new_scan.image_filename),
        "message": f"Scan saved for {patient_name}"
    }), 201


@bp.route("/api/predict", methods=["POST"])
def predict():
    # Accepts multipart/form-data with an 'image' file
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    if not image or image.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Validate extension
    allowed = {'png', 'jpg', 'jpeg'}
    if '.' not in image.filename or image.filename.rsplit('.', 1)[1].lower() not in allowed:
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(image.filename)
    upload_dir = os.path.join(current_app.static_folder, "uploads", "scans")
    os.makedirs(upload_dir, exist_ok=True)

    # Save original upload
    file_path = os.path.join(upload_dir, filename)
    image.save(file_path)

    # Read image into OpenCV (BGR)
    try:
        file_bytes = open(file_path, 'rb').read()
        npimg = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
    except Exception as e:
        return jsonify({"error": f"Could not read uploaded image: {e}"}), 400

    # Ensure model is available
    model = getattr(current_app, 'yolo_model', None)
    if not getattr(current_app, 'yolo_ready', False) or model is None:
        return jsonify({"error": "YOLO model not available on server"}), 500

    try:
        # Run segmentation
        nail_mask, fungi_mask, bbox = model.segment(img)

        # Compute OSI if available
        osi = None
        severity = None
        bbox_out = None
        if compute_osi is not None:
            osi, severity, bbox_out = compute_osi(nail_mask, fungi_mask)

        # Visualization
        vis_img = img.copy()
        if draw_segmentation is not None:
            vis_img = draw_segmentation(vis_img, nail_mask, fungi_mask)
        if bbox is not None and draw_grid is not None:
            vis_img = draw_grid(vis_img, bbox)

        # Encode vis to base64 for JSON transport
        success, encoded = cv2.imencode('.jpg', vis_img)
        if not success:
            raise ValueError("Failed to encode processed image")

        b64 = base64.b64encode(encoded.tobytes()).decode('utf-8')

        # Optionally save processed image
        proc_name = f"pred_{filename}"
        proc_path = os.path.join(upload_dir, proc_name)
        with open(proc_path, 'wb') as f:
            f.write(encoded.tobytes())

        return jsonify({
            "filename": filename,
            "processed_filename": proc_name,
            "osi": osi,
            "severity": severity,
            "bbox": bbox or bbox_out,
            "image_b64": b64,
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500
