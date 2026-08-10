#!/usr/bin/env python3

# filename: /backend/app/models/user.py
# descr: relationship with orders.py


from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationships
from app.extensions import (
    db,
    Mapped,
    mapped_column,
    String,
    BigInteger,
    Boolean,
    TimeStampModel,
    Optional,
    Text
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
    # user enter email to send order and other notifications
    email: Mapped[str] = mapped_column(
        String(200), 
        unique=True, 
        nullable=False, 
        index=True
    )
 
    additional_notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
