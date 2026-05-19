import os
from dotenv import load_dotenv

# Memuat variabel dari berkas .env ke environment
load_dotenv()

class Settings:

    PROJECT_NAME: str = "Sistem Rekomendasi Produk"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/bootcamp_product_recommendation"
    )
    API_KEY: str = os.getenv("API_KEY")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")

settings = Settings()



