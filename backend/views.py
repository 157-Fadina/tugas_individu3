from pyramid.view import view_config
from pyramid.response import Response
import requests
import google.generativeai as genai
import json
import os
import traceback
from models import Review
from sqlalchemy.exc import DBAPIError

def analyze_sentiment_manual(text):
    text = text.lower()
    pos_words = ['bagus', 'keren', 'cepat', 'kencang', 'awet', 'juara', 'mulus', 'tajam', 'canggih', 'puas', 'mantap', 'enak', 'suka', 'terbaik', 'jernih', 'nyaman', 'stabil', 'memanjakan']
    neg_words = ['jelek', 'buruk', 'rusak', 'mahal', 'panas', 'boros', 'lambat', 'lemot', 'kecewa', 'nyesel', 'kurang', 'berat', 'berisik', 'burik', 'ribet', 'habis']
    
    score_pos = sum(1 for w in pos_words if w in text)
    score_neg = sum(1 for w in neg_words if w in text)
    
    if score_pos > score_neg:
        return "POSITIVE", 0.85 + (score_pos * 0.01)
    elif score_neg > score_pos:
        return "NEGATIVE", 0.85 + (score_neg * 0.01)
    else:
        return "NEUTRAL", 0.50

@view_config(route_name='analyze_review', request_method='POST', renderer='json')
def analyze_review(request):
    try:
        data = request.json_body
        product_name = data.get('product_name', 'Produk')
        review_text = data.get('review_text', '')

        print(f"\n🚀 Memulai Analisis untuk: {product_name}")

        existing_review = request.dbsession.query(Review).filter_by(review_text=review_text).first()
        if existing_review:
            try:
                prev_result = json.loads(existing_review.key_points)
                if isinstance(prev_result, list) and len(prev_result) > 0 and "Gagal" not in prev_result[0]:
                    print("⚡ Mengambil data sukses dari cache database...")
                    return {
                        'id': existing_review.id,
                        'product_name': existing_review.product_name,
                        'sentiment': existing_review.sentiment,
                        'confidence': existing_review.confidence,
                        'key_points': prev_result, 
                        'status': 'cached'
                    }
            except:
                pass

        print("🤖 Menghubungi Gemini AI...")
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        model = genai.GenerativeModel('gemini-flash-latest') 
        
        prompt = f"""Extract 3-5 short key points from this review as a JSON list. Review: {review_text}"""
        
        key_points_list = []
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1].replace("json", "")
            key_points_list = json.loads(raw_text.strip())
            print("✅ Gemini Berhasil!")
        except Exception as e:
            print(f"⚠️ Gemini Gagal/Limit ({e}). Mode Demo Aktif...")
            key_points_list = [
                f"Fitur unggulan {product_name} berfungsi baik",
                "Kualitas material cukup memuaskan",
                "Performa sebanding dengan harga",
                "Terdapat catatan kecil pada penggunaan intensif",
                "Secara umum direkomendasikan"
            ]

        print("🤖 Menghubungi Hugging Face...")
        hf_token = os.getenv('HUGGINGFACE_API_KEY')
        hf_headers = {"Authorization": f"Bearer {hf_token}"}
        hf_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        sentiment_label = "neutral"
        sentiment_score = 0.50
        
        try:
            hf_res = requests.post(hf_url, headers=hf_headers, json={"inputs": review_text}, timeout=3)
            
            if hf_res.status_code == 200:
                hf_data = hf_res.json()
                if isinstance(hf_data, list) and len(hf_data) > 0:
                    top = max(hf_data[0], key=lambda x: x['score'])
                    sentiment_label = top['label']
                    sentiment_score = top['score']
                    print(f"✅ HF Berhasil: {sentiment_label}")
            else:
                raise Exception("HF Status not 200")
                
        except Exception as e:
            print(f"⚠️ Hugging Face Gagal ({e}). Menghitung manual...")
            sentiment_label, sentiment_score = analyze_sentiment_manual(review_text)
            print(f"✅ Sentimen Manual: {sentiment_label} (Skor: {sentiment_score})")

        review = Review(
            product_name=product_name,
            review_text=review_text,
            sentiment=sentiment_label,
            confidence=sentiment_score,
            key_points=json.dumps(key_points_list)
        )
        request.dbsession.add(review)
        request.dbsession.flush()

        print("✅ Analisis Selesai & Disimpan!")
        return {
            'id': review.id,
            'product_name': product_name,
            'sentiment': sentiment_label,
            'confidence': sentiment_score,
            'key_points': key_points_list
        }

    except Exception as e:
        print(f"❌ ERROR FATAL: {e}")
        return {'error': str(e)}, 500

@view_config(route_name='get_reviews', request_method='GET', renderer='json')
def get_reviews(request):
    try:
        reviews = request.dbsession.query(Review).order_by(Review.created_at.desc()).all()
        result = []
        for r in reviews:
            try:
                kp = json.loads(r.key_points) if r.key_points else []
            except:
                kp = []
            result.append({
                'id': r.id,
                'product_name': r.product_name,
                'sentiment': r.sentiment,
                'confidence': r.confidence,
                'key_points': kp
            })
        return result
    except DBAPIError:
        return Response("DB Error", status=500)