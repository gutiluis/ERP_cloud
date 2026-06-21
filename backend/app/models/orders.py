#!/usr/bin/env python3

# filename: /backend/app/models/orders.py
# descr: relationship with product, user
from __future__ import annotations
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlite3.dbapi2 import Timestamp
from sqlalchemy.orm import relationship
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
    Index
)
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .products import Product
    from .user import User
    from .customers import Customer

class Order(TimeStampModel):
    __tablename__ = "orders"
    "table arguments is a class attribute"
    "This attribute accommodates both positional as well as keyword arguments that are normally sent to the Table constructor. "
    __table_args__ = (
        Index("ix_order_customer", "customer_id"),
        Index("ix_order_status", "status"),
        Index("ix_order_product", "product_id"),
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

    stripe_payment_intent: Mapped[str] = mapped_column(
        String(200), 
        unique=True, 
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey('products.id')
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
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

    product: Mapped["Product"] = db.relationship(
        "Product",
        back_populates="orders"
    )
    created_by_user: Mapped["AdminUser"] = db.relationship(
        "AdminUser",
        back_populates="orders"
    )
    customer: Mapped["Customer"] = db.relationship(
        "Customer",
        back_populates="orders"
    )
