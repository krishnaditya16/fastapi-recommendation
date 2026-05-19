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
                    SET name = :name, 
                        description = :description, 
                        category_id = :category_id,
                        price = :price, 
                        original_price = :original_price,
                        image = :image,
                        rating = :rating,
                        reviews = :reviews,
                        stock = :stock,
                        in_stock = :in_stock,
                        featured = :featured,
                        tags = :tags,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "category_id": product.category_id,
                    "price": product.price,
                    "original_price": product.original_price,
                    "image": product.image,
                    "rating": product.rating,
                    "reviews": product.reviews,
                    "stock": product.stock,
                    "in_stock": product.in_stock,
                    "featured": product.featured,
                    "tags": product.tags
                }
            )
            message = "Data produk berhasil diperbarui."
        else:
            # Insert jika produk baru
            await db.execute(
                text("""
                    INSERT INTO products (
                        id, name, description, category_id, price, original_price, 
                        image, rating, reviews, stock, in_stock, featured, tags, created_at, updated_at
                    )
                    VALUES (
                        :id, :name, :description, :category_id, :price, :original_price, 
                        :image, :rating, :reviews, :stock, :in_stock, :featured, :tags, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """),
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "category_id": product.category_id,
                    "price": product.price,
                    "original_price": product.original_price,
                    "image": product.image,
                    "rating": product.rating,
                    "reviews": product.reviews,
                    "stock": product.stock,
                    "in_stock": product.in_stock,
                    "featured": product.featured,
                    "tags": product.tags
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

