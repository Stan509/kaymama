from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EventQuotation
import datetime

def request_quotation_view(request):
    event_choices = EventQuotation.EVENT_CHOICES
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        event_type = request.POST.get('event_type')
        date_str = request.POST.get('event_date')
        guest_count_str = request.POST.get('guest_count')
        notes = request.POST.get('notes')
        
        if not (name and email and phone and event_type and date_str and guest_count_str and notes):
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('events:request_quote')
            
        try:
            event_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            guest_count = int(guest_count_str)
        except ValueError:
            messages.error(request, "Données invalides.")
            return redirect('events:request_quote')
            
        quote = EventQuotation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            phone=phone,
            event_type=event_type,
            event_date=event_date,
            guest_count=guest_count,
            notes=notes
        )
        
        messages.success(request, f"Votre demande de devis pour votre {quote.get_event_type_display().lower()} a bien été enregistrée. Notre équipe vous recontactera sous 24h.")
        return render(request, 'events/success.html', {'quote': quote})
        
    return render(request, 'events/request.html', {'event_choices': event_choices})
