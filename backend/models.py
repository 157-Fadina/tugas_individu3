from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from database import Base  

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20)) 
    confidence = Column(Float)  
    key_points = Column(Text)  
    created_at = Column(DateTime, default=datetime.utcnow)