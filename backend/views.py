from pyramid.view import view_config
from pyramid.response import Response
import requests
import google.generativeai as genai
import json
import os
import re 
from models import Review
from sqlalchemy.exc import DBAPIError

@view_config(route_name='analyze_review', request_method='POST', renderer='json')
def analyze_review(request):
    try:
        data = request.json_body
        product_name = data.get('product_name')
        review_text = data.get('review_text')

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
                else:
                    print("♻️ Cache ditemukan tapi isinya GAGAL. Melakukan analisis ulang...")
            except:
                print("♻️ Cache rusak. Melakukan analisis ulang...")

        print("🤖 Menghubungi Gemini AI...")
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = f"""
        Analyze this product review and extract 3-5 key points.
        Output MUST be a raw JSON list of strings. 
        Example: ["Battery drains fast", "Screen is bright", "Good value"]
        Do not output markdown code blocks. Just the list.
        Review: {review_text}
        """
        
        key_points_list = []
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            
            key_points_list = json.loads(raw_text.strip())
            
        except Exception as e:
            print(f"⚠️ JSON Parsing Gagal ({e}). Mencoba fallback manual...")
            if 'response' in locals() and response.text:
                lines = response.text.split('\n')
                key_points_list = [line.strip('- *1234567890.') for line in lines if len(line) > 5]
            
            if not key_points_list:
                key_points_list = ["Analisis poin penting terkendala (Coba lagi nanti)"]

        print("🤖 Menghubungi Hugging Face...")
        hf_token = os.getenv('HUGGINGFACE_API_KEY')
        hf_headers = {"Authorization": f"Bearer {hf_token}"}
        hf_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        sentiment_label = "neutral"
        sentiment_score = 0.0
        
        try:
            hf_res = requests.post(hf_url, headers=hf_headers, json={"inputs": review_text})
            if hf_res.status_code == 200:
                hf_data = hf_res.json()
                if isinstance(hf_data, list) and len(hf_data) > 0:
                    top = max(hf_data[0], key=lambda x: x['score'])
                    sentiment_label = top['label']
                    sentiment_score = top['score']
        except Exception as hf_e:
            print(f"⚠️ Hugging Face Error: {hf_e}")

        if not isinstance(key_points_list, list):
            key_points_list = ["Gagal format data"]

        review = Review(
            product_name=product_name,
            review_text=review_text,
            sentiment=sentiment_label,
            confidence=sentiment_score,
            key_points=json.dumps(key_points_list)
        )
        request.dbsession.add(review)
        request.dbsession.flush()

        print("✅ Analisis Sukses!")
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
                kp = ["Data error"]
            
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