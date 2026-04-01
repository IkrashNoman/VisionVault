from rest_framework import serializers
from .models import ImageStore

class ImageStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageStore
        fields = ['public_id', 'image_file', 'source', 'generation_prompt', 'embedding_vector']
        read_only_fields = ['public_id', 'width', 'height', 'embedding_vector', 'tags']

class ImageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the 'View All' gallery."""
    class Meta:
        model = ImageStore
        # Only send what is necessary to render the grid
        fields = ['public_id', 'image_file', 'created_at'] 

class ImageDetailSerializer(serializers.ModelSerializer):
    """Heavy serializer for the specific image view including top 5 captions."""
    tags = serializers.SerializerMethodField()
    captions = serializers.SerializerMethodField() # Changed from single 'caption'

    class Meta:
        model = ImageStore
        fields = ['public_id', 'image_file', 'tags', 'captions', 'created_at']

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_captions(self, obj):
        # Returns the top 5 captions based on the ordering defined in the model
        return [
            {"text": c.text, "score": c.confidence_score, "is_primary": c.is_primary} 
            for c in obj.captions.all()[:5]
        ]