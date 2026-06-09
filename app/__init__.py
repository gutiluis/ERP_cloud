#!/usr/bin/env python3
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

    return app
