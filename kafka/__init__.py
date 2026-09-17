import asyncio
from typing import Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from core.config import settings

producer: Optional[AIOKafkaProducer] = None
consumer: Optional[AIOKafkaConsumer] = None
consumer_task: Optional[asyncio.Task] = None

NOTIFICATION_TOPIC = "notifications"
CONSUMER_GROUP = "notification-consumers"

async def create_kafka_producer() -> AIOKafkaProducer:
    global producer
    if producer is None:
        producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
    return producer

async def close_kafka() -> None:
    global producer, consumer, consumer_task
    if consumer_task is not None:
        consumer_task.cancel()
        consumer_task = None
    if consumer is not None:
        await consumer.stop()
        consumer = None
    if producer is not None:
        await producer.stop()
        producer = None

async def publish_message(topic: str, value: bytes) -> None:
    producer = await create_kafka_producer()
    await producer.send_and_wait(topic, value)

async def create_kafka_consumer() -> AIOKafkaConsumer:
    global consumer
    if consumer is None:
        consumer = AIOKafkaConsumer(
            NOTIFICATION_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=CONSUMER_GROUP,
            auto_offset_reset="latest",
        )
        await consumer.start()
    return consumer

import json
from notifications.email import send_order_email

async def _notification_consumer_loop():
    consumer = await create_kafka_consumer()

    async for msg in consumer:
        data = json.loads(msg.value.decode())
        
        if data["type"] == "ORDER_CREATED":
            await send_order_email(data)
            

async def start_kafka_consumer() -> None:
    global consumer_task
    if consumer_task is None:
        consumer_task = asyncio.create_task(_notification_consumer_loop())
