from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

# ---------------------------------------------------------
#  Load environment variables
# ---------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Folder for uploaded scans
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'scans')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ---------------------------------------------------------
#  DATABASE MODELS
# ---------------------------------------------------------
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
    analyzed = db.Column(db.Boolean, default=False)

# ---------------------------------------------------------
#  ROUTES — WEB PAGES
# ---------------------------------------------------------
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/patients')
def patients():
    patient_records = Patient.query.all()
    return render_template('patients.html', patient_records=patient_records)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/scan')
def scan():
    # Only show patients that exist in DB for dropdown
    patients = [p.name for p in Patient.query.all()]
    return render_template('scan.html', patients=patients)

@app.route('/medications')
def medications():
    return render_template('medications.html')

# ---------------------------------------------------------
#  API ROUTES — PATIENTS
# ---------------------------------------------------------
@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "sex": p.sex,
            "condition": p.condition,
            "severity": p.severity,
            "last_visit": p.last_visit
        }
        for p in patients
    ])

@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    new_patient = Patient(
        name=data['name'],
        age=data['age'],
        sex=data['sex'],
        last_visit="Today",
        condition="Not set",
        severity="Mild"
    )
    db.session.add(new_patient)
    db.session.commit()

    # Return full new record instead of just a message
    return jsonify({
        "id": new_patient.id,
        "name": new_patient.name,
        "age": new_patient.age,
        "sex": new_patient.sex,
        "condition": new_patient.condition,
        "severity": new_patient.severity,
        "last_visit": new_patient.last_visit
    })

@app.route('/api/patients/<int:id>', methods=['PUT'])
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    data = request.get_json()

    patient.last_visit = data.get('last_visit', patient.last_visit)
    patient.condition = data.get('condition', patient.condition)
    patient.severity = data.get('severity', patient.severity)
    db.session.commit()

    # Return updated patient info
    return jsonify({
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "sex": patient.sex,
        "condition": patient.condition,
        "severity": patient.severity,
        "last_visit": patient.last_visit
    })

# ✅ Added DELETE route for patients
@app.route('/api/patients/<int:id>', methods=['DELETE'])
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted successfully"})

# ---------------------------------------------------------
#  API ROUTES — MEDICATIONS
# ---------------------------------------------------------
@app.route('/api/medications', methods=['GET'])
def get_medications():
    meds = Medication.query.all()
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "type": m.type,
            "stock": m.stock,
            "image_url": f"/static/uploads/scans/{m.image_filename}" if m.image_filename else None
        }
        for m in meds
    ])

@app.route('/api/medications', methods=['POST'])
def add_medication():
    data = request.get_json()
    new_med = Medication(
        name=data['name'],
        type=data['type'],
        stock=data['stock']
    )
    db.session.add(new_med)
    db.session.commit()
    return jsonify({
        "id": new_med.id,
        "name": new_med.name,
        "type": new_med.type,
        "stock": new_med.stock,
        "image_url": None
    })

@app.route('/api/medications/<int:id>', methods=['PUT'])
def update_medication(id):
    med = Medication.query.get_or_404(id)
    data = request.get_json()
    med.name = data['name']
    med.type = data['type']
    med.stock = data['stock']
    db.session.commit()
    return jsonify({
        "id": med.id,
        "name": med.name,
        "type": med.type,
        "stock": med.stock
    })

# ✅ Added DELETE route for medications
@app.route('/api/medications/<int:id>', methods=['DELETE'])
def delete_medication(id):
    med = Medication.query.get_or_404(id)
    db.session.delete(med)
    db.session.commit()
    return jsonify({"message": "Medication deleted successfully"})

@app.route('/api/medications/<int:med_id>/image', methods=['POST'])
def upload_medication_image(med_id):
    med = Medication.query.get_or_404(med_id)
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image provided'}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    try:
        file.save(upload_path)
        med.image_filename = filename
        db.session.commit()
        return jsonify({'message': 'Image uploaded successfully'})
    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
#  API ROUTE — SCANS
# ---------------------------------------------------------
@app.route('/api/scans', methods=['POST'])
def save_scan():
    patient_name = request.form.get('patient_name')
    notes = request.form.get('notes')
    image = request.files.get('image')

    if not patient_name or not image:
        return jsonify({'error': 'Missing patient name or image'}), 400

    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    new_scan = Scan(
        patient_name=patient_name,
        notes=notes,
        image_filename=filename,
        analyzed=False
    )
    db.session.add(new_scan)
    db.session.commit()

    return jsonify({'message': f'Scan saved for {patient_name}', 'image_url': f'/static/uploads/scans/{filename}'})

# ---------------------------------------------------------
#  INITIALIZE DATABASE & RUN APP
# ---------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
