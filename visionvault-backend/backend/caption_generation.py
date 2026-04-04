import os
import sys

# ---- Set HF cache directory to D: if available, else C: ----
def _setup_hf_cache():
    cache_base = "D:\\hf_cache" if os.path.exists("D:") else "C:\\hf_cache"
    os.makedirs(cache_base, exist_ok=True)
    os.environ["HF_HOME"] = cache_base
    os.environ["TRANSFORMERS_CACHE"] = cache_base
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"   
_setup_hf_cache()
# ------------------------------------------------------------

import os
import re
import logging
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

logger = logging.getLogger(__name__)

class CaptionGenerator:
    def __init__(self):
        logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)
        self.device = "cpu"
        self.blip_model_id = "Salesforce/blip-image-captioning-base"
        
        try:
            self.processor = BlipProcessor.from_pretrained(self.blip_model_id)
            self.model = BlipForConditionalGeneration.from_pretrained(self.blip_model_id).to(self.device)
            logger.info("BLIP model loaded successfully.")
        except Exception as e:
            # If the model fails to load, the system is fundamentally broken. Log as critical.
            logger.critical(f"CRITICAL: Failed to load BLIP natively. Captioning offline. Error: {e}")
            self.processor = None
            self.model = None

    def _clean_caption(self, text):
        noise = [
            r"stock footage", r"getty images", r"shutterstock", 
            r"high quality", r"4k", r"watermark", r"photography of", r"a photography of"
        ]
        for pattern in noise:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        text = " ".join(text.split()).strip(",. ")
        return text.capitalize()

    def generate_all_captions(self, image_path, yolo_tags, clip_tags):
        if not self.processor or not self.model:
            logger.error("Skipping caption generation: BLIP model is not initialized.")
            return []

        # Point of Failure 1: Corrupt or missing image files
        try:
            raw_image = Image.open(image_path).convert('RGB')
        except Exception as e:
            logger.error(f"Failed to load or convert image at {image_path}. Error: {e}")
            return []
        
        prompts = [
            "A photograph of",
            "An image showing",
            "A close up of",
            "A scenic view of",
            "" 
        ]

        # Point of Failure 2: OOM (Out of Memory) and Tensor Mismatches
        try:
            inputs = self.processor(
                images=[raw_image] * len(prompts), 
                text=prompts, 
                return_tensors="pt",
                padding=True  # Retaining the required fix
            ).to(self.device)

            out = self.model.generate(
                **inputs, 
                max_new_tokens=30,
                num_beams=3,
                repetition_penalty=1.2
            )

            raw_captions = self.processor.batch_decode(out, skip_special_tokens=True)
            
        except RuntimeError as e:
            # PyTorch frequently throws RuntimeErrors for memory exhaustion
            logger.error(f"Runtime/Memory error during BLIP inference for {image_path}: {e}")
            return []
        except Exception as e:
            # Catch-all for unexpected pipeline failures, forcing full traceback to logs
            logger.error(f"Unexpected pipeline failure during BLIP generation for {image_path}: {e}", exc_info=True)
            return []

        # Final Cleaning & Deduplication (Safe logic, no external dependencies)
        final_list = []
        seen = set()
        
        for c in raw_captions:
            cleaned = self._clean_caption(c)
            if cleaned and cleaned.lower() not in seen and len(cleaned) > 10:
                final_list.append(cleaned)
                seen.add(cleaned.lower())
        
        return final_list[:5]

captioner = CaptionGenerator()