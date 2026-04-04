import torch 
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
from torchvision.transforms import InterpolationMode
from PIL import Image
from transformers import AutoTokenizer
from .model import CLIP
from .config import Config   
import os

class ZeroShotPipeline:

    def __init__(self):
        import os
        self.config = Config
        
        # Get the absolute path to 'DeepLearning/liteCLIP_main/'
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Define absolute paths for the model weights and tokenizer folder
        # This ensures the files are found regardless of where you start the Django server
        model_weights_path = os.path.join(base_path, 'model', 'liteclip2.pt')
        tokenizer_path = os.path.join(base_path, 'model')

        self.model = CLIP(self.config)
        
        # Explicitly load to CPU to prevent hardware errors on your Dell Precision 7550 [cite: 2026-02-17]
        self.model.load_state_dict(torch.load(model_weights_path, map_location='cpu'), strict=False)
        self.model.eval()
        
        # Use local_files_only to skip web validation and stop the "Repo id" error
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
        
        self._img_tfms = T.Compose([
            T.Resize(224, interpolation=InterpolationMode.BICUBIC),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=(0.48145466, 0.4578275, 0.40821073), 
                        std=(0.26862954, 0.26130258, 0.27577711))
        ])

    @torch.no_grad()
    def _prepare_image(self,image):
        try:
            img = Image.open(image).convert('RGB')
        except Exception:
            raise Exception('provide a valid path for the image')
        img = self._img_tfms(img)
        img = torch.unsqueeze(img, 0)

        return img
    
    
    @torch.no_grad()
    def _prepare_text(self,labels):

        text_inputs = self.tokenizer(
        labels,
        padding='max_length',
        truncation=True,
        max_length=self.config.max_length,
        return_tensors='pt'
    )

        return text_inputs

    @torch.no_grad()
    def get_image_features(self, image_path):
        """
        Extracts the final projection vector for an image.
        """
        # 1. Preprocess the image to a tensor
        img = self._prepare_image(image_path).to(next(self.model.parameters()).device)
        
        # 2. Pass through the Image Encoder (Backbone)
        # In your model.py, this is self.image_encoder
        image_features = self.model.image_encoder(img)
        
        # 3. Pass through the Projection Head
        # This is required to align the image math with the text math
        projected_features = self.model.img_projection(image_features)
        
        # 4. Normalize the vector
        # This turns it into a unit vector so Cosine Similarity works correctly
        projected_features = projected_features / projected_features.norm(dim=-1, keepdim=True)
        
        # 5. Convert to list for Django JSON storage
        return projected_features.cpu().numpy().flatten().tolist()
    
    @torch.no_grad()
    def predict(self,image:str, labels: list[str],top_k:int=5):

        assert len(labels) >= 2, "provide atleast 2 labels"

        if len(labels) < top_k:
            top_k = len(labels)

        img = self._prepare_image(image)
        text = self._prepare_text(labels)

        logits,_ = self.model((img,text))
        
        print('logits',logits)
        logits = torch.flatten(logits)
        probabilities = torch.softmax(logits,dim=0)
        values,indices = torch.topk(probabilities,k=top_k)
        values = [v.item() for v in values]
        indices = [i.item() for i in indices]
        
        result = [(labels[i],v) for v,i in zip(values,indices)]

        return result