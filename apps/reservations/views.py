from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import Reservation
from apps.restaurant.models import RestaurantSettings, OpeningHours, BlockedDate
import datetime

def reserve_table_view(request):
    settings_obj = RestaurantSettings.objects.first()
    occasions = Reservation.OCCASION_CHOICES
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time_slot')
        guest_count_str = request.POST.get('guest_count')
        occasion = request.POST.get('occasion', Reservation.OCCASION_OTHER)
        notes = request.POST.get('notes', '')
        
        # 1. Validation
        if not (first_name and last_name and email and phone and date_str and time_str and guest_count_str):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('reservations:book')
            
        try:
            res_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            res_time = datetime.datetime.strptime(time_str, '%H:%M').time()
            guest_count = int(guest_count_str)
        except ValueError:
            messages.error(request, "Format de date ou d'heure invalide.")
            return redirect('reservations:book')
            
        # 2. Blocked dates check
        if BlockedDate.objects.filter(date=res_date).exists():
            blocked = BlockedDate.objects.get(date=res_date)
            messages.error(request, f"Le restaurant est exceptionnellement fermé ce jour-là : {blocked.reason or 'Jour férié'}")
            return redirect('reservations:book')
            
        # 3. Opening hours check
        # Django weekday: 0 is Monday, 6 is Sunday (Python weekday is also 0-6)
        weekday = res_date.weekday()
        try:
            hours = OpeningHours.objects.get(day_of_week=weekday)
            if hours.is_closed:
                messages.error(request, "Le restaurant est fermé ce jour de la semaine.")
                return redirect('reservations:book')
            
            # Check if time is within open slots
            if hours.opening_time and hours.closing_time:
                if not (hours.opening_time <= res_time <= hours.closing_time):
                    messages.error(request, f"Le restaurant est ouvert de {hours.opening_time.strftime('%H:%M')} à {hours.closing_time.strftime('%H:%M')}.")
                    return redirect('reservations:book')
        except OpeningHours.DoesNotExist:
            pass # No rules set, default allow
            
        # 4. Slot availability check
        max_guests = settings_obj.max_guests_per_slot if settings_obj else 30
        reserved_guests = Reservation.objects.filter(
            date=res_date,
            time_slot=res_time,
            status__in=[Reservation.STATUS_APPROVED, Reservation.STATUS_PENDING, Reservation.STATUS_MODIFIED]
        ).aggregate(Sum('guest_count'))['guest_count__sum'] or 0
        
        if reserved_guests + guest_count > max_guests:
            messages.error(request, f"Désolé, il ne reste plus que {max(0, max_guests - reserved_guests)} places disponibles pour ce créneau horaire.")
            return redirect('reservations:book')
            
        # 5. Create reservation
        reservation = Reservation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date=res_date,
            time_slot=res_time,
            guest_count=guest_count,
            occasion=occasion,
            notes=notes,
            status=Reservation.STATUS_PENDING
        )
        
        messages.success(request, f"Votre demande de réservation pour le {res_date.strftime('%d/%m/%Y')} à {res_time.strftime('%H:%M')} a bien été reçue. Vous recevrez un e-mail de confirmation.")
        return redirect('reservations:success', reservation_id=reservation.id)
        
    return render(request, 'reservations/book.html', {'occasions': occasions})


def reservation_success_view(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    return render(request, 'reservations/success.html', {'reservation': reservation})
