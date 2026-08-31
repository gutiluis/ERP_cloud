# filename: /backend/app/models/orders.py
# descr: relationship with product, user, invoice. The cart model has an order
# declarative maping with annotations
# do not import model where foreignkey is back_populating to prevent circular import
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.customers import Customer
    from app.models.invoice import Invoice
    from app.models.products import Product, ProductVariant
    from app.models.cart import Cart

import enum
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.mixin import TimeStampModel


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(TimeStampModel):
    __tablename__ = "orders"
    "table arguments is a class attribute"
    "This attribute accommodates both positional as well as keyword arguments that are normally sent to the Table constructor. "
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    stripe_session_id: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False
    )
    # idempotency stripe webhook help to avoid double payments
    stripe_payment_intent_id: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=True
    )

    status: Mapped[OrderStatus] = mapped_column(
        db.Enum(OrderStatus, native_enum=False, validate_strings=True),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default="pending",
        index=True,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # admin does not create orders
    operator_admin_id: Mapped[int] = mapped_column(
        BigInteger, db.ForeignKey("adminUsers.id"), nullable=False
    )

    customer_id: Mapped[int] = mapped_column(
        BigInteger, db.ForeignKey("customers.id"), nullable=False
    )

    customer: Mapped[Customer] = db.relationship("Customer", back_populates="orders")

    items: Mapped[list[OrderItem]] = db.relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    shipping_address_1: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False
    )

    shipping_address_2: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=True
    )
    shipping_country: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    shipping_city: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    shipping_zip_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    shipping_state: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    invoice: Mapped[Invoice] = db.relationship(
        "Invoice",
        back_populates="order",
        # one order produces one invoice
        uselist=False,
    )
    cart_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey("carts.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    cart: Mapped[Cart] = db.relationship(
        "Cart",
        back_populates="order",
    )


class OrderItem(TimeStampModel):
    """
    Should determine where inventory is stored and how updated
    """

    __tablename__ = "order_items"
    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_product_id", "product_id"),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # invoice.py has quantity for several products
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    order_id: Mapped[int] = mapped_column(
        BigInteger, db.ForeignKey("orders.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, db.ForeignKey("products.id"), nullable=False
    )
    product: Mapped[Product] = db.relationship("Product", back_populates="order_items")

    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped[Order] = db.relationship("Order", back_populates="items")

    product_variant_id: Mapped[int] = mapped_column(
        BigInteger, db.ForeignKey("product_variants.id"), nullable=False
    )

    product_variant: Mapped[ProductVariant] = db.relationship(
        "ProductVariant", back_populates="order_items"
    )
