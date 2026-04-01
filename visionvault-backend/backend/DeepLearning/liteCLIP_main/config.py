import os
from dataclasses import dataclass

@dataclass
class Config:
    # Get the directory where this config.py file resides
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the folder containing tokenizer and model configuration files
    text_encoder = os.path.join(base_dir, 'model')

    # Image encoder name (timm model name)
    image_encoder = 'convnext_tiny'

    # CLIP CONFIG
    proj_dim = 256
    dropout = 0.1
    max_length = 128

    # Path to the trained model weights
    state_dict_path = os.path.join(base_dir, 'model', 'liteclip2.pt')