import os
import sys

# ---- Set HF cache directory to D: if available, else C: ----
def _setup_hf_cache():
    # Choose drive: D: if it exists, otherwise C:
    cache_base = "D:\\hf_cache" if os.path.exists("D:") else "C:\\hf_cache"
    os.makedirs(cache_base, exist_ok=True)
    os.environ["HF_HOME"] = cache_base
    os.environ["TRANSFORMERS_CACHE"] = cache_base
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"   
_setup_hf_cache()
# ------------------------------------------------------------

import torch
import nltk
from PIL import Image
from nltk.corpus import wordnet as wn
from ultralytics import YOLO
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

# Import using the full package path (relative to Django project root)
try:
    from backend.DeepLearning.liteCLIP_main.liteclip import ZeroShotPipeline
except ImportError as e:
    logger.error(f"Error loading liteCLIP: {e}")
    ZeroShotPipeline = None

# Initialize NLTK
try:
    wn.ensure_loaded()
except:
    nltk.download('wordnet')
    nltk.download('omw-1.4')


class TagGenerator:
    def __init__(self):
        self.device = "cpu"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 1. YOLOv8
        try:
            yolo_pt = os.path.join(self.base_dir, 'yolov8n.pt')
            self.yolo = YOLO(yolo_pt)
        except Exception as e:
            logger.error(f"Error loading YOLO: {e}")
            self.yolo = None

        # 2. ZERO-SHOT: liteCLIP
        if ZeroShotPipeline is not None:
            try:
                self.clip_pipeline = ZeroShotPipeline()
            except Exception as e:
                logger.error(f"Error initializing liteCLIP: {e}")
                self.clip_pipeline = None
        else:
            self.clip_pipeline = None

        # 3. GENERATIVE: DistilGPT2
        try:
            self.text_gen = pipeline(
            'text-generation',
            model='distilgpt2',
            device=-1,
            model_kwargs={"low_cpu_mem_usage": True}
        )
        except Exception as e:
            logger.error(f"Error loading Generative Model: {e}")
            self.text_gen = None

    def get_dynamic_candidates(self, labels):
        """WordNet-based expansion to avoid hardcoding."""
        candidates = set(labels)
        general_contexts = ["sunny", "gloomy", "vintage", "vibrant", "serene", "coastal"]
        candidates.update(general_contexts)

        for label in labels:
            for syn in wn.synsets(label):
                for lemma in syn.lemmas()[:4]:
                    candidates.add(lemma.name().replace('_', ' '))
        return list(candidates)

    def get_image_tags(self, image_path):
        if not self.yolo:
            return {}

        # A. YOLO Step
        results = self.yolo.predict(source=image_path, imgsz=640, conf=0.4, device='cpu')
        detected_objects = list(set([results[0].names[int(box.cls[0])] for box in results[0].boxes]))

        # B. liteCLIP Step (Contextual Selection)
        clip_tags = []
        if self.clip_pipeline and detected_objects:
            candidates = self.get_dynamic_candidates(detected_objects)
            try:
                predictions = self.clip_pipeline.predict(image_path, candidates, top_k=5)
                clip_tags = [label for label, prob in predictions if prob > 0.15]
            except Exception as e:
                logger.error(f"CLIP prediction failed: {e}")

        # C. Generative AI Step (Transformer Expansion)
        final_results = {obj: 0.95 for obj in detected_objects}

        if self.text_gen and (detected_objects or clip_tags):
            context = ", ".join(set(detected_objects + clip_tags))
            prompt = f"The image features {context}. Generate 5 unique descriptive tags for a photo gallery:"

            try:
                gen_out = self.text_gen(prompt, max_new_tokens=20, do_sample=True, repetition_penalty=1.2)
                raw_text = gen_out[0]['generated_text'].split("tags:")[-1].strip()
                for tag in raw_text.split(','):
                    clean_tag = tag.strip('., ').lower()
                    if 3 < len(clean_tag) < 15 and clean_tag not in final_results:
                        final_results[clean_tag] = 0.85
            except Exception as e:
                logger.error(f"GPT-2 tag generation failed: {e}")

        return final_results

# Global instance used by views.py
generator = TagGenerator()  