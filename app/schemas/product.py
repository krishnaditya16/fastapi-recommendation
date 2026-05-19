from pydantic import BaseModel, Field

class ProductIngestSchema(BaseModel):
    id: int
    name: str = Field(..., max_length=100)
    description: str
    price: float = Field(..., ge=0.0)
    rating: float = Field(..., ge=0.0, le=5.0)

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
    product_id: int
    interaction_type: str = Field(..., pattern="^(view|click|purchase)$")

