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
        
        # 2. Susun konteks informasi produk
        context_lines = []
        for p in products:
            context_lines.append(
                f"- {p['name']} | Harga: Rp{p['price']:,} | Rating: {p['rating']}/5 | Deskripsi: {p['description']}"
            )
        context = "\n".join(context_lines) if context_lines else "Tidak ada produk yang cocok ditemukan."

        # 3. Panggil API OpenRouter
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            # Fallback jika API Key OpenRouter belum dikonfigurasi
            return {
                "response": f"Koneksi OpenRouter API tidak terdeteksi. Berikut adalah produk rekomendasi yang relevan berdasarkan kueri pencarian:\n\n{context}\n\n(Catatan: Harap konfigurasi OPENROUTER_API_KEY pada file .env untuk mengaktifkan asisten AI secara penuh).",
                "source_products": products
            }

        prompt = f"""
        Kita adalah asisten belanja AI profesional yang ramah dan interaktif untuk toko e-commerce kita.
        Tugas kita adalah membantu menjawab pertanyaan pembeli berdasarkan data produk di bawah ini.

        Pertanyaan Pembeli: "{user_query}"

        Konteks Produk Rekomendasi Terkait:
        {context}

        Aturan Penulisan:
        - Gunakan bahasa Indonesia yang santun, interaktif, dan komunikatif.
        - JANGAN menggunakan kata "Anda". Panggil pembeli dengan sapaan ramah "Kakak".
        - Berikan ulasan singkat yang persuasif mengapa produk tersebut direkomendasikan berdasarkan rating atau faktor harga mereka.
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
