from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app import models
from app.routes import auth, users

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Authentication API with JWT access/refresh, session rotation, and password reset",
)

# Keep this for local quickstart only; production should rely on Alembic migrations.
if settings.AUTO_CREATE_TABLES:
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} running 🚀",
        "debug": settings.DEBUG
    }
