from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.product import RecommendationRequestSchema, UserInteractionSchema
from app.services.recommendation import recommendation_service

router = APIRouter()

@router.post("/fts", summary="Get FTS + Heuristic Recommendations")
async def recommend_products(request: RecommendationRequestSchema, db: AsyncSession = Depends(get_db)):
    return await recommendation_service.get_fts_recommendations(db, request)

@router.post("/track", summary="Track Customer Behavior (Implicit Feedback)")
async def track_interaction(interaction: UserInteractionSchema, db: AsyncSession = Depends(get_db)):
    return await recommendation_service.track_interaction(db, interaction)
