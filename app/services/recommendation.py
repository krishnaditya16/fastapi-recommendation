from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from app.schemas.product import RecommendationRequestSchema, UserInteractionSchema

class RecommendationService:
    async def track_interaction(self, db: AsyncSession, interaction: UserInteractionSchema) -> dict:
        # 1. Periksa apakah produk dengan ID tersebut benar-benar ada di database (Graceful Check)
        product_check = await db.execute(
            text("SELECT id FROM products WHERE id = :product_id"),
            {"product_id": interaction.product_id}
        )
        if not product_check.first():
            raise HTTPException(
                status_code=404,
                detail=f"Gagal mencatat interaksi: Produk dengan ID '{interaction.product_id}' tidak ditemukan di database."
            )

        # 2. Catat perilaku pembeli (Implicit Feedback) ke database
        await db.execute(
            text("""
                INSERT INTO user_interactions (user_id, product_id, interaction_type)
                VALUES (:user_id, :product_id, :interaction_type)
            """),
            {
                "user_id": interaction.user_id,
                "product_id": interaction.product_id,
                "interaction_type": interaction.interaction_type
            }
        )
        await db.commit()
        return {
            "message": "Data aktivitas perilaku pelanggan berhasil disimpan.",
            "user_id": interaction.user_id,
            "product_id": interaction.product_id,
            "interaction_type": interaction.interaction_type
        }

    async def get_fts_recommendations(self, db: AsyncSession, request: RecommendationRequestSchema) -> dict:
        # 1. Ambil riwayat interaksi terbaru pembeli jika user_id dikirim
        recent_product_ids = []
        if request.user_id is not None:
            recent_result = await db.execute(
                text("""
                    SELECT DISTINCT product_id 
                      FROM user_interactions 
                     WHERE user_id = :user_id 
                     LIMIT 10
                """),
                {"user_id": request.user_id}
            )
            recent_product_ids = [str(row[0]) for row in recent_result.all()]

        # 2. Parsing kueri dan filter stopwords percakapan bahasa Indonesia agar lebih presisi
        conversational_stopwords = {
            "produk", "barang", "toko", "ini", "itu", "yang", "di", "ke", "dari", 
            "apa", "saja", "ada", "jual", "dijual", "beli", "dibeli", "bisa", "mau", 
            "cari", "mencari", "tanya", "bagaimana", "adalah", "dan", "atau", "dengan",
            "untuk", "pada", "dalam", "buat", "kah", "dong", "sih", "kok"
        }
        clean_terms = [
            t for t in request.query.split() 
            if t.isalnum() and t.lower() not in conversational_stopwords
        ]
        
        # Fallback ke kata kunci asli jika semua kata tergolong stopword
        if not clean_terms:
            clean_terms = [t for t in request.query.split() if t.isalnum()]
            
        if not clean_terms:
            return {"message": "Kueri pencarian tidak valid.", "results": []}
        
        query_str = " | ".join(clean_terms)

        
        # Jalankan kueri Full-Text Search menggunakan to_tsquery dan hitung skor ts_rank
        sql = text("""
            SELECT id, name, description, category_id, price, original_price, 
                   image, rating, reviews, stock, in_stock, featured, tags,
                   ts_rank(search_vector, to_tsquery('indonesian', :query)) as fts_rank
              FROM products
             WHERE search_vector @@ to_tsquery('indonesian', :query)
           ORDER BY fts_rank DESC
              LIMIT :limit
        """)
        
        # Kita ambil 2x limit yang diminta untuk proses Heuristic Re-ranking di Python
        result = await db.execute(sql, {"query": query_str, "limit": request.limit * 2})
        products_list = result.all()

        if not products_list:
            return {"message": "Tidak ditemukan produk yang memenuhi kriteria kueri pencarian.", "results": []}

        # 3. Heuristic Weighted Scoring
        # Kombinasi bobot: 50% FTS Rank, 30% Rating, 20% Faktor Harga (Semakin murah semakin tinggi skornya)
        w_fts = 0.5
        w_rating = 0.3
        w_price = 0.2
        
        scored_products = []
        for p in products_list:
            p_id, name, desc, category_id, price, original_price, image, rating, reviews, stock, in_stock, featured, tags, fts_rank = p
            p_id_str = str(p_id)
            
            # Normalisasi Rating (Skala 0.0 - 1.0)
            norm_rating = float(rating) / 5.0
            
            # Normalisasi Harga (Asumsi harga maksimal 2.000.000, semakin murah semakin tinggi skornya)
            norm_price = 1.0 - (float(price) / 2000000.0)
            norm_price = max(0.1, min(1.0, norm_price)) # Batasan nilai 0.1 - 1.0
            
            # Kalkulasi Skor Heuristik Dasar
            base_score = (float(fts_rank) * w_fts) + (norm_rating * w_rating) + (norm_price * w_price)
            
            # Personalisasi Booster (Implicit Feedback): 
            # Jika pembeli memiliki riwayat interaksi terbaru dengan produk ini, beri bonus skor +0.25!
            booster = 0.0
            if p_id_str in recent_product_ids:
                booster = 0.25
            
            final_score = base_score + booster
            
            scored_products.append({
                "id": p_id_str,
                "name": name,
                "description": desc,
                "category_id": category_id,
                "price": float(price),
                "original_price": float(original_price) if original_price is not None else None,
                "image": image,
                "rating": float(rating),
                "reviews": reviews,
                "stock": stock,
                "in_stock": in_stock,
                "featured": featured,
                "tags": tags,
                "fts_rank": float(fts_rank),
                "personalization_boost": booster,
                "final_score": round(final_score, 4)
            })

        # Urutkan secara menurun berdasarkan final_score
        scored_products.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Batasi sesuai limit asli permintaan
        results = scored_products[:request.limit]

        # Siapkan pesan informasi metode kalkulasi rekomendasi
        method_msg = "Heuristic Weighted Scoring"
        if request.user_id is not None and recent_product_ids:
            method_msg += " + Personalization Boost (Implicit Feedback)"

        return {
            "message": f"Rekomendasi pencarian berhasil diproses menggunakan {method_msg}.",
            "query": request.query,
            "user_id": request.user_id,
            "results": results
        }


recommendation_service = RecommendationService()
