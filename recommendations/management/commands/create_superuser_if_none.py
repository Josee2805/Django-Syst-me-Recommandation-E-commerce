import os
from django.core.management.base import BaseCommand
from recommendations.models import CustomUser


class Command(BaseCommand):
    help = 'Crée un superuser depuis les variables d\'environnement s\'il n\'en existe aucun'

    def handle(self, *args, **kwargs):
        if CustomUser.objects.filter(is_superuser=True).exists():
            self.stdout.write('Superuser déjà existant, rien à faire.')
            return

        email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@recoshop.com')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin1234')

        CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Superuser créé : {email} / {password}'
        ))
