from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from models.user import User, UserRole
from models.order import OrderStatus
from schemas.order import Order as OrderSchema, OrderCreate, OrderUpdateStatus
from auth.deps import get_current_active_user
from crud.crud_order import order_crud
#from crud.crud_restaurant import restaurant as crud_restaurant

import json
from kafka import publish_message

router = APIRouter()


NOTIFICATION_TOPIC = "notifications"

# ...


@router.post("/", response_model=OrderSchema)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    #restaurant = await crud_restaurant.get(db, id=order_in.restaurant_id)
    #if not restaurant:
      #  raise HTTPException(status_code=404, detail="Restaurant not found")

    order = await order_crud.create_order(db, user_id=current_user.id, order_in=order_in)
    if not order:
            raise HTTPException(status_code=400, detail="Your cart is empty")


    event = {
        "type": "ORDER_CREATED",
        "order_id": order.id,
        "user_id": current_user.id,
        "email": current_user.email,
        "name": current_user.full_name,
        "restaurant_id": order.restaurant_id,
        "total": float(order.total_amount),
    }

    await publish_message(
        NOTIFICATION_TOPIC,
        json.dumps(event).encode("utf-8")
    )

    return order



@router.get("/", response_model=List[OrderSchema])
async def read_orders(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await order_crud.get_orders_by_user(db, user_id=current_user.id)


@router.get("/{order_id}", response_model=OrderSchema)
async def read_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    order = await order_crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    #restaurant = await crud_restaurant.get(db, id=order.restaurant_id)
    if (
        current_user.id != order.user_id
        and current_user.role != UserRole.ADMIN
        #and (restaurant is None or restaurant.owner_id != current_user.id)
    ):
        raise HTTPException(status_code=403, detail="Not enough privileges")

    return order


@router.put("/{order_id}/status", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    status_in: OrderUpdateStatus,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    order = await order_crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    #restaurant = await crud_restaurant.get(db, id=order.restaurant_id)
    can_manage = current_user.role == UserRole.ADMIN
    #if restaurant and restaurant.owner_id == current_user.id:
     #   can_manage = True
    if current_user.role == UserRole.DELIVERY_PARTNER:
        can_manage = True

    if not can_manage:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    return await order_crud.update_order_status(db, order_id=order_id, status=status_in.status.value)
