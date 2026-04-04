from django.urls import path
from .views import (
    ImageUploadView, 
    ImageListView, 
    ImageDetailView,
    ImageSearchView,
    SilentUploadView   
)

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    
    path('gallery/', ImageListView.as_view(), name='image-list'),
    path('gallery/<uuid:public_id>/', ImageDetailView.as_view(), name='image-detail'),
    
    path('search/', ImageSearchView.as_view(), name='image-search'),
    path('silent-upload/', SilentUploadView.as_view(), name='silent-upload'),
]