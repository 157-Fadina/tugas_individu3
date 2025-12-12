from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from database import Base  

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20))  # POSITIVE, NEGATIVE, NEUTRAL
    confidence = Column(Float)  # 0.0 to 1.0
    key_points = Column(Text)  # Akan disimpan sebagai JSON string
    created_at = Column(DateTime, default=datetime.utcnow)