import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.recommendation import recommendation_service
from app.schemas.product import RecommendationRequestSchema
from app.core.config import settings

class ChatbotService:
    async def generate_rag_response(self, db: AsyncSession, user_query: str) -> dict:
        # 1. Temukan produk yang relevan menggunakan mesin Full-Text Search kita
        search_request = RecommendationRequestSchema(query=user_query, limit=3)
        search_results = await recommendation_service.get_fts_recommendations(db, search_request)
        
        products = search_results.get("results", [])
        
        # 2. Susun konteks informasi produk dengan fitur transaksional lengkap
        context_lines = []
        for p in products:
            stock_status = "Tersedia" if p.get("in_stock", True) else "Habis"
            discount_info = ""
            if p.get("original_price") and p["original_price"] > p["price"]:
                discount_info = f" (Diskon aktif dari Rp{p['original_price']:,})"
            
            tags_str = ", ".join(p.get("tags", []))
            tags_info = f" | Tag: {tags_str}" if tags_str else ""
            
            context_lines.append(
                f"- {p['name']} | Harga: Rp{p['price']:,}{discount_info} | Rating: {p['rating']}/5 | Stok: {stock_status} ({p.get('stock', 0)} pcs) | Deskripsi: {p['description']}{tags_info}"
            )
        context = "\n".join(context_lines) if context_lines else "Tidak ada produk yang cocok ditemukan."

        # 3. Panggil API OpenRouter
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            # Fallback jika API Key OpenRouter belum dikonfigurasi
            return {
                "response": f"Koneksi OpenRouter API tidak terdeteksi. Berikut adalah produk rekomendasi yang relevan berdasarkan kueri pencarian Kakak:\n\n{context}\n\n(Catatan: Harap konfigurasi OPENROUTER_API_KEY pada file .env untuk mengaktifkan asisten AI secara penuh).",
                "source_products": products
            }

        prompt = f"""
        Kita adalah asisten belanja AI profesional yang ramah, persuasif, dan interaktif untuk toko e-commerce kita.
        Tugas kita adalah membantu menjawab pertanyaan pembeli berdasarkan data katalog produk nyata di bawah ini.

        Pertanyaan Pembeli: "{user_query}"

        Konteks Produk Rekomendasi Terkait dari Database:
        {context}

        Aturan Penulisan Respon:
        - Gunakan bahasa Indonesia yang santun, interaktif, hangat, dan komunikatif.
        - JANGAN PERNAH menggunakan kata "Anda". Panggil pembeli dengan sapaan hangat "Kakak".
        - Rekomendasikan produk dari konteks di atas secara jujur dan persuasif.
        - Manfaatkan informasi diskon aktif (original_price vs price), ulasan rating, atau sisa stok secara proaktif (misal: "Wah, ini sedang diskon lho Kak!", "Stoknya terbatas tinggal 50 saja Kak, jadi buruan diorder ya!").
        - Jika stok habis (stock = 0 atau in_stock = false), informasikan dengan sopan dan rekomendasikan alternatif lain yang tersedia.
        """

        # Format standar request chat OpenRouter (seperti OpenAI API)
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": settings.PROJECT_NAME
        }
        payload = {
            "model": "baidu/cobuddy:free",  # Memilih model free Baidu Qianfan CoBuddy yang sangat stabil dan bebas rate-limit
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=15.0)
                if response.status_code == 200:
                    data = response.json()
                    text_response = data["choices"][0]["message"]["content"]
                    return {
                        "response": text_response,
                        "source_products": products
                    }
                else:
                    raise Exception(f"OpenRouter Error {response.status_code}: {response.text}")
        except Exception as e:
            return {
                "response": f"Gagal menghubungi layanan AI OpenRouter ({str(e)}). Berikut adalah daftar produk rekomendasi yang relevan:\n\n{context}",
                "source_products": products
            }


chatbot_service = ChatbotService()
