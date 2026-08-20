from fastapi import APIRouter

from app.api.routes import places

api_router = APIRouter(prefix="/api")
api_router.include_router(places.router)