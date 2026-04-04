import torch
import requests
import os
import logging
from .models import ImageStore, Tag
from .tag_generation import generator

logger = logging.getLogger(__name__)

class HybridSearcher:
    def __init__(self):
        self.device = "cpu"
        self.db_threshold = 0.1
        self.web_api_url = "https://api.pexels.com/v1/search"
        
        # Explicitly check for the key
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        
        if not self.pexels_api_key:
            # This will show up in your terminal if the .env failed to load
            logger.error("!!! CRITICAL: PEXELS_API_KEY IS NULL. CHECK YOUR .ENV LOCATION !!!")

    def search_web(self, query_text, limit=15):
        # We check the key again here
        api_key = os.getenv("PEXELS_API_KEY") or self.pexels_api_key
        
        if not api_key:
            return []
            
        try:
            headers = {"Authorization": api_key}
            res = requests.get(
                self.web_api_url, 
                headers=headers, 
                params={"query": query_text, "per_page": limit}, 
                timeout=5
            )
            if res.status_code == 200:
                return res.json().get('photos', [])
            
            logger.error(f"Pexels API Auth Failed: {res.status_code}")
            return []
        except Exception as e:
            logger.error(f"Pexels Request Exception: {e}")
            return []

    def get_suggestions(self, query_text):
        if not query_text: return []
        return list(Tag.objects.filter(name__icontains=query_text).values_list('name', flat=True)[:5])

    def get_text_embedding(self, query_text):
        if not generator.clip_pipeline: 
            logger.error("CRITICAL: CLIP Pipeline not loaded.")
            return None
        try:
            text_inputs = generator.clip_pipeline._prepare_text([query_text])
            with torch.no_grad():
                text_features = generator.clip_pipeline.model.text_encoder(text_inputs)
                projected_text = generator.clip_pipeline.model.txt_projection(text_features)
                projected_text /= projected_text.norm(dim=-1, keepdim=True)
            return projected_text.cpu().numpy().flatten().tolist()
        except Exception as e:
            logger.error(f"Embedding failure: {e}")
            return None

    def search_database(self, query_vector, limit=12):
        if not query_vector: return []
        all_images = ImageStore.objects.filter(embedding_vector__isnull=False)
        results = []
        
        qt = torch.tensor(query_vector)
        for img in all_images:
            iv = torch.tensor(img.embedding_vector)
            sim = torch.nn.functional.cosine_similarity(qt.unsqueeze(0), iv.unsqueeze(0)).item()
            if sim > self.db_threshold:
                results.append((img, sim))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

searcher = HybridSearcher()