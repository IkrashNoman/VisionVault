from rest_framework import serializers
from .models import ImageStore

class ImageStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageStore
        fields = ['public_id', 'image_file', 'source', 'generation_prompt', 'embedding_vector']
        read_only_fields = ['public_id', 'width', 'height']
        
class ImageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the 'View All' gallery."""
    class Meta:
        model = ImageStore
        # Only send what is necessary to render the grid
        fields = ['public_id', 'image_file', 'created_at'] 

class ImageDetailSerializer(serializers.ModelSerializer):
    """Heavy serializer for the specific image view."""
    tags = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()

    class Meta:
        model = ImageStore
        fields = ['public_id', 'image_file', 'tags', 'caption', 'created_at']

    def get_tags(self, obj):
        # Extracts a flat list of tag strings from the M2M relationship
        return [tag.name for tag in obj.tags.all()]

    def get_caption(self, obj):
        # Retrieves the primary caption text
        caption_obj = obj.captions.filter(is_primary=True).first()
        return caption_obj.text if caption_obj else None