# app/image_processor.py
from PIL import Image
import numpy as np
import io
import os
from pathlib import Path
from typing import Tuple, Optional, List
import hashlib
from fastapi import UploadFile

class ImageProcessor:
    def __init__(self):
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        self.max_size = 1024  # Max dimension for thumbnails
    
    async def validate_image(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate if file is a valid image"""
        # Check extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            return False, f"Invalid file type. Allowed: {self.allowed_extensions}"
        
        # Check file size (10MB limit)
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > 10 * 1024 * 1024:
            return False, "File too large. Max 10MB"
        
        # Try to open as image
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            image.verify()
            await file.seek(0)
            return True, "Valid"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    async def process_image(self, file_path: Path, file_id: str, user_id: int, image_type: str):
        """Process and save image metadata"""
        try:
            img = Image.open(file_path)
            width, height = img.size
            
            # Store metadata (would save to database)
            metadata = {
                "file_id": file_id,
                "filename": file_path.name,
                "file_path": str(file_path),
                "image_type": image_type,
                "width": width,
                "height": height,
                "file_size": file_path.stat().st_size,
                "user_id": user_id
            }
            
            print(f"✅ Processed image: {file_path.name}")
            return metadata
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return None
    
    async def create_thumbnail(self, image_path: Path, size: Tuple[int, int] = (200, 200)) -> Path:
        """Create thumbnail of image"""
        img = Image.open(image_path)
        img.thumbnail(size)
        
        thumbnail_path = Path("uploads/thumbnails") / f"thumb_{image_path.name}"
        thumbnail_path.parent.mkdir(exist_ok=True)
        
        img.save(thumbnail_path, "JPEG", quality=85)
        return thumbnail_path
    
    def get_user_images(self, user_id: int, image_type: str) -> List:
        """Get user's images (mock - would query database)"""
        # This would query database
        # For now, return mock data
        return []
    
    def get_image_path(self, image_id: int) -> Optional[Path]:
        """Get image path by ID"""
        # Would query database
        return None
    
    async def save_ranking_session(self, user_id: int, results: List, request) -> str:
        """Save ranking session to database"""
        import uuid
        session_id = str(uuid.uuid4())
        # Would save to database
        return session_id
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        return {
            "total_sessions": 5,
            "total_images": 42,
            "avg_similarity": 0.78,
            "preferred_method": "weighted"
        }
    
    async def get_trending_styles(self) -> List:
        """Get trending visual styles"""
        return [
            {"style": "Minimalist", "count": 1234},
            {"style": "Vintage", "count": 987},
            {"style": "Portrait", "count": 756},
            {"style": "Landscape", "count": 543}
        ]