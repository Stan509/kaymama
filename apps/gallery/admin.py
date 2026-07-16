from django.contrib import admin
from .models import PhotoAlbum, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order_index']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PhotoInline]

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'created_at']
    list_filter = ['album']
