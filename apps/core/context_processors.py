from apps.restaurant.models import RestaurantSettings, OpeningHours

def global_settings(request):
    try:
        settings_obj = RestaurantSettings.objects.first()
    except Exception:
        settings_obj = None

    try:
        hours = OpeningHours.objects.all()
    except Exception:
        hours = []

    # Calculate cart count from session
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())

    return {
        'restaurant_settings': settings_obj,
        'opening_hours': hours,
        'global_cart_count': cart_count,
    }
