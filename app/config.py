from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    APP_NAME: str = "HR Central"
    COMPANY_NAME: str = "Surface Paints Pvt Ltd"

    class Config:
        env_file = ".env"

settings = Settings()