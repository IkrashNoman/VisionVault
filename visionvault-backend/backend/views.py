from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import ImageStoreSerializer, ImageListSerializer, ImageDetailSerializer
from .models import ImageStore, Tag, ImageTag, Caption
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .tag_generation import generator

# --- YOUR SIMPLIFIED DL INTEGRATION POINTS ---
def generate_caption(image_path):
    """
    Simulated DL output.
    Returns a single string.
    """
    return "a"


# --- THE UPLOAD VIEW ---

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
    lookup_field = 'public_id'

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        serializer = ImageStoreSerializer(data=request.data)
        
        if serializer.is_valid():
            # 1. Save the image to the database and filesystem
            image_instance = serializer.save()
            image_path = image_instance.image_file.path
            
            try:
                # 2. Run ENHANCED YOLOv8 + WordNet Tagging Pipeline
                # We call the method from the 'generator' instance imported from tag_generation
                predicted_data = generator.get_image_tags(image_path)
                
                for tag_name, score in predicted_data.items():
                    # Get or create the Tag object
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    
                    # Create the relationship link with the specific confidence score
                    ImageTag.objects.create(
                        image=image_instance, 
                        tag=tag_obj, 
                        confidence_score=score 
                    )

                # 3. Run Captioning Pipeline (Currently simulated)
                caption_text = generate_caption(image_path)
                Caption.objects.create(
                    image=image_instance,
                    text=caption_text,
                    is_primary=True
                )

            except Exception as e:
                return Response(
                    {
                        "message": "Image saved successfully, but AI processing failed.",
                        "error": str(e),
                        "data": serializer.data
                    }, 
                    status=status.HTTP_207_MULTI_STATUS
                )

            # Return full success
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)