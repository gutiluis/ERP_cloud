#!/usr/bin/env python3


# file: /backend/app/extensions.py
# descr: factory pattern extensions instances of init_app()


from flask_login import LoginManager, UserMixin, current_user, login_required
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    String, 
    BigInteger, 
    Numeric, 
    Text, 
    Boolean, 
    DateTime, 
    text, 
    Enum,
    Index,
    Integer,
    CheckConstraint,
    UniqueConstraint)
from decimal import Decimal, InvalidOperation
from typing import Optional
from sqlalchemy.orm import mapped_column, Mapped
from flask_migrate import Migrate
from sqlalchemy.sql import func


db = SQLAlchemy()


# LoginManager is extension object not configuration data
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


#class AnonymousUser(AnonymousUserMixin):
#    is_admin = False

# login_manager.anonymous_user = AnonymousUser


migrate = Migrate()

class TimeStampModel(db.Model):
    __abstract__ = True
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
