# filename: /backend/app/models/user.py
# descr: relationship with orders.py. is the buyer

from __future__ import annotations

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixin import TimeStampModel


class User(TimeStampModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
    )

    additional_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
