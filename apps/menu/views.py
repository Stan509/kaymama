from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import Category, Dish

def menu_view(request):
    categories = Category.objects.filter(is_active=True).order_by('order_index')
    
    # Get active/selected category (default is all or the first category)
    selected_cat_slug = request.GET.get('category', '')
    query = request.GET.get('q', '')
    
    dishes = Dish.objects.filter(is_available=True)
    if selected_cat_slug:
        dishes = dishes.filter(category__slug=selected_cat_slug)
    if query:
        dishes = dishes.filter(Q(name__icontains=query) | Q(description__icontains=query))
        
    context = {
        'categories': categories,
        'selected_category_slug': selected_cat_slug,
        'dishes': dishes,
        'query': query,
    }
    return render(request, 'menu/menu.html', context)


def menu_items_htmx(request):
    """Partial HTML endpoint for HTMX requests to filter menu items on the fly."""
    selected_cat_slug = request.GET.get('category', '')
    query = request.GET.get('q', '')
    
    dishes = Dish.objects.filter(is_available=True)
    if selected_cat_slug:
        dishes = dishes.filter(category__slug=selected_cat_slug)
    if query:
        dishes = dishes.filter(Q(name__icontains=query) | Q(description__icontains=query))
        
    return render(request, 'menu/partials/dish_grid.html', {'dishes': dishes})


@login_required
def toggle_favorite(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    user = request.user
    if user.favorites.filter(id=dish.id).exists():
        user.favorites.remove(dish)
        favorited = False
    else:
        user.favorites.add(dish)
        favorited = True
        
    # Check if HTMX request
    if request.headers.get('HX-Request'):
        # Return a partial heart icon representing the status
        color = "text-[#B87333] fill-[#B87333]" if favorited else "text-[#0F2B46]/40 hover:text-[#B87333]"
        icon = f"""
        <button hx-post="/menu/favorite/{dish.id}/" hx-swap="outerHTML" class="focus:outline-none transition {color}">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
        </button>
        """
        return HttpResponse(icon)
        
    return redirect('menu:menu')
