import asyncio
import sys
import os

# Set Windows asyncio event loop policy for psycopg compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Tambahkan path proyek ke sys.path agar impor modul berjalan lancar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine

# Daftar produk tiruan berkualitas tinggi berbahasa Indonesia untuk pengujian FTS & Heuristik
MOCK_PRODUCTS = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Sepatu Lari RoadRunner Pro",
        "description": "Sepatu lari ringan berteknologi tinggi dengan bantalan empuk, sangat cocok untuk maraton atau olahraga lari santai sehari-hari.",
        "category_id": 1,
        "price": 850000.0,
        "original_price": 950000.0,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "rating": 4.8,
        "reviews": 120,
        "stock": 50,
        "in_stock": True,
        "featured": True,
        "tags": ["Sepatu", "Lari", "Sport", "Olahraga", "Merah"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "Sepatu Casual Santai Keren",
        "description": "Sepatu sneakers casual bahan kulit sintesis yang modis dan nyaman dipakai untuk nongkrong atau jalan-jalan santai.",
        "category_id": 1,
        "price": 350000.0,
        "original_price": 400000.0,
        "image": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77",
        "rating": 4.2,
        "reviews": 85,
        "stock": 100,
        "in_stock": True,
        "featured": False,
        "tags": ["Sepatu", "Casual", "Sneakers", "Keren", "Putih"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "name": "Kemeja Flanel Slim Fit Retro",
        "description": "Kemeja flanel lengan panjang bermotif kotak-kotak klasik dengan potongan slim fit modern berbahan katun tebal hangat.",
        "category_id": 2,
        "price": 199000.0,
        "original_price": 250000.0,
        "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c",
        "rating": 4.5,
        "reviews": 95,
        "stock": 40,
        "in_stock": True,
        "featured": True,
        "tags": ["Kemeja", "Flanel", "Baju", "Pakaian", "Retro"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "name": "Laptop Gaming Razer Stealth",
        "description": "Laptop gaming berspesifikasi tinggi dengan kartu grafis RTX terbaru, performa kencang untuk game berat dan editing video professional.",
        "category_id": 3,
        "price": 18500000.0,
        "original_price": 19900000.0,
        "image": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed",
        "rating": 4.9,
        "reviews": 34,
        "stock": 10,
        "in_stock": True,
        "featured": True,
        "tags": ["Laptop", "Gaming", "Razer", "Stealth", "Komputer"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "name": "Smartwatch Sport Fit Band",
        "description": "Jam tangan pintar pelacak kebugaran dengan sensor detak jantung, monitor tidur, dan notifikasi pintar dari HP smartphone.",
        "category_id": 3,
        "price": 499000.0,
        "original_price": 599000.0,
        "image": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a",
        "rating": 4.4,
        "reviews": 230,
        "stock": 0,
        "in_stock": False,
        "featured": False,
        "tags": ["Jam", "Smartwatch", "Sport", "Fitness", "Gadget"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000006",
        "name": "Kopi Arabika Gayo Premium",
        "description": "Biji kopi arabika pilihan khas dataran tinggi Gayo Aceh, dipanggang dengan tingkat kematangan medium roast aromatik nikmat.",
        "category_id": 4,
        "price": 85000.0,
        "original_price": 95000.0,
        "image": "https://images.unsplash.com/photo-1447933601403-0c6688de566e",
        "rating": 4.7,
        "reviews": 512,
        "stock": 120,
        "in_stock": True,
        "featured": True,
        "tags": ["Kopi", "Arabika", "Gayo", "Minuman", "Premium"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000007",
        "name": "Tas Ransel Outdoor Waterproof",
        "description": "Tas ransel punggung backpack tangguh anti air waterproof berkapasitas besar, sangat handal untuk camping, hiking, dan petualangan alam liar.",
        "category_id": 2,
        "price": 299000.0,
        "original_price": 350000.0,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
        "rating": 4.6,
        "reviews": 78,
        "stock": 35,
        "in_stock": True,
        "featured": False,
        "tags": ["Tas", "Ransel", "Outdoor", "Backpack", "Waterproof"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000008",
        "name": "Sepatu Olahraga Basket Bounce",
        "description": "Sepatu olahraga basket dengan cengkaman karet kuat anti selip dan teknologi sol memantul melompat tinggi aman nyaman.",
        "category_id": 1,
        "price": 1100000.0,
        "original_price": 1250000.0,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "rating": 4.7,
        "reviews": 46,
        "stock": 15,
        "in_stock": True,
        "featured": False,
        "tags": ["Sepatu", "Olahraga", "Basket", "Bounce", "Hitam"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000009",
        "name": "T-Shirt Kaos Polos Katun Bambu",
        "description": "Kaos polos lengan pendek bahan serat bambu premium ultra lembut, menyerap keringat dingin anti bakteri sangat adem.",
        "category_id": 2,
        "price": 75000.0,
        "original_price": 85000.0,
        "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518",
        "rating": 4.3,
        "reviews": 420,
        "stock": 200,
        "in_stock": True,
        "featured": False,
        "tags": ["Baju", "Kaos", "T-Shirt", "Polos", "Bambu"]
    },
    {
        "id": "00000000-0000-0000-0000-000000000010",
        "name": "Powerbank Quick Charge 20000mAh",
        "description": "Pengisi daya portabel kapasitas besar 20000mAh dengan fitur pengisian daya cepat type C berkecepatan tinggi aman ringkas.",
        "category_id": 3,
        "price": 250000.0,
        "original_price": 320000.0,
        "image": "https://images.unsplash.com/photo-1609592424085-f55a10972c67",
        "rating": 4.5,
        "reviews": 310,
        "stock": 60,
        "in_stock": True,
        "featured": False,
        "tags": ["Powerbank", "Charger", "Baterai", "Gadget", "Aksesoris"]
    }
]

async def seed_db():
    print("Memulai proses penyemaian data produk tiruan (seeder)...")
    async with engine.begin() as conn:
        for p in MOCK_PRODUCTS:
            await conn.execute(
                text("""
                    INSERT INTO products (
                        id, name, description, category_id, price, original_price, 
                        image, rating, reviews, stock, in_stock, featured, tags, created_at, updated_at
                    )
                    VALUES (
                        :id, :name, :description, :category_id, :price, :original_price, 
                        :image, :rating, :reviews, :stock, :in_stock, :featured, :tags, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (id) DO UPDATE 
                    SET name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        category_id = EXCLUDED.category_id,
                        price = EXCLUDED.price,
                        original_price = EXCLUDED.original_price,
                        image = EXCLUDED.image,
                        rating = EXCLUDED.rating,
                        reviews = EXCLUDED.reviews,
                        stock = EXCLUDED.stock,
                        in_stock = EXCLUDED.in_stock,
                        featured = EXCLUDED.featured,
                        tags = EXCLUDED.tags,
                        updated_at = CURRENT_TIMESTAMP;
                """),
                p
            )
    print(f"Penyemaian berhasil! {len(MOCK_PRODUCTS)} produk telah berhasil disemai ke PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(seed_db())
