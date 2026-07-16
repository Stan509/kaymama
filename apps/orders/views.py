from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from apps.menu.models import Dish, DishVariant
from .models import Order, OrderItem
from decimal import Decimal
import datetime

def cart_detail_view(request):
    cart = request.session.get('cart', {})
    
    # Calculate subtotal
    subtotal = Decimal('0.00')
    for item in cart.values():
        subtotal += Decimal(item['price']) * item['quantity']
        
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'delivery_fee': Decimal('5.00'),
        'total_with_delivery': subtotal + Decimal('5.00'),
    }
    return render(request, 'orders/cart.html', context)


def cart_add_htmx(request, dish_id):
    """Add a dish to the session-based cart. Returns the updated navbar cart counter."""
    dish = get_object_or_404(Dish, id=dish_id)
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant', None)
    
    # Retrieve cart or initialize
    cart = request.session.get('cart', {})
    
    # Generate unique key in cart based on dish + variant
    cart_key = f"{dish_id}_{variant_id}" if variant_id else str(dish_id)
    
    price = dish.price
    variant_name = ""
    if variant_id:
        variant = get_object_or_404(DishVariant, id=variant_id)
        price += variant.additional_price
        variant_name = variant.name
        
    image_url = dish.image.url if dish.image else '/static/img/default-dish.jpg'
    
    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
    else:
        cart[cart_key] = {
            'dish_id': dish.id,
            'name': dish.name,
            'price': str(price),
            'quantity': quantity,
            'variant_id': variant_id,
            'variant_name': variant_name,
            'image_url': image_url,
        }
        
    request.session['cart'] = cart
    request.session.modified = True
    
    total_qty = sum(item['quantity'] for item in cart.values())
    
    # Return updated HTML snippet for cart badge
    return HttpResponse(f"""
        <span id="cart-counter" class="absolute -top-2 -right-2 bg-[#B87333] text-[#F7F3EC] text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center animate-bounce">
            {total_qty}
        </span>
    """)


def cart_remove_htmx(request, cart_key):
    """Remove item from session cart. Returns refreshed cart table partial."""
    cart = request.session.get('cart', {})
    if cart_key in cart:
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
        
    # Re-calculate subtotal
    subtotal = Decimal('0.00')
    for item in cart.values():
        subtotal += Decimal(item['price']) * item['quantity']
        
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'delivery_fee': Decimal('5.00'),
    }
    
    # Trigger event to update the cart badge too (using HX-Trigger header)
    total_qty = sum(item['quantity'] for item in cart.values())
    response = render(request, 'orders/partials/cart_table.html', context)
    response['HX-Trigger'] = f'{{"updateCartBadge": {total_qty}}}'
    return response


def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect('menu:menu')
        
    subtotal = Decimal('0.00')
    for item in cart.values():
        subtotal += Decimal(item['price']) * item['quantity']
        
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        delivery_method = request.POST.get('delivery_method')
        delivery_address = request.POST.get('delivery_address', '')
        delivery_time_str = request.POST.get('delivery_time')
        special_instructions = request.POST.get('special_instructions', '')
        payment_method = request.POST.get('payment_method')
        
        # Verify min 5 dishes for delivery in Cayenne (from flyer)
        total_dishes = sum(item['quantity'] for item in cart.values())
        if delivery_method == Order.DELIVERY_HOME and total_dishes < 5:
            messages.error(request, "La livraison à domicile est disponible à partir de 5 plats minimum (voir flyer).")
            return render(request, 'orders/checkout.html', {
                'cart': cart, 'subtotal': subtotal, 'delivery_fee': Decimal('5.00'), 'total_with_delivery': subtotal + Decimal('5.00')
            })
            
        # Parse delivery time (default to 45 mins from now if empty)
        if delivery_time_str:
            try:
                delivery_time = timezone.make_aware(
                    datetime.datetime.strptime(delivery_time_str, '%Y-%m-%dT%H:%M')
                )
            except ValueError:
                delivery_time = timezone.now() + datetime.timedelta(minutes=45)
        else:
            delivery_time = timezone.now() + datetime.timedelta(minutes=45)
            
        total_price = subtotal
        if delivery_method == Order.DELIVERY_HOME:
            total_price += Decimal('5.00')
            
        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            delivery_method=delivery_method,
            delivery_address=delivery_address if delivery_method == Order.DELIVERY_HOME else "",
            delivery_time=delivery_time,
            special_instructions=special_instructions,
            payment_method=payment_method,
            total_price=total_price,
            status=Order.STATUS_INCOMING,
            payment_status=Order.PAY_STATUS_PENDING,
        )
        
        # Create Order Items
        for cart_key, item in cart.items():
            dish = get_object_or_404(Dish, id=item['dish_id'])
            variant = None
            if item.get('variant_id'):
                variant = get_object_or_404(DishVariant, id=item['variant_id'])
                
            OrderItem.objects.create(
                order=order,
                dish=dish,
                variant=variant,
                quantity=item['quantity'],
                price=Decimal(item['price'])
            )
            
            # Decrease stock level
            dish.stock_level = max(0, dish.stock_level - item['quantity'])
            dish.save()
            
        # If online card payment selected, redirect to payment simulator, else success
        if payment_method == Order.PAY_METHOD_CARD:
            request.session['pending_order_id'] = order.id
            return redirect('payments:checkout')
        else:
            # Cash or Delivery, clear cart and redirect to success
            request.session['cart'] = {}
            request.session.modified = True
            messages.success(request, f"Votre commande {order.order_number} a été validée !")
            return redirect('orders:order_success', order_number=order.order_number)
            
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'delivery_fee': Decimal('5.00'),
        'total_with_delivery': subtotal + Decimal('5.00'),
    }
    return render(request, 'orders/checkout.html', context)


def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/success.html', {'order': order})
