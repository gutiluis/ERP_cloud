# file: /app/models/cart.py
# descr: preorder cart to be used in the stripe checkout function
from __future__ import annotations

from typing import TYPE_CHECKING  # allow Mapped["annotation"], Mapped[list[Product]]

if TYPE_CHECKING:
    from app.models.products import Product, ProductVariant
    from app.models.customer import Customer
    from app.models.orders import Order

import enum
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import (
    db,
)
from app.models.mixin import TimeStampModel


class CartStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CONVERTED = "converted"


class Cart(TimeStampModel):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # react can store it in a cookie or local storage and send it with api requests
    # instead of user_id for no login of user and /stripe/checkout
    cart_token: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )

    status: Mapped[CartStatus] = mapped_column(
        db.Enum(CartStatus, native_enum=False, validate_string=True),
        nullable=False,
        default=CartStatus.PENDING,
        server_default=CartStatus.PENDING.value,
        index=True,
    )
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )
    customer: Mapped[Customer] = db.relationship(
        "Customer",
        back_populates="carts",
    )
    order: Mapped[Order] = db.relationship(
        "Order",
        back_populates="cart",
        uselist=False,
    )
    items: Mapped[list[CartItem]] = db.relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )
    # for stripe checkout session buyer does not need login
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class CartItem(TimeStampModel):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(
        db.ForeignKey("carts.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey("products.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cart: Mapped[Cart] = db.relationship("Cart", back_populates="items")
    product: Mapped[Product] = db.relationship("Product", back_populates="cart_items")
    product_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey("product_variants.id"),
        nullable=False,
        index=True,
    )
    product_variant: Mapped[ProductVariant] = db.relationship(
        "ProductVariant",
        back_populates="cart_items",
    )
