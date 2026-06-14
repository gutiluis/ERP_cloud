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
    CheckConstraint)
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import mapped_column, Mapped
from flask_migrate import Migrate
from sqlalchemy.sql import func


db = SQLAlchemy()
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
        server_onupdate=func.now(),
        nullable=False
    )
