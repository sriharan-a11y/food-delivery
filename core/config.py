from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL:str="postgresql+asyncpg://postgres:12345@localhost:5433/food_delivery"

settings=Settings()