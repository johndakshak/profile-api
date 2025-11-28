import logging
from fastapi import FastAPI
from .models.base import Base
from app.models.user_model import User
from app.database import engine
from .routes import users_routes
from app.routes import auth_route
from fastapi.staticfiles import StaticFiles



logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "Profile App",
    version = "0.0.1",
    description = "User profile system"
    )

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(users_routes.router)
app.include_router(auth_route.router)
