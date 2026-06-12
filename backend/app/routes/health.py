#!/usr/bin/env python3

# file: backend/app/routes/health.py
# descr: /health rest api endpint



from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


# .route or .get
@health_bp.route("/health")
def health():
    return jsonify(status="ok")
