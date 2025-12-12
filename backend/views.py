from pyramid.view import view_config
from pyramid.response import Response
import requests
import google.generativeai as genai
import json
import os
from models import Review
from sqlalchemy.exc import DBAPIError

@view_config(route_name='analyze_review', request_method='POST', renderer='json')
def analyze_review(request):
    try:
        data = request.json_body
        product_name = data.get('product_name')
        review_text = data.get('review_text')

        existing_review = request.dbsession.query(Review).filter_by(review_text=review_text).first()
        if existing_review:
             print("⚡ Mengambil data dari cache database...")
             return {
                'id': existing_review.id,
                'product_name': existing_review.product_name,
                'sentiment': existing_review.sentiment,
                'confidence': existing_review.confidence,
                'key_points': json.loads(existing_review.key_points), 
                'status': 'cached'
            }

        print("🤖 Meminta analisis ke AI...")
        
        sentiment_result = call_huggingface_sentiment(review_text)
        key_points_list = extract_key_points_gemini(review_text)

        review = Review(
            product_name=product_name,
            review_text=review_text,
            sentiment=sentiment_result['label'],
            confidence=sentiment_result['score'],
            key_points=json.dumps(key_points_list) 
        )
        request.dbsession.add(review)
        request.dbsession.flush() 

        return {
            'id': review.id,
            'product_name': product_name,
            'sentiment': sentiment_result['label'],
            'confidence': sentiment_result['score'],
            'key_points': key_points_list
        }

    except Exception as e:
        print(f"Error: {e}")
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='get_reviews', request_method='GET', renderer='json')
def get_reviews(request):
    try:
        reviews = request.dbsession.query(Review).order_by(Review.created_at.desc()).all()
        result = []
        for r in reviews:
            result.append({
                'id': r.id,
                'product_name': r.product_name,
                'review_text': r.review_text,
                'sentiment': r.sentiment,
                'confidence': r.confidence,
                'key_points': json.loads(r.key_points) if r.key_points else [],
                'created_at': str(r.created_at)
            })
        return result
    except DBAPIError:
        return Response("Database error", status=500)


def call_huggingface_sentiment(text):
    API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
    HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": text})
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            top_sentiment = max(result[0], key=lambda x: x['score'])
            return top_sentiment
    except Exception as e:
        print(f"HF Error: {e}")
    
    return {"label": "neutral", "score": 0.0}

def extract_key_points_gemini(text):
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"Extract 3-5 key points from this product review. Return ONLY a JSON list of strings, for example: [\"point 1\", \"point 2\"]. Do not use markdown code blocks. Review: {text}"
    
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return ["Gagal mengekstrak poin penting"]