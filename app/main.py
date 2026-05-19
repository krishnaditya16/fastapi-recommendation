import sys
import asyncio

# Set Windows asyncio event loop policy for psycopg compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from app.core.config import settings

from app.api.v1.api import api_router
from app.api.v1.endpoints import health

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Root level routes
app.include_router(health.router)

# Versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
