import nltk
from nltk.corpus import wordnet as wn
from ultralytics import YOLO
import os

# Initialize NLTK assets
try:
    wn.ensure_loaded()
except:
    nltk.download('wordnet')
    nltk.download('omw-1.4')

class TagGenerator:
    def __init__(self):
        # Load model once at initialization
        try:
            self.model = YOLO('yolov8n.pt')
        except Exception as e:
            print(f"Error loading YOLO: {e}")
            self.model = None
            
        # Define the hypernym categories for grouping
        self.target_categories = ['vehicle', 'furniture', 'clothing', 'animal', 'appliance', 'structure']

    def get_general_category(self, word):
        """Finds broader categories using Hypernym Tree Traversal."""
        synsets = wn.synsets(word, pos=wn.NOUN)
        if not synsets:
            return None
        
        for syn in synsets:
            # Closure follows the 'is-a' relationship up the tree
            for hyper in syn.closure(lambda s: s.hypernyms()):
                name = hyper.lemma_names()[0].lower().replace('_', ' ')
                if name in self.target_categories:
                    return name
        return None

    def get_image_tags(self, image_path):
        """Combined DL Inference and Semantic Processing Pipeline."""
        if self.model is None:
            return {}

        # 1. ENHANCED DL INFERENCE
        results = self.model.predict(
            source=image_path,
            imgsz=640,      # Spatial consistency
            augment=True,   # TTA for robustness
            iou=0.45,       # NMS tuning to reduce duplicates
            conf=0.4,       # Confidence filtering
            device='cpu'
        )
        
        final_tags = {}
        
        for result in results:
            names = result.names
            for box in result.boxes:
                label = names[int(box.cls[0])].lower().replace('_', ' ')
                score = float(box.conf[0])
                
                # 2. BASE TAG CLEANING
                final_tags[label] = max(final_tags.get(label, 0), score)

                # 3. SEMANTIC INTELLIGENCE (WordNet)
                category = self.get_general_category(label)
                if category and category != label:
                    # Categorize automatically (e.g., 'car' -> 'vehicle')
                    # We use a slightly lower confidence (0.9 multiplier) for inferred tags
                    final_tags[category] = max(final_tags.get(category, 0), score * 0.9)
                
        return final_tags

# Global instance for use in Django Views
generator = TagGenerator()