# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    credits_remaining = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    images = relationship("ImageMetadata", back_populates="user")
    sessions = relationship("RankingSession", back_populates="user")

class ImageMetadata(Base):
    __tablename__ = "image_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), unique=True)
    filename = Column(String(255))
    file_path = Column(String(500))
    image_type = Column(String(20))  # 'liked' or 'candidate'
    embedding_path = Column(String(500), nullable=True)
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="images")

class RankingSession(Base):
    __tablename__ = "ranking_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    method_used = Column(String(50))
    top_k = Column(Integer)
    diversity_penalty = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    results = relationship("RankingResult", back_populates="session")

class RankingResult(Base):
    __tablename__ = "ranking_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ranking_sessions.id"))
    image_id = Column(Integer, ForeignKey("image_metadata.id"))
    rank = Column(Integer)
    similarity_score = Column(Float)
    
    # Relationships
    session = relationship("RankingSession", back_populates="results")
    image = relationship("ImageMetadata")