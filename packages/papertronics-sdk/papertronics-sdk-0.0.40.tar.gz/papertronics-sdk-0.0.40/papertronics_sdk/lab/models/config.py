from pydantic import BaseSettings


class Config(BaseSettings):
    VERSION: str = "2.1.0"
    PORT: str = "8080"

    IMAGE_STORAGE_BUCKET: str = ""
    TEMPLATE_STORAGE_BUCKET: str = ""

    DATABASE_SECRET_REF: str = None
    API_SECRET_REF: str = None
    ADMIN_TOKEN_REF: str = None

    SECRET_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DEVICE_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
