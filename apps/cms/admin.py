from django.contrib import admin
from .models import PageSection, SEOPageMeta

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ['page', 'section_key', 'title']
    list_filter = ['page']
    search_fields = ['section_key', 'title', 'content']

@admin.register(SEOPageMeta)
class SEOPageMetaAdmin(admin.ModelAdmin):
    list_display = ['path', 'meta_title', 'meta_description']
    search_fields = ['path', 'meta_title']
