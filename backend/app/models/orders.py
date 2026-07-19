#!/usr/bin/env python3

# filename: /backend/app/models/orders.py
# descr: relationship with product, user, invoice. The cart model has an order
from __future__ import annotations
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlite3.dbapi2 import Timestamp
from sqlalchemy.orm import relationship

import enum
from app.extensions import (
    db,
    Mapped,
    mapped_column,
    BigInteger,
    DateTime,
    String,
    Boolean,
    Numeric,
    TimeStampModel,
    Optional,
    Text,
    Index,
    Integer,
    Decimal,
    Enum
)


if TYPE_CHECKING:
    from .products import Product
    from .user import User
    from .customers import Customer




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
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    stripe_session_id: Mapped[str] = mapped_column(
        String(200), 
        unique=True, 
        nullable=False
    )

    stripe_payment_intent_id: Mapped[str] = mapped_column(
        String(200), 
        unique=True, 
        nullable=True
    )

    status: Mapped[OrderStatus] = mapped_column(
        db.Enum(
            OrderStatus,
            native_enum=False,
            validate_strings=True
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default="pending",
        index=True
    )

    user: Mapped["User"] = db.relationship(
        "User",
        back_populates="orders",
    )

    created_by_user_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey('adminUsers.id'),
        nullable=False
    )
    
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    customer: Mapped["Customer"] = db.relationship(
        "Customer",
        back_populates="orders"
    )

    items: Mapped[list["OrderItem"]] = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    shipping_address_1: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False
    )

    shipping_address_2: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=True
    )

    shipping_country: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    shipping_city: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    shipping_zip_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    shipping_state: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    invoice: Mapped["Invoice"] = db.relationship(
        "Invoice",
        back_populates="order",
        uselist=False, # one order produces one invoice
    )


class OrderItem(TimeStampModel):
    __tablename__ = 'order_items'
    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_product_id", "product_id"),
    )
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # invoice.py has quantity for several products
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    product_id: Mapped[str] = mapped_column(
        String(50),
        db.ForeignKey("products.product_id"),
        nullable=False,
        index=True
    )

    product: Mapped["Product"] = db.relationship(
        "Product",
        back_populates="order_items"
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    order: Mapped["Order"] = db.relationship(
        "Order",
        back_populates="items"
    )
