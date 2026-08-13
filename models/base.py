from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from database.session import Base

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BaseIDMixin:
    id = Column(Integer, primary_key=True, index=True)