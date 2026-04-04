import os
import django

# 1. Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visionvault_backend.settings') # Change 'your_project_name'
django.setup()

from backend.models import ImageStore
from backend.tag_generation import generator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backfill_vectors():
    # Fetch only images where embedding_vector is null
    images_to_process = ImageStore.objects.filter(embedding_vector__isnull=True)
    
    total = images_to_process.count()
    if total == 0:
        logger.info("No images found with null embedding vectors.")
        return

    logger.info(f"Starting backfill for {total} images...")

    success_count = 0
    for i, image_instance in enumerate(images_to_process):
        try:
            image_path = image_instance.image_file.path
            
            if not os.path.exists(image_path):
                logger.warning(f"File missing: {image_path}. Skipping.")
                continue

            # Generate vector using the new method in TagGenerator
            vector = generator.get_image_embedding(image_path)
            
            if vector:
                image_instance.embedding_vector = vector
                # Use update_fields for efficiency and to avoid overwriting other changes
                image_instance.save(update_fields=['embedding_vector'])
                success_count += 1
                logger.info(f"[{i+1}/{total}] Success: {image_instance.public_id}")
            else:
                logger.error(f"[{i+1}/{total}] Failed to generate vector for {image_instance.public_id}")

        except Exception as e:
            logger.error(f"Error processing image {image_instance.pk}: {e}")

    logger.info(f"Backfill complete. Successfully updated {success_count} out of {total} images.")

if __name__ == "__main__":
    backfill_vectors()