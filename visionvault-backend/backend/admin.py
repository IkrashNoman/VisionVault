from django.contrib import admin
from .models import ImageStore, Tag, ImageTag, Caption

class ImageTagInline(admin.TabularInline):
    model = ImageTag
    extra = 1

class CaptionInline(admin.StackedInline):
    model = Caption
    extra = 1

@admin.register(ImageStore)
class ImageStoreAdmin(admin.ModelAdmin):
    # Changed 'image_extension' to 'extension' (the new @property)
    # Replaced 'id' with 'public_id' to match your updated schema focus
    list_display = ('public_id', 'source', 'extension', 'width', 'height', 'created_at')
    

    list_filter = ('source',) 
    search_fields = ('generation_prompt',)
    
    inlines = [ImageTagInline, CaptionInline]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Caption)
class CaptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'image', 'confidence_score', 'is_primary')