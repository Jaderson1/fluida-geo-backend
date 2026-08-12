from fastapi import APIRouter

from app.api.routes import attractions

api_router = APIRouter(prefix="/api")
api_router.include_router(attractions.router)
