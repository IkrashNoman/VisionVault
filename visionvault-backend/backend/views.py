from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.base import ContentFile
from django.core.files import File
from .serializers import ImageStoreSerializer, ImageListSerializer, ImageDetailSerializer
from .models import ImageStore, Tag, ImageTag, Caption
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .tag_generation import generator
from .caption_generation import captioner
from .search_functionality import searcher
from .image_generation import image_gen
import logging
import uuid
import requests 
import os   
from django.db import transaction
from rest_framework import status
import gc
import torch

logger = logging.getLogger(__name__)

class ImageListView(ListAPIView):
    queryset = ImageStore.objects.all().order_by('-created_at')
    serializer_class = ImageListSerializer

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
        query = request.query_params.get('q', '').strip()
        # If frontend sends "undefined" string, treat as empty
        if query.lower() == 'undefined':
            query = ''
        page = int(request.query_params.get('page', 1))
        mode = request.query_params.get('mode', 'search')

        if mode == 'suggest':
            return Response(searcher.get_suggestions(query))

        results = []
        
        # 1. DATABASE RESULTS: Only fetched on Page 1 to prevent repeats during scroll
        if page == 1:
            if query:
                vector = searcher.get_text_embedding(query)
                db_matches = searcher.search_database(vector)
                for img, score in db_matches:
                    # Skip records without an actual image file
                    if not img.image_file or not img.image_file.name:
                        continue
                    results.append({
                        "id": str(img.public_id),
                        "src": img.image_file.url,
                        "source": "DATABASE",
                        "tags": [t.name for t in img.tags.all()],
                        "captions": [{"text": c.text} for c in img.captions.all()[:1]]
                    })
            else:
                # Load standard gallery if no query exists
                images = ImageStore.objects.filter(image_file__isnull=False).order_by('-created_at')[:20]
                for img in images:
                    # Additional safety check
                    if not img.image_file or not img.image_file.name:
                        continue
                    results.append({
                        "id": str(img.public_id),
                        "src": img.image_file.url,
                        "source": "DATABASE",
                        "tags": [t.name for t in img.tags.all()],
                        "captions": [{"text": c.text} for c in img.captions.all()[:1]]
                    })

        # 2. WEB RESULTS: Always fetch from Pexels for every page to enable infinite scroll
        web_query = query if query else "photography"
        web_data = searcher.search_web(web_query, page=page, limit=20)
        
        for photo in web_data:
            results.append({
                "id": f"web_{photo['id']}", 
                "src": photo['src']['large2x'],
                "source": "INTERNET",
                "tags": ["Pexels"],
                "captions": [{"text": photo.get('alt', 'Web Result')}]
            })
        
        return Response(results)
          
class ImageDetailView(RetrieveAPIView):
    queryset = ImageStore.objects.all()
    serializer_class = ImageDetailSerializer
    lookup_field = 'public_id'

    def get(self, request, *args, **kwargs):
        # FIX: Check if ID is from the web before Django tries to validate it as a UUID
        lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)

        if str(lookup_value).startswith('web_'):
            return Response({
                "image_file": request.query_params.get('src'),
                "tags": ["Internet", "Pexels"],
                "captions": [{"text": "External Web Image", "score": 1.0}]
            })
        
        return super().get(request, *args, **kwargs)

