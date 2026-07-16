from django.shortcuts import render
from .models import PhotoAlbum, Photo

def gallery_view(request):
    albums = PhotoAlbum.objects.all().prefetch_related('photos')
    photos = Photo.objects.all().select_related('album')
    return render(request, 'gallery/gallery.html', {'albums': albums, 'photos': photos})
