import os
import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler, AutoencoderKL
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
import uuid
import gc

def _setup_hf_cache():
    cache_base = "D:\\hf_cache" if os.path.exists("D:") else "C:\\hf_cache"
    os.makedirs(cache_base, exist_ok=True)
    os.environ["HF_HOME"] = cache_base
_setup_hf_cache()

class ImageGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self._load_model()

    def _load_model(self):
        print(f"🚀 Loading SDXL-Lightning on {self.device}...")
        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        ckpt = "sdxl_lightning_4step_unet.safetensors"
        
        # 1. Load UNet in fp16
        unet = UNet2DConditionModel.from_config(base, subfolder="unet").to(self.device, dtype=torch.float16)
        unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device=self.device))
        
        # 2. BLACK IMAGE KILLER: Force VAE to float32
        vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float32).to(self.device)
        
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            base, unet=unet, vae=vae, torch_dtype=torch.float16, variant="fp16"
        )

        # 3. Disable Safety Checker (often causes false-positive black images)
        self.pipe.safety_checker = None
        self.pipe.requires_safety_checker = False

        self.pipe.scheduler = EulerDiscreteScheduler.from_config(
            self.pipe.scheduler.config, timestep_spacing="trailing"
        )
        
        # 4. Laptop Optimizations
        self.pipe.enable_model_cpu_offload() 
        self.pipe.enable_vae_tiling()
        print("✅ SDXL-Lightning ready. VAE stabilized in FP32.")

    def generate(self, prompt, num_images=2):
        if not self.pipe: return []
        output_dir = "media/generated/"
        os.makedirs(output_dir, exist_ok=True)
        
        enhanced_prompt = f"{prompt}, masterpiece, 8k, photorealistic, highly detailed"
        generated_paths = []

        for i in range(num_images):
            try:
                with torch.inference_mode():
                    # Generate latents first
                    latents = self.pipe(
                        prompt=enhanced_prompt,
                        num_inference_steps=4,
                        guidance_scale=0.0,
                        output_type="latent"
                    ).images

                    # Decode manually in FP32 to ensure no black pixels
                    image = self.pipe.vae.decode(latents.to(torch.float32) / self.pipe.vae.config.scaling_factor, return_dict=False)[0]
                    image = self.pipe.image_processor.postprocess(image, output_type="pil")[0]

                path = os.path.join(output_dir, f"ai_{uuid.uuid4()}.jpg")
                image.save(path)
                generated_paths.append(path)
            except Exception as e:
                print(f"❌ Generation error: {e}")
            
            gc.collect()
            torch.cuda.empty_cache()
            
        return generated_paths

image_gen = ImageGenerator()