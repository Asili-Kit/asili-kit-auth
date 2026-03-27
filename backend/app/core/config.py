import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AsiliKit Auth")
    DEBUG: bool = _as_bool(os.getenv("DEBUG", "False"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./asili.db")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30"))
    LOGIN_MAX_ATTEMPTS: int = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
    LOGIN_LOCK_MINUTES: int = int(os.getenv("LOGIN_LOCK_MINUTES", "15"))
    AUTO_CREATE_TABLES: bool = _as_bool(os.getenv("AUTO_CREATE_TABLES", "True"))

    def validate(self) -> None:
        # Fail fast in non-debug environments if SECRET_KEY is left unsafe.
        if not self.DEBUG and self.SECRET_KEY.strip() in {"", "changeme", "CHANGE_ME_WITH_A_LONG_RANDOM_SECRET"}:
            raise ValueError(
                "Unsafe SECRET_KEY for non-debug environment. Set a strong SECRET_KEY in .env."
            )
    
settings = Settings()
settings.validate()