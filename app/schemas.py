# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_premium: bool
    credits_remaining: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# Image schemas
class UploadResponse(BaseModel):
    success: bool
    files: List[dict]
    message: str

class RankRequest(BaseModel):
    method: Optional[str] = "weighted"
    top_k: Optional[int] = 5
    diversity_penalty: Optional[float] = 0.1

class RankedImage(BaseModel):
    rank: int
    image_id: Optional[int]
    filename: str
    similarity_score: float
    score_percentage: float
    thumbnail_url: Optional[str]

class RankingResponse(BaseModel):
    session_id: str
    ranked_images: List[RankedImage]
    method_used: str
    total_candidates: int

# Analytics schemas
class UserStats(BaseModel):
    total_images: int
    total_sessions: int
    avg_similarity: float
    favorite_method: str