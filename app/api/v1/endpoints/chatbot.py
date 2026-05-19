from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.product import ChatbotRequestSchema
from app.services.chatbot import chatbot_service

router = APIRouter()

@router.post("/query", summary="Interactive AI Chatbot RAG")
async def chatbot_query(request: ChatbotRequestSchema, db: AsyncSession = Depends(get_db)):
    return await chatbot_service.generate_rag_response(db, request.query)
