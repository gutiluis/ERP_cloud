#!/usr/bin/env python3

# filename: backend/app/__init__.py
# descr: orchestrator does not load models

from flask import Flask
from .config import Config
from .extensions import db, migrate

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    from .routes.index import index_bp
    app.register_blueprint(index_bp)

    from . import models

    return app
