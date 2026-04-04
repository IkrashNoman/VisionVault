from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import ImageStoreSerializer, ImageListSerializer, ImageDetailSerializer
from .models import ImageStore, Tag, ImageTag, Caption
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .tag_generation import generator
from .caption_generation import captioner
import logging

logger = logging.getLogger(__name__)

class ImageListView(ListAPIView):
    queryset = ImageStore.objects.all().order_by('-created_at')
    serializer_class = ImageListSerializer

class ImageDetailView(RetrieveAPIView):
    queryset = ImageStore.objects.all()
    serializer_class = ImageDetailSerializer
    lookup_field = 'public_id'

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ImageStoreSerializer(data=request.data)

        if serializer.is_valid():
            image_instance = serializer.save()
            image_path = image_instance.image_file.path

            try:
                # --- NEW: GENERATE EMBEDDING VECTOR ---
                vector = generator.get_image_embedding(image_path)
                if vector:
                    image_instance.embedding_vector = vector
                    image_instance.save(update_fields=['embedding_vector'])
                # --------------------------------------

                # 1. TAGGING PHASE
                predicted_tags = generator.get_image_tags(image_path)
                yolo_list = []
                clip_list = []

                for tag_name, score in predicted_tags.items():
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    ImageTag.objects.create(image=image_instance, tag=tag_obj, confidence_score=score)

                    if score > 0.8:
                        yolo_list.append(tag_name)
                    else:
                        clip_list.append(tag_name)

                # 2. AUTO-START CAPTIONING PHASE
                all_captions = captioner.generate_all_captions(image_path, yolo_list, clip_list)

                # 3. ENSEMBLE RANKING (liteCLIP)
                if generator.clip_pipeline is not None and all_captions:
                    rankings = generator.clip_pipeline.predict(image_path, all_captions, top_k=len(all_captions))
                else:
                    rankings = [(text, 0.5) for text in all_captions]

                # 4. STORE BEST 5
                for i, (text, score) in enumerate(rankings[:5]):
                    Caption.objects.create(
                        image=image_instance,
                        text=text,
                        confidence_score=score,
                        is_primary=(i == 0)
                    )

            except Exception as e:
                logger.exception("AI pipeline failed")
                return Response(
                    {"message": "Upload successful, but AI pipeline failed.", "error": str(e)},
                    status=status.HTTP_207_MULTI_STATUS
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)