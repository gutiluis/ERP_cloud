#!/usr/bin/env python3

# file: /backend/app/routes/products.py
# descr: product model rest api routes with flask

from flask import Blueprint


product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/admin/products"
)

@product_bp.route("/")
def index_all_products():
    pass

@product_bp.route("/")
def product_detail():
    product = Product.query.all_or_get_404()
    return product