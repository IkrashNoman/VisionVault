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
        # Ensure your .env is loaded in settings.py for this to work
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")

    def get_suggestions(self, query_text):
        if not query_text: return []
        return list(Tag.objects.filter(name__icontains=query_text).values_list('name', flat=True).distinct()[:5])

    def get_text_embedding(self, query_text):
        if not generator.clip_pipeline: return None
        try:
            text_inputs = generator.clip_pipeline._prepare_text([query_text])
            with torch.no_grad():
                text_features = generator.clip_pipeline.model.text_encoder(text_inputs)
                projected_text = generator.clip_pipeline.model.txt_projection(text_features)
                projected_text /= projected_text.norm(dim=-1, keepdim=True)
            return projected_text.cpu().numpy().flatten().tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

    def search_database(self, query_vector):
        if not query_vector: return []
        # Use distinct to prevent duplicate images showing up
        all_images = ImageStore.objects.filter(embedding_vector__isnull=False).distinct()
        results = []
        
        qt = torch.tensor(query_vector)
        for img in all_images:
            iv = torch.tensor(img.embedding_vector)
            sim = torch.nn.functional.cosine_similarity(qt.unsqueeze(0), iv.unsqueeze(0)).item()
            if sim > self.db_threshold:
                results.append((img, sim))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def search_web(self, query_text, page=1, limit=20):
        if not self.pexels_api_key:
            logger.error("PEXELS_API_KEY missing. Images will not show.")
            return []
        try:
            headers = {"Authorization": self.pexels_api_key}
            params = {"query": query_text, "per_page": limit, "page": page}
            res = requests.get(self.web_api_url, headers=headers, params=params, timeout=5)
            return res.json().get('photos', []) if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

searcher = HybridSearcher()