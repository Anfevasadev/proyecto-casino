# back/api/router.py

from fastapi import APIRouter

from back.api.v1 import places

api_router = APIRouter()

api_router.include_router(
    places.router,
    prefix="/v1/places",   
    tags=["places"]        
)
