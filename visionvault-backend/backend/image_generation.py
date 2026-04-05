import os

def _setup_hf_cache():
    cache_base = "D:\\hf_cache" if os.path.exists("D:") else "C:\\hf_cache"
    os.makedirs(cache_base, exist_ok=True)
    os.environ["HF_HOME"] = cache_base
    os.environ["TRANSFORMERS_CACHE"] = cache_base
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
_setup_hf_cache()

import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
import uuid
import gc

class ImageGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self._load_model()

    def _load_model(self):
        print(f"🚀 Loading SDXL-Lightning on {self.device}...")
        
        # Base SDXL model
        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        # Use the 4-step UNet checkpoint for optimal speed/quality
        ckpt = "sdxl_lightning_4step_unet.safetensors"
        
        # Load UNet with custom checkpoint
        unet = UNet2DConditionModel.from_config(base, subfolder="unet").to(self.device, torch.float16)
        unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))
        
        # Load the pipeline
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            base, unet=unet, torch_dtype=torch.float16, variant="fp16"
        ).to(self.device)
        
        # Ensure sampler uses "trailing" timesteps
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(
            self.pipe.scheduler.config, timestep_spacing="trailing"
        )
        
        # Memory optimizations for 4GB GPU
        if self.device == "cuda":
            self.pipe.enable_attention_slicing()
            self.pipe.enable_vae_slicing()
        
        print("✅ SDXL-Lightning ready.")

    def generate(self, prompt, num_images=2):
        if not self.pipe:
            return []
        
        # Lightning model: 4 steps, CFG = 0
        num_inference_steps = 4
        guidance_scale = 0.0

        output_dir = "media/generated/"
        os.makedirs(output_dir, exist_ok=True)

        enhanced_prompt = f"masterpiece, best quality, {prompt}"
        negative_prompt = "worst quality, low quality, ugly, deformed"

        generated_paths = []
        for i in range(num_images):
            print(f"🖌️ Generating {i+1}/{num_images}...")
            image = self.pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                height=1024,
                width=1024,
            ).images[0]
            fname = f"ai_{uuid.uuid4()}.jpg"
            path = os.path.join(output_dir, fname)
            image.save(path)
            generated_paths.append(path)
            print(f"✅ Saved: {path}")
            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()
        return generated_paths

image_gen = ImageGenerator()