# main.py
import os
from pathlib import Path

from flask import Flask
from jinja2 import DictLoader, ChoiceLoader
from dotenv import load_dotenv

# DB
from extensions import db

# Models (so db.create_all() can see them)
import models  # noqa: F401

# --- Pages (blueprints + in-memory templates) ---
from pages.base_tpl import TEMPLATES as BASE_TPL

from pages.landing import bp as landing_page_bp, TEMPLATES as LANDING_TPL
from pages.dashboard import bp as dashboard_page_bp, TEMPLATES as DASHBOARD_TPL
from pages.patients import bp as patients_page_bp, TEMPLATES as PATIENTS_TPL
from pages.medications import bp as medications_page_bp, TEMPLATES as MEDICATIONS_TPL
from pages.scan import bp as scan_page_bp, TEMPLATES as SCAN_TPL
from pages.aboutus import bp as aboutus_page_bp, TEMPLATES as ABOUT_TPL
from pages.reports import bp as reports_page_bp, TEMPLATES as REPORTS_TPL

# --- APIs (blueprints) ---
from api.patients_api import bp as patients_api_bp
from api.medications_api import bp as medications_api_bp
from api.scans_api import bp as scans_api_bp


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, static_folder="static")

    # ---------- Config ----------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///mycoscan.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Where uploaded scans are stored
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads", "scans")
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # ---------- DB ----------
    db.init_app(app)

    # ---------- Jinja templates (in-memory) ----------
    # Merge all TEMPLATES dicts from page modules
    templates = {}
    templates.update(BASE_TPL)
    templates.update(LANDING_TPL)
    templates.update(DASHBOARD_TPL)
    templates.update(PATIENTS_TPL)
    templates.update(MEDICATIONS_TPL)
    templates.update(SCAN_TPL)
    templates.update(ABOUT_TPL)
    templates.update(REPORTS_TPL)

    # Prepend our DictLoader so these names resolve first
    app.jinja_loader = ChoiceLoader([DictLoader(templates), app.jinja_loader])

    # ---------- Register blueprints ----------
    # Pages
    app.register_blueprint(landing_page_bp)
    app.register_blueprint(dashboard_page_bp)
    app.register_blueprint(patients_page_bp)
    app.register_blueprint(medications_page_bp)
    app.register_blueprint(scan_page_bp)
    app.register_blueprint(aboutus_page_bp)
    app.register_blueprint(reports_page_bp)

    # APIs
    app.register_blueprint(patients_api_bp)
    app.register_blueprint(medications_api_bp)
    app.register_blueprint(scans_api_bp)

    # ---------- Create tables ----------
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    # Use PORT from env if provided
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)