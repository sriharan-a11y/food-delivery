from fastapi import APIRouter,HTTPException,Depends
from auth.deps import get_current_active_user
from models.user import User
from kafka import publish_message
from redis_client import cache_get, cache_set
router = APIRouter()
NOTIFICATION_TOPIC ="notifications"
@router.post("/notification/send")
async def send_notification(message:str,current_user:User = Depends(get_current_active_user)):
    payload = message.encode("utf-8")
    await publish_message(NOTIFICATION_TOPIC,payload)
    await cache_set(f"notification:{current_user.id}",message,expire_seconds=600)
    return {"status":"queued","message":message}

@router.get("/notification/latest")
async def latest_notification(current_user: User=Depends(get_current_active_user)):
    cached =await cache_get(f"notification:{current_user.id}")
    if cached is None:
        raise HTTPException(status_code=404,detail="No recent Notification")
    return {"message":cached}
