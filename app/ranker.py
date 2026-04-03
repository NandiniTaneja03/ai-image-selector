# app/ranker.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import pickle
from pathlib import Path

class ImageRanker:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Loading CLIP model on {self.device}...")
        
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.eval()
        
        self.embedding_dim = 512
        self.liked_embeddings = None
        self.weighted_centroid = None
        
        print(f"✅ CLIP model loaded!")
    
    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Extract embedding for a single image"""
        image = Image.open(image_path).convert('RGB')
        
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        
        # Normalize
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy().flatten()
    
    def extract_batch(self, image_paths: List[str]) -> np.ndarray:
        """Extract embeddings for multiple images"""
        embeddings = []
        for path in image_paths:
            try:
                embedding = self.extract_embedding(path)
                embeddings.append(embedding)
            except Exception as e:
                print(f"⚠️ Error processing {path}: {e}")
                embeddings.append(np.zeros(self.embedding_dim))
        
        return np.array(embeddings)
    
    def set_reference(self, liked_image_paths: List[str]):
        """Set reference images (user's liked images)"""
        print(f"📸 Processing {len(liked_image_paths)} liked images...")
        self.liked_embeddings = self.extract_batch(liked_image_paths)
        
        # Compute weighted centroid
        if len(self.liked_embeddings) > 1:
            pairwise_sim = cosine_similarity(self.liked_embeddings)
            np.fill_diagonal(pairwise_sim, 0)
            weights = np.mean(pairwise_sim, axis=1)
            weights = weights / weights.sum()
            self.weighted_centroid = np.average(self.liked_embeddings, axis=0, weights=weights)
        else:
            self.weighted_centroid = np.mean(self.liked_embeddings, axis=0)
        
        print(f"✅ Reference set with {len(liked_image_paths)} images")
    
    def rank_candidates(self, candidate_paths: List[str], top_k: int = 5, 
                       method: str = 'weighted', diversity_penalty: float = 0.1) -> List[Dict]:
        """Rank candidate images based on reference"""
        print(f"🎯 Ranking {len(candidate_paths)} candidate images...")
        
        candidate_embeddings = self.extract_batch(candidate_paths)
        
        # Calculate similarities
        if method == 'weighted':
            similarities = cosine_similarity(candidate_embeddings, self.weighted_centroid.reshape(1, -1)).flatten()
        elif method == 'centroid':
            centroid = np.mean(self.liked_embeddings, axis=0)
            similarities = cosine_similarity(candidate_embeddings, centroid.reshape(1, -1)).flatten()
        elif method == 'avg':
            similarities = cosine_similarity(candidate_embeddings, self.liked_embeddings).mean(axis=1)
        elif method == 'max':
            similarities = cosine_similarity(candidate_embeddings, self.liked_embeddings).max(axis=1)
        else:
            similarities = cosine_similarity(candidate_embeddings, self.weighted_centroid.reshape(1, -1)).flatten()
        
        # Apply diversity penalty
        if diversity_penalty > 0:
            similarities = self._apply_diversity_penalty(candidate_embeddings, similarities, diversity_penalty)
        
        # Get top k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for i, idx in enumerate(top_indices):
            results.append({
                'rank': i + 1,
                'path': candidate_paths[idx],
                'similarity': float(similarities[idx]),
                'score_percentage': float(similarities[idx] * 100)
            })
        
        print(f"✅ Top {top_k} images selected")
        return results
    
    def _apply_diversity_penalty(self, embeddings, similarities, penalty_strength):
        """Apply penalty for diversity"""
        penalized = similarities.copy()
        selected = []
        
        for _ in range(min(5, len(embeddings))):
            best_idx = np.argmax(penalized)
            selected.append(best_idx)
            
            if len(selected) > 1:
                for i in range(len(penalized)):
                    if i not in selected:
                        sim_to_selected = cosine_similarity(
                            embeddings[i].reshape(1, -1),
                            embeddings[selected]
                        ).max()
                        penalized[i] -= penalty_strength * sim_to_selected
        
        return penalized
    
    def explain_ranking(self, candidate_path: str) -> Dict:
        """Explain why an image was ranked highly"""
        embedding = self.extract_embedding(candidate_path)
        similarities = cosine_similarity(embedding.reshape(1, -1), self.liked_embeddings).flatten()
        
        return {
            'max_similarity': float(similarities.max()),
            'avg_similarity': float(similarities.mean()),
            'similarities': similarities.tolist()
        }