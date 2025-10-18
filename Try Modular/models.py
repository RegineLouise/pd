# models.py
from datetime import datetime
from extensions import db

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    condition = db.Column(db.String(120), default="Not set")
    severity = db.Column(db.String(50), default="Mild")
    last_visit = db.Column(db.String(50), default="Today")

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(120), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)
    # NEW:
    condition = db.Column(db.String(40), default="Onychomycosis")  # or Healthy
    severity = db.Column(db.String(20), default="Mild")            # Mild/Moderate/Severe/N/A
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed = db.Column(db.Boolean, default=False)
