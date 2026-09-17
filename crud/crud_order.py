from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import Order, OrderStatus
from schemas.order import OrderCreate


class OrderCRUD:

    async def create_order(
        self,
        db: AsyncSession,
        user_id: int,
        order_in: OrderCreate
    ):
        order = Order(
            user_id=user_id,
            restaurant_id=order_in.restaurant_id,
            total_amount=order_in.total_amount,
            status=OrderStatus.PENDING
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)

        return order

    async def get_order(
        self,
        db: AsyncSession,
        order_id: int
    ):
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_orders_by_user(
        self,
        db: AsyncSession,
        user_id: int
    ):
        result = await db.execute(
            select(Order).where(Order.user_id == user_id)
        )
        return result.scalars().all()

    async def update_order_status(
        self,
        db: AsyncSession,
        order_id: int,
        status: str
    ):
        order = await self.get_order(db, order_id)

        if order:
            order.status = status
            await db.commit()
            await db.refresh(order)

        return order


order_crud = OrderCRUD()