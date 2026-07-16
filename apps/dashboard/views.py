from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from apps.orders.models import Order, OrderItem
from apps.reservations.models import Reservation
from apps.menu.models import Dish
from apps.restaurant.models import RestaurantSettings, OpeningHours
import datetime
from decimal import Decimal

def is_staff_user(user):
    return user.is_authenticated and user.is_staff_member

@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    # Overall metrics
    total_sales = Order.objects.filter(status=Order.STATUS_COMPLETED).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    orders_count = Order.objects.count()
    reservations_count = Reservation.objects.filter(status=Reservation.STATUS_APPROVED).count()
    avg_order_value = Order.objects.filter(status=Order.STATUS_COMPLETED).aggregate(Avg('total_price'))['total_price__avg'] or Decimal('0.00')
    
    # Popular dishes (best sellers)
    best_sellers = OrderItem.objects.values('dish__name', 'dish__price')\
        .annotate(total_qty=Sum('quantity'))\
        .order_by('-total_qty')[:5]
        
    # Recent orders and reservations
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_reservations = Reservation.objects.order_by('-created_at')[:5]
    
    # Sales Chart Data (past 7 days)
    today = datetime.date.today()
    sales_labels = []
    sales_values = []
    
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        sales_labels.append(day.strftime('%d/%m'))
        daily_sum = Order.objects.filter(
            created_at__date=day,
            status=Order.STATUS_COMPLETED
        ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
        sales_values.append(float(daily_sum))
        
    context = {
        'total_sales': total_sales,
        'orders_count': orders_count,
        'reservations_count': reservations_count,
        'avg_order_value': avg_order_value,
        'best_sellers': best_sellers,
        'recent_orders': recent_orders,
        'recent_reservations': recent_reservations,
        'sales_labels': sales_labels,
        'sales_values': sales_values,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
@user_passes_test(is_staff_user)
def reservations_list(request):
    reservations = Reservation.objects.order_by('-date', '-time_slot')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
        
    return render(request, 'dashboard/reservations.html', {
        'reservations': reservations,
        'status_filter': status_filter
    })


@login_required
@user_passes_test(is_staff_user)
def update_reservation_status(request, res_id, status):
    """HTMX status updater for reservations."""
    reservation = get_object_or_404(Reservation, id=res_id)
    if status in [Reservation.STATUS_APPROVED, Reservation.STATUS_REJECTED]:
        reservation.status = status
        reservation.save()
        messages.success(request, f"Réservation de {reservation.first_name} mise à jour : {reservation.get_status_display()}")
        
    if request.headers.get('HX-Request'):
        # Return a partial replacement row or refresh action
        return render(request, 'dashboard/partials/reservation_row.html', {'res': reservation})
        
    return redirect('dashboard:reservations')


@login_required
@user_passes_test(is_staff_user)
def kitchen_screen(request):
    # Kitchen screen shows orders that are INCOMING or PREPARING
    active_orders = Order.objects.filter(
        status__in=[Order.STATUS_INCOMING, Order.STATUS_PREPARING]
    ).prefetch_related('items__dish').order_by('created_at')
    
    # We can filter orders by pickup/delivery too
    return render(request, 'dashboard/kitchen.html', {'orders': active_orders})


@login_required
@user_passes_test(is_staff_user)
def update_order_status_htmx(request, order_id, status):
    """HTMX status updater for kitchen board and manager screen."""
    order = get_object_or_404(Order, id=order_id)
    old_status = order.status
    
    if status in [Order.STATUS_PREPARING, Order.STATUS_READY, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]:
        order.status = status
        # If order is completed or delivered, verify payment status
        if status == Order.STATUS_COMPLETED and order.payment_method in [Order.PAY_METHOD_CASH, Order.PAY_METHOD_DELIVERY]:
            order.payment_status = Order.PAY_STATUS_PAID
        order.save()
        
    if request.headers.get('HX-Request'):
        # If it is the kitchen screen, and the new status is ready/completed (i.e. removed from kitchen board), return empty body to delete it
        if status in [Order.STATUS_READY, Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]:
            return HttpResponse("")
        # Else return refreshed card
        return render(request, 'dashboard/partials/kitchen_card.html', {'order': order})
        
    return redirect('dashboard:kitchen')


@login_required
@user_passes_test(is_staff_user)
def orders_list(request):
    orders = Order.objects.order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    return render(request, 'dashboard/orders.html', {'orders': orders, 'status_filter': status_filter})


@login_required
@user_passes_test(is_staff_user)
def settings_edit(request):
    settings_obj = RestaurantSettings.objects.first()
    hours = OpeningHours.objects.all()
    
    if request.method == 'POST':
        # Update settings
        settings_obj.name = request.POST.get('name', settings_obj.name)
        settings_obj.phone = request.POST.get('phone', settings_obj.phone)
        settings_obj.whatsapp = request.POST.get('whatsapp', settings_obj.whatsapp)
        settings_obj.max_guests_per_slot = int(request.POST.get('max_guests_per_slot', settings_obj.max_guests_per_slot))
        settings_obj.delivery_fee = Decimal(request.POST.get('delivery_fee', settings_obj.delivery_fee))
        settings_obj.is_ordering_enabled = 'is_ordering_enabled' in request.POST
        settings_obj.is_reservations_enabled = 'is_reservations_enabled' in request.POST
        settings_obj.save()
        
        # Update opening hours
        for oh in hours:
            oh.opening_time = request.POST.get(f'open_{oh.day_of_week}') or None
            oh.closing_time = request.POST.get(f'close_{oh.day_of_week}') or None
            oh.is_closed = f'closed_{oh.day_of_week}' in request.POST
            oh.save()
            
        messages.success(request, "Paramètres enregistrés avec succès.")
        return redirect('dashboard:settings')
        
    return render(request, 'dashboard/settings.html', {'settings': settings_obj, 'hours': hours})


@login_required
@user_passes_test(is_staff_user)
def menu_edit(request):
    dishes = Dish.objects.all().select_related('category')
    return render(request, 'dashboard/menu.html', {'dishes': dishes})


@login_required
@user_passes_test(is_staff_user)
def update_dish_stock(request, dish_id):
    """HTMX helper to change availability or stock quickly."""
    dish = get_object_or_404(Dish, id=dish_id)
    if request.method == 'POST':
        stock = request.POST.get('stock')
        if stock is not None:
            dish.stock_level = int(stock)
            dish.is_available = dish.stock_level > 0
            dish.save()
            
        if request.headers.get('HX-Request'):
            return render(request, 'dashboard/partials/menu_row.html', {'dish': dish})
            
    return redirect('dashboard:menu')
