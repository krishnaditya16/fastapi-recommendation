from pydantic import BaseModel, Field
from uuid import UUID

class ProductIngestSchema(BaseModel):
    id: UUID
    name: str = Field(..., max_length=255)
    description: str = ""
    category_id: int
    price: float = Field(..., ge=0.0)
    original_price: float | None = Field(None, ge=0.0)
    image: str
    rating: float = Field(0.0, ge=0.0, le=5.0)
    reviews: int = Field(0, ge=0)
    stock: int = Field(0, ge=0)
    in_stock: bool = True
    featured: bool = False
    tags: list[str] = Field(default_factory=list)

class BulkProductIngestSchema(BaseModel):
    products: list[ProductIngestSchema]

class RecommendationRequestSchema(BaseModel):
    query: str = Field(..., min_length=2)
    limit: int = Field(5, ge=1, le=50)
    user_id: int | None = Field(None, description="Opsional ID user untuk personalisasi rekomendasi")

class ChatbotRequestSchema(BaseModel):
    query: str = Field(..., min_length=2)

class UserInteractionSchema(BaseModel):
    user_id: int
    product_id: UUID
    interaction_type: str = Field(..., pattern="^(view|click|purchase)$")


