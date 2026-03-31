from django.urls import path
from .views import ImageUploadView, ImageListView, ImageDetailView

urlpatterns = [
    # POST endpoint for uploading and synchronous DL processing
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    
    # GET endpoint for retrieving the lightweight gallery grid
    path('gallery/', ImageListView.as_view(), name='image-list'),
    
    # GET endpoint for retrieving specific image details (Tags, Captions)
    path('gallery/<uuid:public_id>/', ImageDetailView.as_view(), name='image-detail'),
]