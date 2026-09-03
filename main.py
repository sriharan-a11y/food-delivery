from contextlib import asynccontextmanager
import secrets
from models.user import User,UserRole
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request
)
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.session import (
    get_db,
    engine,
    Base
)
from models.user import User
from schemas.user import (
    UserCreate,
    UserResponse
)
from core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from config import settings
from core.config import settings
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )
    yield
    await engine.dispose()
app = FastAPI(
    title="Food Delivery API",
    lifespan=lifespan
)
app.add_middleware(
    SessionMiddleware,
    secret_key="settings.SECRET_KEY"
)
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)
@app.get("/")
async def home():
    return {
        "message": "Food delivery API is working"
    }
@app.post(
    "/users",
    response_model=UserResponse
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        ),
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            User.email == form_data.username
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email
    })
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@app.get("/auth/google")
async def google_login(
    request: Request
):
    redirect_uri = (
        settings.GOOGLE_REDIRECT_URI
    )
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )
@app.get("/auth/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        token = await oauth.google.authorize_access_token(
            request
        )
        user_info = token.get("userinfo")
        if not user_info:
            raise HTTPException(
                status_code=400,
                detail="Could not get user information from Google"
            )
        google_email = user_info.get("email")
        google_name = user_info.get("name")
        if not google_email:
            raise HTTPException(
                status_code=400,
                detail="Google account email not available"
            )
        result = await db.execute(
            select(User).where(
                User.email == google_email
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            random_password = (
                secrets.token_urlsafe(32)
            )
            user = User(
                email=google_email,
                hashed_password=hash_password(
                    random_password
                ),
                full_name=(
                    google_name
                    or "Google User"
                ),
                phone_number=None,
                role=UserRole.CUSTOMER
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email
        })
        request.session[
            "access_token"
        ] = access_token
        request.session[
            "user_id"
        ] = user.id
        return {
            "message": "Google login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Google authentication failed: {str(e)}"
            )
        )