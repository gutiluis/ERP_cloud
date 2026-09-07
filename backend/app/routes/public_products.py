# file: /public_products.py
# descr: public product api route


from app.models import Product
from app import db
from flask import Blueprint, jsonify


public_product_bp = Blueprint(
    "public_products",
    __name__,
    url_prefix="/api/products",
)


@public_product_bp.route("", methods=["GET"])
def public_products():
    """
    Public Product frontend route
    """
    products = (
        db.session.execute(
            db.select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.product_id)
        )
        .scalars()
        .all()
    )

    return jsonify(
        {
            "products": [
                {
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "brand": product.brand,
                    "category": product.category,
                    "description": product.description,
                    "url": product.url,
                    "url_tag": product.url_tag,
                    "variants": [
                        {
                            "price": str(variant.price),
                            "stock_quantity": variant.stock_quantity,
                            "color": variant.color,
                            "size": variant.size,
                            "sku": variant.sku,
                            "is_in_stock": variant.is_in_stock,
                        }
                        for variant in product.variants
                        if variant.is_active
                    ],
                }
                for product in products
            ]
        }
    )
