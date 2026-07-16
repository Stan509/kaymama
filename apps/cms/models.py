from django.db import models

class PageSection(models.Model):
    PAGE_CHOICES = [
        ('HOME', 'Page d\'accueil'),
        ('ABOUT', 'À propos'),
        ('EVENTS', 'Événements'),
        ('CONTACT', 'Contact'),
    ]

    page = models.CharField(max_length=20, choices=PAGE_CHOICES, default='HOME')
    section_key = models.CharField(max_length=100, unique=True, help_text="Ex: 'hero_title', 'about_chef_description'")
    title = models.CharField(max_length=250, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='cms/', blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = "Section de page"
        verbose_name_plural = "Sections de pages"
        ordering = ['page', 'section_key']

    def __str__(self):
        return f"{self.get_page_display()} - {self.section_key}"

class SEOPageMeta(models.Model):
    path = models.CharField(max_length=250, unique=True, help_text="Ex: '/', '/menu/', '/about/'")
    meta_title = models.CharField(max_length=80, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    og_title = models.CharField(max_length=80, blank=True)
    og_description = models.CharField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)

    class Meta:
        verbose_name = "Métadonnée SEO Page"
        verbose_name_plural = "Métadonnées SEO Pages"

    def __str__(self):
        return self.path
