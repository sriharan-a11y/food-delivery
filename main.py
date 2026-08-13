from fastapi import FastAPI, Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.session import get_db,engine,Base
from models.user import User
from schemas.user import UserCreate,UserResponse 
from core.security import hash_password,verify_password,create_access_token


app=FastAPI()
@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
@app.get("/")
async def home():
    return{"message":"food delivery api iis working"}

@app.post("/users",response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession= Depends(get_db)
    ):
    new_user=User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/login")
async def login(
    form_data:OAuth2PasswordRequestForm=Depends(),
    db:AsyncSession=Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email== form_data.username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    if not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"

        )
    access_token=create_access_token({
        "sub":str(user.id),
        "email":user.email
    })
    return{
        "access_token":access_token,
        "token_type":"bearer"
    }