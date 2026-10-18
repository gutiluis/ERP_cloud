# filename: backend/app/__init__.py
# descr: factory orchestrator does not load models. app factory for routes


from flask import Flask
from app.config import config
from .extensions import db, login_manager, migrate
from .api.errors import register_error_handlers


def create_app(config_object):
    """
    Make app
    Export routes apis for admin, public frontend and cart
    """
    app = Flask(__name__)
    app.config.from_object(config[config_object])

    config[config_object].init_app(app)
    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)

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

    from .routes.public_products import public_product_bp

    app.register_blueprint(public_product_bp)

    from .routes.invoices import invoice_bp

    app.register_blueprint(invoice_bp)

    from .routes.checkout import checkout_bp

    app.register_blueprint(checkout_bp)

    from .routes.orders import orders_bp

    app.register_blueprint(orders_bp)

    return app
