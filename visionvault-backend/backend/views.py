from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import ImageStoreSerializer, ImageListSerializer, ImageDetailSerializer
from .models import ImageStore, Tag, ImageTag, Caption
from rest_framework.generics import ListAPIView, RetrieveAPIView

# --- YOUR SIMPLIFIED DL INTEGRATION POINTS ---

def generate_tags(image_path):
    """
    Simulated DL output. 
    Returns a flat list of strings.
    """
    return ['mountain', 'sun', 'rainbow', 'bike', 'hill']

def generate_caption(image_path):
    """
    Simulated DL output.
    Returns a single string.
    """
    return "A bike on mountain in rainbow, with a sun on the sky"


# --- THE UPLOAD VIEW ---

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ImageStoreSerializer(data=request.data)
        
        if serializer.is_valid():
            image_instance = serializer.save()
            image_path = image_instance.image_file.path
            
            try:
                # 1. Tagging Pipeline
                predicted_tags = generate_tags(image_path)
                
                for tag_name in predicted_tags:
                    # Retrieve existing tag or create a new one
                    tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                    
                    # Hardcode confidence_score to 1.0 to satisfy the database schema
                    ImageTag.objects.create(
                        image=image_instance, 
                        tag=tag_obj, 
                        confidence_score=1.0 
                    )

                # 2. Captioning Pipeline
                caption_text = generate_caption(image_path)
                
                # The Caption model allows confidence_score to be null, so it is omitted.
                Caption.objects.create(
                    image=image_instance,
                    text=caption_text,
                    is_primary=True
                )

            except Exception as e:
                # Catching DL or Database failures
                return Response(
                    {"message": "Image saved, but AI processing failed.", "error": str(e)}, 
                    status=status.HTTP_207_MULTI_STATUS
                )

            # Return success after synchronous processing completes
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageListView(ListAPIView):
    """
    Returns all images for the main gallery.
    """
    queryset = ImageStore.objects.all().order_by('-created_at')
    serializer_class = ImageListSerializer

class ImageDetailView(RetrieveAPIView):
    """
    Returns full details for a single image, looking it up via the UUID.
    """
    queryset = ImageStore.objects.all()
    serializer_class = ImageDetailSerializer
    lookup_field = 'public_id' # Instructs DRF to search using the UUID, not the PK