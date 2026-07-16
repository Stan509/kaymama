from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.orders.models import Order

def payment_checkout_view(request):
    order_id = request.session.get('pending_order_id')
    if not order_id:
        return redirect('menu:menu')
        
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Simulate success
        order.payment_status = Order.PAY_STATUS_PAID
        order.save()
        
        # Clear cart session
        request.session['cart'] = {}
        request.session.modified = True
        
        # Remove pending order flag
        try:
            del request.session['pending_order_id']
        except KeyError:
            pass
            
        messages.success(request, f"Paiement en ligne accepté. Commande {order.order_number} transmise en cuisine !")
        return redirect('orders:order_success', order_number=order.order_number)
        
    return render(request, 'payments/simulator.html', {'order': order})
