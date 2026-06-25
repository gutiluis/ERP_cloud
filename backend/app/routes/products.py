#!/usr/bin/env python3

# file: /backend/app/routes/products.py
# descr: product model rest api routes with flask for admin auth required

from app import db
from app.models import Product, ProductVariant
from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import login_required, Decimal, InvalidOperation




product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/admin/products"
)

# [ x ] ready http. missing frontend
@product_bp.route("/")
@login_required
def index_all_products():
    """Admin view Index all products"""
    products = db.session.execute(
            db.select(Product).order_by(Product.product_id)).scalars().all()
    return render_template("products/index.html",
                           products=products
    )

# [ x ] render product_variant.html and product_form.html
# [ x ] render product_form
@product_bp.route("/new", methods=["GET"])
@login_required
def product_form():
    """
    Admin add new product
    """
    return render_template('products/product_form.html')















# [  ] submit form to db 
@product_bp.route("/new", methods=["POST"])
@login_required
def add_product():
    """
    Admin submit new product form
    """
    product = Product(
        product_id = request.form.get("product_id", "").strip(),
        product_name = request.form.get("product_name", "").strip(),
        brand = request.form.get("brand", "").strip(),
        category = request.form.get("category", "").strip(),
        description = request.form.get("description", "").strip(),
        url = request.form.get("url", "").strip(),
        url_tag = request.form.get("url_tag", "").strip(),
        additional_notes = request.form.get("additional_notes", "").strip()
    )
    price_str = request.form.get("price", "").strip()
    if not price_str:
        raise ValueError("[INFO] Price field required")

    variant = ProductVariant(
        product = product,
        price=Decimal(price_str),
        # the object has the relationship under productvariant under product backpopulating variants
        color = request.form.get("color", "").strip(),
        size = request.form.get("size", "").strip(),
        stock_quantity = request.form.get("stock_quantity", "").strip(),
        sku = request.form.get("sku", "").strip(),
        # boolean
        is_external = "is_external" in request.form,
        external_source = request.form.get("external_source", "").strip(),
        external_product_id = request.form.get("external_product_id", "").strip(),
    )
    product.variants.append(variant)
    db.session.add(product)
    db.session.commit()
    return redirect(url_for("products.index_all_products"))
































@product_bp.route("/edit/<string:product_id>", methods=["GET"])
@login_required
def edit_product(product_id):
    """
    Admin get product form from db
    """
    product = Product.query.filter_by(product_id=product_id).one_or_404()
    return render_template("products/editproduct.html", product=product, variants=product.variants)



@product_bp.route("/edit/<string:product_id>", methods=["POST"])
@login_required
def update_product(product_id):
    """
    Admin edit product form for db
    """
    try:
        product = Product.query.filter_by(product_id=product_id).one_or_404()
        
        variant = ProductVariant.query.filter_by(
                product_id=product.id
        ).first_or_404()

        product.product_name = request.form.get("product_name", "").strip()
        product.brand = request.form.get("brand", "").strip()
        product.category = request.form.get("category", "").strip()
        product.is_active = "is_active" in request.form
        product.description = request.form.get("description", "").strip()
        product.url = request.form.get("url", "").strip()
        product.url_tag = request.form.get("url_tag", "").strip()
        product.additional_notes = request.form.get("additional_notes", "").strip()

        variant.is_active = "is_active" in request.form
        variant.color = request.form.get("color", "").strip()
        variant.size = request.form.get("size", "").strip()
        variant.price = Decimal(request.form.get("price") or "0.00")
        variant.stock_quantity = int(request.form.get("stock_quantity") or 0)
        variant.sku = request.form.get("sku", "").strip()
        variant.is_external = "is_external" in request.form
        variant.external_source = request.form.get("external_source", "").strip()
        variant.external_product_id = request.form.get("external_product_id", "").strip()

        db.session.commit()
        return redirect(url_for("products.index_all_products",
                                product_id=product.product_id))
    except Exception as err:
        print(err)
        db.session.rollback()
        return redirect(url_for("products.product_form"))





@product_bp.route("/<string:product_id>", methods=["GET"])
@login_required
def product_detail(product_id):
    """
    Admin product render product detail form
    """
    product = Product.query.filter_by(product_id=product_id).one_or_404()
    return render_template("products/productdetail.html", product=product)



@product_bp.route("/<string:product_id>/delete")
@login_required
def delete_product(product_id):
    """
    Admin delete product from the db
    """
    product = Product.query.filter_by(product_id=product_id).one_or_404()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("products.index_all_products"))

