from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User
from apps.orders.models import Order
from apps.reservations.models import Reservation

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'
    }), label="Mot de passe")
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'
    }), label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]'}),
            'address': forms.Textarea(attrs={'class': 'w-full bg-[#F7F3EC]/50 border border-[#0F2B46]/20 rounded-xl px-4 py-3 text-[#0F2B46] focus:outline-none focus:border-[#B87333]', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.ROLE_CUSTOMER
        if commit:
            user.save()
        return user


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
        
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue chez Kay Mama, {user.first_name} !")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomerRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Ravi de vous revoir, {user.first_name or user.username} !")
            # Redirect staff to dashboard
            if user.is_staff_member:
                return redirect('dashboard:home')
            return redirect('accounts:profile')
        else:
            messages.error(request, "Identifiants invalides.")
            
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Vous vous êtes déconnecté avec succès.")
    return redirect('core:home')


@login_required
def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    reservations = Reservation.objects.filter(email=user.email).order_by('-date', '-time_slot')[:10]
    
    # Update profile info
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.save()
        messages.success(request, "Votre profil a été mis à jour avec succès.")
        return redirect('accounts:profile')
        
    context = {
        'orders': orders,
        'reservations': reservations,
    }
    return render(request, 'accounts/profile.html', context)
