#!/usr/bin/env python3

# file: /app/models/cart.py
# descr: preorder cart


import enum
from decimal import Decimal
from sqlalchemy.orm import relationship
from app.extensions import (
    db,
    Mapped,
    mapped_column,
    BigInteger,
    Numeric,
    TimeStampModel,
    Integer
)
    


class CartStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CONVERTED = "converted"


class Cart(TimeStampModel):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    user: Mapped["User"] = db.relationship(
        "User",
        back_populates="carts",
    )
    
    status: Mapped[CartStatus] = mapped_column(
        db.Enum(
            CartStatus,
            native_enum=False,
            validate_string=True
        ),
        nullable=False,
        default=CartStatus.PENDING,
        server_default=CartStatus.PENDING.value,
        index=True
    )

    items: Mapped[list["CartItem"]] = db.relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )

class CartItem(TimeStampModel):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    cart_id: Mapped[int] = mapped_column(
        db.ForeignKey("carts.id"),
        nullable=False,
        index=True
    )
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey("products.id"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    cart: Mapped["Cart"] = db.relationship(
        "Cart",
        back_populates="items"
    )
    product: Mapped["Product"] = db.relationship(
        "Product",
        back_populates="cart_items"
    )
