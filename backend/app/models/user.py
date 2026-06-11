#!/usr/bin/env python3

# filename: user.py
# descr: relationship with orders.py
from __future__ import annotations
from typing import TYPE_CHECKING

from app.extensions import (
    db,
    Mapped,
    mapped_column,
    String,
    BigInteger,
    Boolean,
    TimeStampModel,
    Optional,
    Text,
    text
)

if TYPE_CHECKING:
    from .orders import Order


class User(TimeStampModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, 
        index=True,
        server_default=text("0")
    )
    
    is_admin: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False,
        server_default=text("0")
    )
    
    orders: Mapped[list["Order"]] = db.relationship(
        "Order",
        back_populates="created_by_user"
    )
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)