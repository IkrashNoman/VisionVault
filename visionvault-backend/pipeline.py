import torch
import cv2
import clip
import numpy as np
from PIL import Image
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

# -------------------------
# SETTINGS
# -------------------------
image_path = "D:\\boy.jpg"
sam_checkpoint = "sam_vit_b_01ec64.pth"
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# -------------------------
# LOAD IMAGE
# -------------------------
image_bgr = cv2.imread(image_path)
if image_bgr is None:
    raise FileNotFoundError(f"Cannot find image: {image_path}")
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
image_pil = Image.open(image_path)

# -------------------------
# 1️⃣ SAM - SEGMENTATION
# -------------------------
print("\nLoading SAM (vit_b)...")
sam = sam_model_registry["vit_b"](checkpoint=sam_checkpoint)
sam.to(device)

mask_generator = SamAutomaticMaskGenerator(sam)

print("Generating masks...")
masks = mask_generator.generate(image_rgb)
print("Total segments detected:", len(masks))

# -------------------------
# 2️⃣ CLIP - AUTOMATIC LABELING
# -------------------------
print("\nLoading CLIP...")
clip_model, preprocess = clip.load("ViT-B/32", device=device)

# Load default ImageNet class names for automatic labeling
# (can replace with other vocabularies if desired)
imagenet_classes = []
with open("imagenet_classes.txt", "r") as f:
    imagenet_classes = [line.strip() for line in f.readlines()]

# Crop each SAM mask and classify
object_labels = []
for i, mask_data in enumerate(masks):
    mask = mask_data["segmentation"]
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        continue
    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()
    cropped = image_pil.crop((x1, y1, x2, y2))

    # Preprocess and predict with CLIP
    img_input = preprocess(cropped).unsqueeze(0).to(device)
    text_tokens = clip.tokenize(imagenet_classes).to(device)
    with torch.no_grad():
        image_features = clip_model.encode_image(img_input)
        text_features = clip_model.encode_text(text_tokens)
        similarity = (image_features @ text_features.T).softmax(dim=-1)

    best_idx = similarity.argmax().item()
    label = imagenet_classes[best_idx]
    object_labels.append(label)
    print(f"Object {i+1}: {label}")

# -------------------------
# 3️⃣ ViT-GPT2 CAPTIONING
# -------------------------
print("\nGenerating caption...")
caption_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning").to(device)
caption_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
caption_tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

pixel_values = caption_processor(images=image_pil, return_tensors="pt").pixel_values.to(device)
output_ids = caption_model.generate(pixel_values, max_length=50)
caption = caption_tokenizer.decode(output_ids[0], skip_special_tokens=True)

print("\nGenerated Caption:")
print(caption)

print("\nPipeline Complete ✅")
