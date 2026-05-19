from fastapi import APIRouter, Depends
from app.api.v1.endpoints import products, recommend, chatbot
from app.api.deps import get_api_key

api_router = APIRouter(dependencies=[Depends(get_api_key)])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])

