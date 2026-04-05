import os
from django.db import models
from PIL import Image
import uuid

class ImageStore(models.Model):
    SOURCE_CHOICES = [('HUMAN', 'Uploaded'), ('AI', 'Generated'), ('WEB', 'Internet')] # Added 'WEB'
    
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # NEW: Store the ID from Pexels/Web to prevent duplicate silent uploads
    external_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    
    # Allow image_file to be null temporarily during web-fetching logic if needed
    image_file = models.ImageField(upload_to='gallery/', width_field='width', height_field='height', null=True, blank=True)
    
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='HUMAN')
    generation_prompt = models.TextField(blank=True, null=True)
    embedding_vector = models.JSONField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', through='ImageTag', related_name='images')

    @property
    def extension(self):
        if self.image_file:
            import os
            return os.path.splitext(self.image_file.name)[1].lower()
        return None

    def __str__(self):
        return f"Image {self.public_id} ({self.source}) - External: {self.external_id}"
    
class Tag(models.Model):
    """
    Supporting 'Automated Image Tagging'[cite: 9, 17, 25].
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ImageTag(models.Model):
    """
    Many-to-Many link for multi-label tagging[cite: 9, 38].
    """
    image = models.ForeignKey(ImageStore, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    confidence_score = models.FloatField() # Metric for evaluation [cite: 12]

class Caption(models.Model):
    image = models.ForeignKey(ImageStore, on_delete=models.CASCADE, related_name='captions')
    text = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True) # CLIP similarity score
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-confidence_score']