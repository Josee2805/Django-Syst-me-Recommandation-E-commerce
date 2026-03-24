"""
LuxeMart — ecommerce_reco/urls.py
URLs racine du projet.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recommendations.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
