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
        # Drop existing tables to ensure clean schema update
        await conn.execute(text("DROP TABLE IF EXISTS user_interactions CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS products CASCADE;"))

        # 1. Buat tabel products (jika belum ada)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                category_id INT NOT NULL,
                price DECIMAL(15, 2) NOT NULL,
                original_price DECIMAL(15, 2),
                image TEXT NOT NULL,
                rating DECIMAL(2, 1) NOT NULL DEFAULT 0,
                reviews INT NOT NULL DEFAULT 0,
                stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
                in_stock BOOLEAN NOT NULL DEFAULT true,
                featured BOOLEAN NOT NULL DEFAULT false,
                tags TEXT[] NOT NULL DEFAULT '{}',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                search_vector tsvector
            );
        """))

        # 1b. Buat tabel user_interactions (jika belum ada) untuk pelacakan perilaku (Unit 5: Personalization)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id INT NOT NULL,
                product_id UUID REFERENCES products(id) ON DELETE CASCADE,
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
                setweight(to_tsvector('indonesian', coalesce(new.description, '')), 'B') ||
                setweight(to_tsvector('indonesian', array_to_string(coalesce(new.tags, '{}'), ' ')), 'C');
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
