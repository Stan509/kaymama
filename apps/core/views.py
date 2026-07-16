from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from apps.cms.models import PageSection
from apps.menu.models import Dish
from apps.blog.models import BlogPost
from apps.gallery.models import Photo
from apps.reservations.models import Reservation
import datetime

def home_view(request):
    # Fetch sections
    sections_qs = PageSection.objects.filter(page='HOME')
    sections = {sec.section_key: sec for sec in sections_qs}
    
    # Specialty dishes (featured on homepage)
    specialties = Dish.objects.filter(is_specialty=True, is_available=True)[:3]
    if not specialties.exists():
        specialties = Dish.objects.filter(is_available=True)[:3]
        
    # Latest 2 blog posts
    latest_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:2]
    
    # Showcase photos for landing page
    photos = Photo.objects.all()[:4]
    
    context = {
        'sections': sections,
        'specialties': specialties,
        'latest_posts': latest_posts,
        'photos': photos,
    }
    return render(request, 'core/home.html', context)


def salon_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time_slot')
        service = request.POST.get('service', 'Coiffure & Tressage')
        notes = request.POST.get('notes', '')
        
        if not (first_name and last_name and email and phone and date_str and time_str):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('core:salon')
            
        try:
            res_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            res_time = datetime.datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, "Format de date ou d'heure invalide.")
            return redirect('core:salon')
            
        reservation = Reservation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date=res_date,
            time_slot=res_time,
            guest_count=1,
            occasion=Reservation.OCCASION_SALON,
            notes=f"Prestation demandée: {service}\n{notes}".strip(),
            status=Reservation.STATUS_PENDING
        )
        
        messages.success(request, f"Votre demande de rendez-vous pour le {res_date.strftime('%d/%m/%Y')} à {res_time.strftime('%H:%M')} a bien été reçue. Un email de confirmation vous sera envoyé.")
        return redirect('reservations:success', reservation_id=reservation.id)
        
    return render(request, 'core/salon.html')


def about_view(request):
    about_sections = {sec.section_key: sec for sec in PageSection.objects.filter(page='ABOUT')}
    return render(request, 'core/about.html', {'sections': about_sections})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # In a real app we'd send an email here
        messages.success(request, f"Merci {name}, votre message a été envoyé avec succès. Nous vous répondrons dès que possible.")
        return redirect('core:contact')
        
    return render(request, 'core/contact.html')


# PWA & SEO Routes
def robots_txt(request):
    content = """User-agent: *
Allow: /
Sitemap: http://localhost:8000/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    # Retrieve base domain from request host header
    domain = request.get_host()
    protocol = "https" if request.is_secure() else "http"
    
    static_urls = [
        '/',
        '/menu/',
        '/reservations/book/',
        '/events/request/',
        '/about/',
        '/contact/',
        '/blog/',
        '/gallery/',
    ]
    
    sitemap_items = []
    # Add static pages
    for url in static_urls:
        sitemap_items.append(f"{protocol}://{domain}{url}")
        
    # Add blog posts
    posts = BlogPost.objects.filter(is_published=True)
    for post in posts:
        sitemap_items.append(f"{protocol}://{domain}/blog/{post.slug}/")
        
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc in sitemap_items:
        xml_content += f'  <url>\n    <loc>{loc}</loc>\n    <changefreq>daily</changefreq>\n  </url>\n'
    xml_content += '</urlset>'
    
    return HttpResponse(xml_content, content_type="application/xml")


def pwa_manifest(request):
    manifest_data = {
        "name": "Kay Mama Cuisine Créole",
        "short_name": "Kay Mama",
        "description": "L'authenticité créole à chaque bouchée. Restaurant créole à Cayenne.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#F7F3EC",
        "theme_color": "#0F2B46",
        "icons": [
            {
                "src": "/static/img/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/img/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest_data)


def pwa_service_worker(request):
    worker_js = """
const CACHE_NAME = 'kay-mama-v1';
const ASSETS = [
  '/',
  '/static/css/custom.css',
  'https://cdn.tailwindcss.com',
  'https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js',
  'https://unpkg.com/htmx.org@1.9.10',
  'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js',
  'https://unpkg.com/aos@next/dist/aos.css',
  'https://unpkg.com/aos@next/dist/aos.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      return cachedResponse || fetch(e.request);
    })
  );
});
"""
    return HttpResponse(worker_js, content_type="application/javascript")
