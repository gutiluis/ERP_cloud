#!/usr/bin/env python3

# file: /backend/app/routes/products.py
# descr: product model rest api routes with flask for admin auth required

from app import db
from app.models import Product, ProductVariant
from flask import (Blueprint, render_template, request, redirect, url_for, flash, abort)
from app.extensions import login_required, Decimal, InvalidOperation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError




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

@product_bp.route("/new", methods=["GET"])
@login_required
def product_form():
    """
    Admin add new product
    """
    return render_template('products/product_form.html')


@product_bp.route("/new", methods=["POST"])
@login_required
def add_product():
    """
    Admin submit new product form. 
    reads from data, includes validation required fields nullable=False
    
    """
    product_required_fields = [
        "product_id", "product_name", "brand",
        "category", "description"
        ]

    variant_required_fields = [
        "price", "stock_quantity", "sku",
        ]
    data = request.form

    product_missing = [
        field for field in product_required_fields 
        if not data.get(
        field, "").strip()
        ]

    variant_missing = [
        field for field in variant_required_fields
        if not data.get(
        field, "").strip()
        ]

    if product_missing:
        abort(400, description=f"Missing Product Fields: {product_missing}")

    if variant_missing:
        abort(400, description=f"Missing Variant Field: {variant_missing}")

    product = Product(
        product_id = data.get(
            "product_id", ""
            ).strip(),
        product_name = data.get(
            "product_name", ""
            ).strip(),
        # nullable=False
        brand = data.get(
            "brand", ""
            ).strip(),
        category = data.get(
            "category", ""
            ).strip(),
        description = data.get(
            "description", ""
            ).strip(),
        url = data.get(
            "url", ""
            ).strip() or None,
        url_tag = data.get(
            "url_tag", ""
            ).strip() or None,
        additional_notes = data.get(
            "additional_notes", ""
            ).strip() or None
    )

    try:
        price = Decimal(data.get("price", "").strip())
        stock_quantity = int(data.get("stock_quantity", "").strip())
    except (InvalidOperation, ValueError):
        abort(400, description="Price must be a valid decimal and stock quantity must be a valid integer")

    variant = ProductVariant(
        product = product,
        price=price,
        stock_quantity=stock_quantity,
        # the object has the relationship under productvariant under product backpopulating variants
        color = data.get(
            "color", ""
            ).strip() or None,
        size = data.get(
            "size", ""
            ).strip() or None,
        sku = data.get(
            "sku", ""
            ).strip(),
        # boolean
        is_external = "is_external" in data,
        external_source = data.get(
            "external_source", ""
            ).strip() or None,
        external_product_id = data.get(
            "external_product_id", ""
            ).strip() or None,
    )
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError: # handle dups
        db.session.rollback()
        flash("PLEASE TRY AGAIN YOU ARE DUPLICATING A VALUE INSIDE THE FORM WHICH ALREADY EXISTS", "error")
        return redirect(url_for("products.index_all_products"))



@product_bp.route("/edit/<string:product_id>", methods=["GET"])
@login_required
def edit_product(product_id):
    """
    Admin get product form from db
    """
    product = Product.query.filter_by(product_id=product_id).one_or_404()
    return render_template("products/editproduct.html", 
                           product=product, variants=product.variants
                           )



@product_bp.route("/edit/<string:product_id>", methods=["POST"])
@login_required
def update_product(product_id):
    """
    Admin edit product form for db
    """
    product_required_fields = [
        "product_name", "brand",
        "category", "description"
        ]

    variant_required_fields = [
        "price", "stock_quantity",
        ]
    data = request.form

    product_missing = [
        field for field in product_required_fields 
        if not data.get(
        field, "").strip()
        ]

    variant_missing = [
        field for field in variant_required_fields
        if not data.get(
        field, "").strip()
        ]

    if product_missing:
        abort(400, description=f"Missing product Fields: {product_missing}")

    if variant_missing:
        abort(400, description=f"Missing variant field: {variant_missing}")

    try:
        product = Product.query.filter_by(product_id=product_id).one_or_404()
        
        variant = ProductVariant.query.filter_by(
                product_id=product.id
        ).first_or_404()

        product.product_name = data.get(
                "product_name", ""
                ).strip()# if im updating a product name is it or None? use or None under nullable=True in the model
        product.brand = data.get(
                "brand", ""
                ).strip()
        product.category = data.get(
                "category", ""
                ).strip()
        product.is_active = "is_active" in data
        product.description = data.get(
                "description", ""
                ).strip()
        product.url = data.get( # nullable=True
                "url", ""
                ).strip() or None
        product.url_tag = data.get(
                "url_tag", ""
                ).strip() or None
        product.additional_notes = data.get(
                "additional_notes", ""
                ).strip() or None

        variant.is_active = "is_active" in data
        variant.color = data.get(
                "color", ""
                ).strip() or None
        variant.size = data.get(
                "size", ""
                ).strip() or None
        variant.price = Decimal(data.get("price") or "0.00")
        variant.stock_quantity = int(data.get("stock_quantity") or 0)
        variant.is_external = "is_external" in data
        variant.external_source = data.get(
                "external_source", ""
                ).strip() or None
        variant.external_product_id = data.get(
                "external_product_id", ""
                ).strip() or None

        db.session.commit()
        return redirect(url_for("products.index_all_products",
                                product_id=product.product_id))
    except IntegrityError as err: # handle dups
        db.session.rollback()
        print(err)
        flash("YOU ARE DUPLICATING A UNIQUE VALUE. PLEASE TRY AGAIN", "error")
        return redirect(url_for("products.product_form"))
    except SQLAlchemyError as err: # generic errors class
        db.session.rollback()
        print(err)
        flash("DATABASE ERROR OCURRED", "error")
        return redirect(url_for("products.product_form"))

@product_bp.route("/<string:product_id>", methods=["GET"])
@login_required
def product_detail(product_id):
    """
    Admin product render product detail form
    """
    product = Product.query.filter_by(product_id=product_id).one_or_404()
    return render_template("products/productdetail.html", product=product)



@product_bp.route("/delete/<string:product_id>")
@login_required
def delete_product(product_id):
    """
    Admin delete product from the db
    """
    product = Product.query.filter_by(product_id=product_id).one_or_404()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("products.index_all_products"))

