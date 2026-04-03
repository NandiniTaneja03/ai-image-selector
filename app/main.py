# app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import shutil
import os
import uuid
from pathlib import Path
import asyncio
from datetime import datetime
import pickle

from app.models import User, RankingSession, ImageMetadata
from app.schemas import (
    UploadResponse, RankingResponse, RankRequest,
    UserCreate, UserResponse, Token
)
from app.image_processor import ImageProcessor
from app.ranker import ImageRanker
from app.auth import AuthHandler, get_current_user

# Initialize
app = FastAPI(title="AI Image Selector API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
image_processor = ImageProcessor()
auth_handler = AuthHandler()
ranker = ImageRanker()

# Directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ============ Health Check ============
@app.get("/")
async def root():
    return {"message": "AI Image Selector API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "online", "timestamp": datetime.now().isoformat()}

# ============ Authentication ============
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register new user"""
    return auth_handler.register(user)

@app.post("/api/auth/login", response_model=Token)
async def login(username: str, password: str):
    """Login user"""
    return auth_handler.login(username, password)

# ============ Image Upload & Processing ============
@app.post("/api/upload/liked", response_model=UploadResponse)
async def upload_liked_images(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload liked/reference images"""
    uploaded_files = []
    
    for file in files:
        # Validate image
        is_valid, error = await image_processor.validate_image(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid image: {error}")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process in background
        background_tasks.add_task(
            image_processor.process_image,
            file_path, file_id, current_user.id, "liked"
        )
        
        uploaded_files.append({
            "id": file_id,
            "filename": file.filename,
            "path": str(file_path)
        })
    
    return UploadResponse(
        success=True,
        files=uploaded_files,
        message=f"Uploaded {len(uploaded_files)} liked images"
    )

@app.post("/api/upload/candidates", response_model=UploadResponse)
async def upload_candidate_images(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload candidate images to select from"""
    uploaded_files = []
    
    for file in files:
        # Validate image
        is_valid, error = await image_processor.validate_image(file)
        if not is_valid:
            continue  # Skip invalid images
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process in background
        background_tasks.add_task(
            image_processor.process_image,
            file_path, file_id, current_user.id, "candidate"
        )
        
        uploaded_files.append({
            "id": file_id,
            "filename": file.filename,
            "path": str(file_path)
        })
    
    return UploadResponse(
        success=True,
        files=uploaded_files,
        message=f"Uploaded {len(uploaded_files)} candidate images"
    )

# ============ Ranking ============
@app.post("/api/rank", response_model=RankingResponse)
async def rank_images(
    request: RankRequest,
    current_user: User = Depends(get_current_user)
):
    """Rank candidate images based on liked images"""
    try:
        # Get user's liked images
        liked_images = image_processor.get_user_images(current_user.id, "liked")
        if len(liked_images) < 3:
            raise HTTPException(
                status_code=400,
                detail="Need at least 3 liked images for accurate ranking"
            )
        
        # Get candidate images
        candidate_images = image_processor.get_user_images(current_user.id, "candidate")
        if not candidate_images:
            raise HTTPException(
                status_code=400,
                detail="No candidate images found"
            )
        
        # Set reference
        ranker.set_reference([img.path for img in liked_images])
        
        # Rank candidates
        results = ranker.rank_candidates(
            [img.path for img in candidate_images],
            top_k=request.top_k or 5,
            method=request.method or "weighted",
            diversity_penalty=request.diversity_penalty or 0.1
        )
        
        # Save results to database
        session_id = await image_processor.save_ranking_session(
            current_user.id, results, request
        )
        
        # Prepare response
        ranked_images = []
        for result in results:
            # Find original image metadata
            original = next(
                (img for img in candidate_images if img.path == result['path']),
                None
            )
            
            ranked_images.append({
                "rank": result['rank'],
                "image_id": original.id if original else None,
                "filename": Path(result['path']).name,
                "similarity_score": result['similarity'],
                "score_percentage": result['score_percentage'],
                "thumbnail_url": f"/api/images/thumbnail/{original.id}" if original else None
            })
        
        return RankingResponse(
            session_id=session_id,
            ranked_images=ranked_images,
            method_used=request.method or "weighted",
            total_candidates=len(candidate_images)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Image Serving ============
@app.get("/api/images/thumbnail/{image_id}")
async def get_thumbnail(image_id: int):
    """Get image thumbnail"""
    image_path = image_processor.get_image_path(image_id)
    if not image_path:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Generate thumbnail
    thumbnail = await image_processor.create_thumbnail(image_path)
    return FileResponse(thumbnail, media_type="image/jpeg")

# ============ Analytics ============
@app.get("/api/analytics/user")
async def get_user_analytics(current_user: User = Depends(get_current_user)):
    """Get user analytics"""
    stats = await image_processor.get_user_stats(current_user.id)
    return stats

@app.get("/api/analytics/trends")
async def get_trending_styles():
    """Get trending visual styles"""
    trends = await image_processor.get_trending_styles()
    return {"trends": trends}