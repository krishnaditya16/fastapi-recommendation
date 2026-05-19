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
        "id": 1,
        "name": "Sepatu Lari RoadRunner Pro",
        "description": "Sepatu lari ringan berteknologi tinggi dengan bantalan empuk, sangat cocok untuk maraton atau olahraga lari santai sehari-hari.",
        "price": 850000.0,
        "rating": 4.8
    },
    {
        "id": 2,
        "name": "Sepatu Casual Santai Keren",
        "description": "Sepatu sneakers casual bahan kulit sintesis yang modis dan nyaman dipakai untuk nongkrong atau jalan-jalan santai.",
        "price": 350000.0,
        "rating": 4.2
    },
    {
        "id": 3,
        "name": "Kemeja Flanel Slim Fit Retro",
        "description": "Kemeja flanel lengan panjang bermotif kotak-kotak klasik dengan potongan slim fit modern berbahan katun tebal hangat.",
        "price": 199000.0,
        "rating": 4.5
    },
    {
        "id": 4,
        "name": "Laptop Gaming Razer Stealth",
        "description": "Laptop gaming berspesifikasi tinggi dengan kartu grafis RTX terbaru, performa kencang untuk game berat dan editing video professional.",
        "price": 18500000.0,
        "rating": 4.9
    },
    {
        "id": 5,
        "name": "Smartwatch Sport Fit Band",
        "description": "Jam tangan pintar pelacak kebugaran dengan sensor detak jantung, monitor tidur, dan notifikasi pintar dari HP smartphone.",
        "price": 499000.0,
        "rating": 4.4
    },
    {
        "id": 6,
        "name": "Kopi Arabika Gayo Premium",
        "description": "Biji kopi arabika pilihan khas dataran tinggi Gayo Aceh, dipanggang dengan tingkat kematangan medium roast aromatik nikmat.",
        "price": 85000.0,
        "rating": 4.7
    },
    {
        "id": 7,
        "name": "Tas Ransel Outdoor Waterproof",
        "description": "Tas ransel punggung backpack tangguh anti air waterproof berkapasitas besar, sangat handal untuk camping, hiking, dan petualangan alam liar.",
        "price": 299000.0,
        "rating": 4.6
    },
    {
        "id": 8,
        "name": "Sepatu Olahraga Basket Bounce",
        "description": "Sepatu olahraga basket dengan cengkaman karet kuat anti selip dan teknologi sol memantul melompat tinggi aman nyaman.",
        "price": 1100000.0,
        "rating": 4.7
    },
    {
        "id": 9,
        "name": "T-Shirt Kaos Polos Katun Bambu",
        "description": "Kaos polos lengan pendek bahan serat bambu premium ultra lembut, menyerap keringat dingin anti bakteri sangat adem.",
        "price": 75000.0,
        "rating": 4.3
    },
    {
        "id": 10,
        "name": "Powerbank Quick Charge 20000mAh",
        "description": "Pengisi daya portabel kapasitas besar 20000mAh dengan fitur pengisian daya cepat type C berkecepatan tinggi aman ringkas.",
        "price": 250000.0,
        "rating": 4.5
    }
]

async def seed_db():
    print("Memulai proses penyemaian data produk tiruan (seeder)...")
    async with engine.begin() as conn:
        for p in MOCK_PRODUCTS:
            await conn.execute(
                text("""
                    INSERT INTO products (id, name, description, price, rating)
                    VALUES (:id, :name, :description, :price, :rating)
                    ON CONFLICT (id) DO UPDATE 
                    SET name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        price = EXCLUDED.price,
                        rating = EXCLUDED.rating;
                """),
                p
            )
    print(f"Penyemaian berhasil! {len(MOCK_PRODUCTS)} produk telah berhasil disemai ke PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(seed_db())