class SilentUploadView(APIView):
    def post(self, request):
        image_url = request.data.get('image_url')
        raw_external_id = request.data.get('external_id')
        
        if not image_url or not raw_external_id:
            return Response(
                {"error": "Missing fields: 'image_url' and 'external_id' are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent duplicate downloads
        if ImageStore.objects.filter(external_id=raw_external_id).exists():
            return Response(
                {"message": "Already in vault", "public_id": None},
                status=status.HTTP_200_OK
            )

        try:
            # 1. Download image from the web
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # 2. Create DB entry (image_file will be saved after download)
            image_instance = ImageStore.objects.create(
                source='WEB',
                external_id=raw_external_id
            )

            # 3. Save the downloaded content as the image file
            image_instance.image_file.save(
                f"web_{raw_external_id}.jpg",
                ContentFile(response.content),
                save=True
            )

            # 4. --- AI PIPELINE (same as ImageUploadView) ---
            image_path = image_instance.image_file.path
            ai_success = True
            ai_error = None

            try:
                # Generate embedding vector
                vector = generator.get_image_embedding(image_path)
                if vector:
                    image_instance.embedding_vector = vector
                    image_instance.save(update_fields=['embedding_vector'])

                # Generate tags
                predicted_tags = generator.get_image_tags(image_path)
                yolo_list = []
                clip_list = []

                for tag_name, score in predicted_tags.items():
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    ImageTag.objects.create(
                        image=image_instance,
                        tag=tag_obj,
                        confidence_score=score
                    )
                    if score > 0.8:
                        yolo_list.append(tag_name)
                    else:
                        clip_list.append(tag_name)

                # Generate captions
                all_captions = captioner.generate_all_captions(image_path, yolo_list, clip_list)

                # Ensemble ranking (liteCLIP)
                if generator.clip_pipeline is not None and all_captions:
                    rankings = generator.clip_pipeline.predict(image_path, all_captions, top_k=len(all_captions))
                else:
                    rankings = [(text, 0.5) for text in all_captions]

                # Store top 5 captions
                for i, (text, score) in enumerate(rankings[:5]):
                    Caption.objects.create(
                        image=image_instance,
                        text=text,
                        confidence_score=score,
                        is_primary=(i == 0)
                    )

            except Exception as e:
                logger.exception("AI pipeline failed for silent upload")
                ai_success = False
                ai_error = str(e)

            # 5. Return response
            if ai_success:
                return Response(
                    {"message": "Saved with AI insights", "public_id": image_instance.public_id},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        "message": "Image saved but AI pipeline failed",
                        "error": ai_error,
                        "public_id": image_instance.public_id
                    },
                    status=status.HTTP_207_MULTI_STATUS
                )

        except requests.exceptions.Timeout:
            return Response(
                {"error": "Request timed out while fetching the image"},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Failed to fetch image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Unexpected error in SilentUploadView")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    
    
class GenerateAIView(APIView):
    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. TOTAL VRAM PURGE: Move everything else to CPU immediately
            # This is why your requests are failing; the GPU is choking the OS
            if hasattr(generator, 'model'): 
                generator.model.to("cpu")
            if hasattr(captioner, 'model'): 
                captioner.model.to("cpu")
            
            torch.cuda.empty_cache()
            gc.collect()

            # 2. GENERATE: (Forced FP32 VAE prevents black images)
            # This is the 6-minute bottleneck
            file_paths = image_gen.generate(prompt, num_images=2)
            
            if not file_paths:
                return Response({"error": "Model failed to produce output"}, status=500)

            results = []
            # 3. SAVE & ANALYZE: Re-load models to GPU only after generation is done
            if hasattr(generator, 'model'): generator.model.to("cuda")
            if hasattr(captioner, 'model'): captioner.model.to("cuda")

            with transaction.atomic():
                for path in file_paths:
                    with open(path, 'rb') as f:
                        instance = ImageStore.objects.create(
                            source='AI',
                            generation_prompt=prompt
                        )
                        instance.image_file.save(os.path.basename(path), File(f), save=True)

                    image_path = instance.image_file.path
                    
                    # Standard Tagging & Captioning
                    predicted_tags = generator.get_image_tags(image_path)
                    yolo_list, clip_list = [], []
                    for tag_name, score in predicted_tags.items():
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                        ImageTag.objects.create(image=instance, tag=tag_obj, confidence_score=score)
                        if score > 0.8: yolo_list.append(tag_name)
                        else: clip_list.append(tag_name)

                    all_captions = captioner.generate_all_captions(image_path, yolo_list, clip_list)
                    rankings = generator.clip_pipeline.predict(image_path, all_captions, top_k=5) if generator.clip_pipeline else []

                    for i, (text, score) in enumerate(rankings):
                        Caption.objects.create(image=instance, text=text, confidence_score=score, is_primary=(i==0))

                    results.append({
                        "id": str(instance.public_id),
                        "src": instance.image_file.url,
                        "source": "AI",
                        "tags": [t.name for t in instance.tags.all()]
                    })

            return Response(results, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("AI Generation Failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)