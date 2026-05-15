import base64
import os
from pydantic_settings import SettingsConfigDict
from starlette.config import Config
from starlette.datastructures import Secret

class Settings:
    """
    Settings for the database connection
    """
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    config = Config(file_dir + "/.env")

    # App
    APP_NAME: str = "invoice-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = config("DATABASE_URL", cast=str)
    
    SECRET_KEY: str = config("SECRET_KEY", cast=str)
    ALGORITHM: str = config("ALGORITHM", cast=str)

    AUTH_SERVICE_URL: str = config("AUTH_SERVICE_URL", cast=str)
    INVENTORY_SERVICE_URL: str = config("INVENTORY_SERVICE_URL", cast=str)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()