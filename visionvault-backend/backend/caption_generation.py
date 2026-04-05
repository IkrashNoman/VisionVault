import os
import sys

def _setup_hf_cache():
    cache_base = "D:\\hf_cache" if os.path.exists("D:") else "C:\\hf_cache"
    os.makedirs(cache_base, exist_ok=True)
    os.environ["HF_HOME"] = cache_base
    os.environ["TRANSFORMERS_CACHE"] = cache_base
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
_setup_hf_cache()

import re
import logging
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

logger = logging.getLogger(__name__)

class CaptionGenerator:
    def __init__(self):
        logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)
        # Use GPU if available, otherwise CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.blip_model_id = "Salesforce/blip-image-captioning-base"
        
        try:
            self.processor = BlipProcessor.from_pretrained(self.blip_model_id)
            self.model = BlipForConditionalGeneration.from_pretrained(self.blip_model_id).to(self.device)
            logger.info(f"BLIP model loaded on {self.device}")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to load BLIP. Error: {e}")
            self.processor = None
            self.model = None

    def _clean_caption(self, text):
        noise = [r"stock footage", r"getty images", r"shutterstock", r"high quality", r"4k", r"watermark", r"photography of", r"a photography of"]
        for pattern in noise:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        text = " ".join(text.split()).strip(",. ")
        return text.capitalize()

    def generate_all_captions(self, image_path, yolo_tags, clip_tags):
        if not self.processor or not self.model:
            return []
        try:
            raw_image = Image.open(image_path).convert('RGB')
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return []
        
        prompts = ["A photograph of", "An image showing", "A close up of", "A scenic view of", ""]
        try:
            inputs = self.processor(
                images=[raw_image] * len(prompts),
                text=prompts,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            out = self.model.generate(
                **inputs,
                max_new_tokens=30,
                num_beams=3,
                repetition_penalty=1.2
            )
            raw_captions = self.processor.batch_decode(out, skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Caption generation error: {e}")
            return []

        final_list = []
        seen = set()
        for c in raw_captions:
            cleaned = self._clean_caption(c)
            if cleaned and cleaned.lower() not in seen and len(cleaned) > 10:
                final_list.append(cleaned)
                seen.add(cleaned.lower())
        return final_list[:5]

captioner = CaptionGenerator()