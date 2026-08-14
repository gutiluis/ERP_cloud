# filename: backend/app/__init__.py
# descr: factory orchestrator does not load models. app factory for routes


# enable for api docstring for api documentation with marshmallow
# from flasgger import Swagger
# from flask import Marshmallow
from flask import Flask, render_template

from .config import Config
from .extensions import db, login_manager, migrate


def register_error_handlers(app):
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500


def create_app(config_object=Config):
    """
    Make app
    Export routes apis for admin and cart
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    # add by the end of the app
    #    ma = Marshmallow(app)
    # intialize swagger with the app instance
    #    swagger = Swagger(app)

    register_error_handlers(app)

    from .routes.cart import cart_bp

    app.register_blueprint(cart_bp)

    from .routes.stripe import stripe_bp

    app.register_blueprint(stripe_bp)

    from .auth.routes import auth_bp

    app.register_blueprint(auth_bp)

    from .routes.health import health_bp

    app.register_blueprint(health_bp)

    from .routes.index import index_bp

    app.register_blueprint(index_bp)

    from .routes.customers import customer_bp

    app.register_blueprint(customer_bp)

    from .routes.products import product_bp

    app.register_blueprint(product_bp)

    from .routes.invoices import invoice_bp

    app.register_blueprint(invoice_bp)

    # from . import models

    return app
