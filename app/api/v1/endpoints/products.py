from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.product import ProductIngestSchema, BulkProductIngestSchema
from app.services.product import product_service

router = APIRouter()

@router.post("/ingest", summary="Ingest Single Product")
async def ingest_product(product: ProductIngestSchema, db: AsyncSession = Depends(get_db)):
    return await product_service.ingest_product(db, product)

@router.post("/ingest/bulk", summary="Ingest Bulk Products")
async def ingest_bulk_products(payload: BulkProductIngestSchema, db: AsyncSession = Depends(get_db)):
    return await product_service.ingest_bulk_products(db, payload.products)
