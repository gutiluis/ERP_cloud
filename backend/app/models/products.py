# filename: products.py
# descr: static catalog. relationship with orders.py. declarative mapping with annotations

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.cart import CartItem
    from app.models.customers import Customer
    from app.models.orders import OrderItem

from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.mixin import TimeStampModel


class Product(TimeStampModel):
    """
    Related to orderitem model
    """

    __tablename__ = "products"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    product_id: Mapped[str] = mapped_column(
        String(50), index=True, unique=True, nullable=False
    )

    product_name: Mapped[str] = mapped_column(String(200), nullable=False)

    customer_id: Mapped[str] = mapped_column(
        String(50), db.ForeignKey("customers.customer_id"), nullable=False
    )

    customer: Mapped[list[Customer]] = db.relationship(
        "Customer", back_populates="products"
    )

    brand: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    category: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"))

    description: Mapped[str] = mapped_column(Text, nullable=False)
    # under Product not ProductVariant
    order_items: Mapped[list[OrderItem]] = db.relationship(
        "OrderItem", back_populates="product"
    )
    # photolink
    # text cannot be indexed
    # If a column is unique=True or index=True, it must be String(n) in MySQL.
    # 3072 bytes = 768 characters in utf8mb4
    url: Mapped[str] = mapped_column(String(760), unique=True, nullable=True)
    url_tag: Mapped[str] = mapped_column(String(100), nullable=True)

    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    cart_items: Mapped[list[CartItem]] = db.relationship(
        "CartItem", back_populates="product"
    )

    variants = db.relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",  # parent-child ownership
        lazy="selectin",  # avoids n+1 queries when loading products with variants
    )


class ProductVariant(TimeStampModel):
    __tablename__ = "product_variants"
    __table_args__ = (
        db.UniqueConstraint(
            "external_source", "external_product_id", name="uq_external_product"
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    product_id: Mapped[str] = mapped_column(
        String(50), db.ForeignKey("products.product_id"), nullable=False, index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1"),  # db
    )
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        # text('0') is sql expression not Text column types
        nullable=False,
        server_default=text("0"),
    )

    sku: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    stripe_price_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    # stripe is an external integration, not source of truth of db. db owns the product not stripe. even though all payemnts are in credit card
    stripe_product_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )

    is_external: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0")
    )

    external_source: Mapped[str | None] = mapped_column(String(200), nullable=True)

    external_product_id: Mapped[str | None] = mapped_column(String(200), nullable=True)

    product: Mapped[Product] = db.relationship(
        "Product",
        back_populates="variants",
    )

    order_items: Mapped[list[OrderItem]] = db.relationship(
        "OrderItem", back_populates="product_variant"
    )

    @property
    def is_in_stock(self) -> bool:
        return self.is_active and self.stock_quantity > 0
