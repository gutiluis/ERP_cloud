#!/usr/bin/env python3

# file: /backend/app/routes/products.py
# descr: product model rest api routes with flask


from app.models import Product
from flask import Blueprint, render_template




product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/admin/products"
)


# get by default
@product_bp.route("/")
def index_all_products():
    products = db.session.execute(
            db.select(Product).order_by(Product.product_id)).scalars().all()
    return render_template("products/index.html",
                           products=products
    )

@product_bp.route("/new")
def add_product():
    return "ok"
