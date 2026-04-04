from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.base import ContentFile
from .serializers import ImageStoreSerializer, ImageListSerializer, ImageDetailSerializer
from .models import ImageStore, Tag, ImageTag, Caption
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .tag_generation import generator
from .caption_generation import captioner
from .search_functionality import searcher
import logging
import uuid

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

class ImageSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        mode = request.query_params.get('mode', 'search')

        if mode == 'suggest':
            return Response(searcher.get_suggestions(query))

        if not query:
            return Response([])

        # 1. Local Search
        vector = searcher.get_text_embedding(query)
        db_matches = searcher.search_database(vector)
        
        results = []
        for img, score in db_matches:
            results.append({
                "id": str(img.public_id),
                "src": img.image_file.url,
                "source": "DATABASE",
                "tags": [t.name for t in img.tags.all()],
                "captions": [{"text": c.text} for c in img.captions.all()[:1]]
            })

        # 2. Web Fallback - Force search if under 10 results
        if len(results) < 10:
            web_data = searcher.search_web(query)
            for photo in web_data:
                results.append({
                    "id": str(img.public_id),
                    "src": img.image_file.url, # DRF .url includes the /media/ prefix
                    "source": "DATABASE",
                    "tags": [t.name for t in img.tags.all()],
                    "captions": [{"text": c.text} for c in img.captions.all()[:1]]
                })
        
        return Response(results)

class SilentUploadView(APIView):
    def post(self, request):
        image_url = request.data.get('image_url')
        if not image_url:
            return Response({"error": "No URL provided"}, status=400)

        try:
            # 1. Download the image from the web
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return Response({"error": "Failed to fetch image from web"}, status=400)

            # 2. Create the ImageStore instance
            file_name = f"web_{uuid.uuid4().hex[:8]}.jpg"
            image_instance = ImageStore.objects.create(
                source='AI', # Marking as AI/Web sourced
                generation_prompt=request.data.get('query', 'Web Search')
            )
            
            # Save the downloaded binary content to the ImageField
            image_instance.image_file.save(file_name, ContentFile(response.content), save=True)
            image_path = image_instance.image_file.path

            # 3. TRIGGER AI PIPELINE (Same logic as your Manual Upload)
            # Generate Embedding Vector
            vector = generator.get_image_embedding(image_path)
            if vector:
                image_instance.embedding_vector = vector
                image_instance.save(update_fields=['embedding_vector'])

            # Generate Tags
            predicted_tags = generator.get_image_tags(image_path)
            yolo_list = [name for name, score in predicted_tags.items() if score > 0.8]
            clip_list = [name for name, score in predicted_tags.items() if score <= 0.8]
            
            for tag_name, score in predicted_tags.items():
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                ImageTag.objects.create(image=image_instance, tag=tag_obj, confidence_score=score)

            # Generate Captions
            all_captions = captioner.generate_all_captions(image_path, yolo_list, clip_list)
            
            # Rank and Store Best 5
            if generator.clip_pipeline and all_captions:
                rankings = generator.clip_pipeline.predict(image_path, all_captions, top_k=len(all_captions))
            else:
                rankings = [(text, 0.5) for text in all_captions]

            for i, (text, score) in enumerate(rankings[:5]):
                Caption.objects.create(
                    image=image_instance,
                    text=text,
                    confidence_score=score,
                    is_primary=(i == 0)
                )

            return Response({
                "message": "Silently indexed", 
                "public_id": image_instance.public_id
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)