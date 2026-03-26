# ═══════════════════════════════════════════════════════════════
# AJOUTS À FAIRE DANS recommendations/models.py
# Coller ces classes APRÈS les classes existantes de ta camarade
# ═══════════════════════════════════════════════════════════════

# Ajouter cet import en haut du fichier de ta camarade (s'il n'existe pas) :
# import random
# from django.utils import timezone

import random
from django.utils import timezone
from django.db import models


class EmailVerificationCode(models.Model):
    """Code OTP à 6 chiffres envoyé par email à l'inscription."""
    user = models.OneToOneField(
        'recommendations.CustomUser',
        on_delete=models.CASCADE,
        related_name='email_code'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return timezone.now() < self.expires_at and self.attempts < 5

    def __str__(self):
        return f"Code {self.code} → {self.user.email}"


class OnboardingAnswer(models.Model):
    """Réponses du questionnaire d'onboarding de l'utilisateur."""
    user = models.OneToOneField(
        'recommendations.CustomUser',
        on_delete=models.CASCADE,
        related_name='onboarding'
    )
    # Question 1 : genre
    gender = models.CharField(max_length=20, blank=True)
    # Question 2 : catégories préférées (JSON list)
    preferred_categories = models.JSONField(default=list)
    # Question 3 : budget
    budget = models.CharField(max_length=20, blank=True)
    # Question 4 : priorité d'achat
    purchase_priority = models.CharField(max_length=50, blank=True)
    # Questions bonus
    frequency = models.CharField(max_length=30, blank=True)
    discovery_mode = models.JSONField(default=list)
    # Statut
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Onboarding de {self.user.email}"
