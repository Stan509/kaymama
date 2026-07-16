import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize the first administrator account from environment variables.'

    def handle(self, *args, **options):
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not email or not password:
            self.stderr.write(self.style.ERROR(
                'DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD environment variables are missing.'
            ))
            return

        username = email.split('@')[0]
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(
                f'Superuser with email "{email}" already exists.'
            ))
            return

        if User.objects.filter(username=username).exists():
            # If username exists, generate a unique one
            username = f"{username}_admin"

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role=User.ROLE_SUPER_ADMIN
        )
        self.stdout.write(self.style.SUCCESS(
            f'Superuser "{username}" created successfully with role SUPER_ADMIN.'
        ))
