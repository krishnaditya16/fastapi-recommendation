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

async def init_db():
    print("Memulai inisialisasi skema database PostgreSQL...")
    async with engine.begin() as conn:
        # 1. Buat tabel products (jika belum ada)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                price NUMERIC(12, 2) NOT NULL,
                rating NUMERIC(3, 2) NOT NULL,
                search_vector tsvector
            );
        """))

        # 1b. Buat tabel user_interactions (jika belum ada) untuk pelacakan perilaku (Unit 5: Personalization)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT REFERENCES products(id) ON DELETE CASCADE,
                interaction_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))


        # 2. Buat fungsi trigger untuk sinkronisasi otomatis tsvector berbahasa Indonesia
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION products_trigger_func() RETURNS trigger AS $$
            begin
              new.search_vector :=
                setweight(to_tsvector('indonesian', coalesce(new.name, '')), 'A') ||
                setweight(to_tsvector('indonesian', coalesce(new.description, '')), 'B');
              return new;
            end
            $$ LANGUAGE plpgsql;
        """))

        # 3. Tempel trigger ke tabel products
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS products_tsvector_update ON products;
            CREATE TRIGGER products_tsvector_update
            BEFORE INSERT OR UPDATE ON products
            FOR EACH ROW EXECUTE FUNCTION products_trigger_func();
        """))
    print("Database PostgreSQL FTS berhasil diinisialisasi sepenuhnya!")

if __name__ == "__main__":
    asyncio.run(init_db())
