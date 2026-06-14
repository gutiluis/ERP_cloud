#!/usr/bin/env python3

# filename: backend/app/__init__.py
# descr: orchestrator does not load models

from flask import Flask, render_template
from .config import Config
from .extensions import db, migrate

def register_error_handlers(app):
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500




def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    register_error_handlers(app)

    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    from .routes.index import index_bp
    app.register_blueprint(index_bp)
    
    from .routes.customers import customer_bp
    app.register_blueprint(customer_bp)

    from . import models
    
    
    return app

