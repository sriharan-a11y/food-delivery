from pydantic import BaseModel
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    restaurant_id: int
    total_amount: float


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class Order(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    total_amount: float
    status: OrderStatus

    class Config:
        from_attributes = True