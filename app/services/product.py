from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.schemas.product import ProductIngestSchema

class ProductService:
    async def ingest_product(self, db: AsyncSession, product: ProductIngestSchema) -> dict:
        # Periksa apakah produk sudah ada di database
        result = await db.execute(
            text("SELECT id FROM products WHERE id = :id"),
            {"id": product.id}
        )
        exists = result.scalar()

        if exists:
            # Update jika produk sudah terdaftar
            await db.execute(
                text("""
                    UPDATE products 
                    SET name = :name, description = :description, price = :price, rating = :rating
                    WHERE id = :id
                """),
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "rating": product.rating
                }
            )
            message = "Data produk berhasil diperbarui."
        else:
            # Insert jika produk baru
            await db.execute(
                text("""
                    INSERT INTO products (id, name, description, price, rating)
                    VALUES (:id, :name, :description, :price, :rating)
                """),
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "rating": product.rating
                }
            )
            message = "Data produk berhasil disimpan."

        await db.commit()
        return {"message": message, "product_id": product.id}

    async def ingest_bulk_products(self, db: AsyncSession, products: list[ProductIngestSchema]) -> dict:
        # Memproses penyimpanan massal (Unit 3)
        success_count = 0
        for product in products:
            await self.ingest_product(db, product)
            success_count += 1
        return {"message": f"Berhasil memproses {success_count} data produk secara massal."}


product_service = ProductService()
