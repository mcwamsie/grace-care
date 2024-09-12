from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create a superuser without prompting for input'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        #username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'mcwamsie')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'root_admin@emcwamsie.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'P@ssw0rd!1#')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, first_name="Root", last_name="Admin", password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{email}" created successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{email}" already exists.'))
