#!/usr/bin/env python3


# file: /backend/app/models/admin_user.py
# descr: admin user model for flask_login


from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
from app.extensions import (
    TimeStampModel,
    Mapped,
    mapped_column,
    BigInteger,
    String,
    Boolean,
    text,
    Optional,
    Text,
    db,
    UserMixin,
    # AnonymousUserMixin
)


if TYPE_CHECKING:
    from .customers import Customer
    from .orders import Order
    from .invoice import Invoice
    from .products import Product
    from .user import User
    from .payments import Payment

# usermixin is the reason of is_authenticated(), and is_active for the route
# UserMixin is not for db columns. has: is_authenticated, is_active, is_anonymous, get_id()
class AdminUser(UserMixin, TimeStampModel):
    __tablename__ = "adminUsers"
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    admin_id: Mapped[str] = mapped_column(
        String(50),
        index=True,
        unique=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(200), 
        unique=True, 
        nullable=False, 
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # UserMixin is not for a db column. The column is overriding the property of UserMixin
    #is_active: Mapped[bool] = mapped_column(
    #    Boolean, 
    #    nullable=False, 
    #    index=True,
    #    server_default=text("0")
    #)
    
    orders: Mapped[list["Order"]] = db.relationship(
        "Order",
        back_populates="created_by_user"
    )

    additional_notes: Mapped[str | None ] = mapped_column(
        Text, 
        nullable=True
    )
    # can I use get_id() from the UserMixin clas form flask_login instead for the class AdminUser
    #def get_id(self):
     #   return self.admin_id
