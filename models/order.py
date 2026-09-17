from sqlalchemy import Column, Integer, Float, ForeignKey, Enum as SqlEnum
from database.session import Base
from models.base import BaseIDMixin, TimestampMixin
from schemas.order import OrderStatus


class Order(Base, BaseIDMixin, TimestampMixin):
    __tablename__ = "orders"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(
        SqlEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    ) 