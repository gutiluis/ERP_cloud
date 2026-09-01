# file: /backend/app/models/admin_user.py
# descr: admin user model for flask_login


from flask_login import UserMixin
from sqlalchemy import (
    BigInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixin import TimeStampModel


class AdminUser(UserMixin, TimeStampModel):
    __tablename__ = "adminUsers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    admin_id: Mapped[str] = mapped_column(
        String(50), index=True, unique=True, nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    email: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False, index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
