"""
LuxeMart — recommendations/models.py
Sections balisées A / B / C — ne modifier que SA propre section.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import uuid
import random


# ════════════════════════════════════════════════════════════════
# ═══ SECTION A — AUTH & ONBOARDING  (Personne A)             ═══
# ════════════════════════════════════════════════════════════════

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    email_verified = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class EmailVerificationCode(models.Model):
    """Code OTP à 6 chiffres envoyé par email."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_code')
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
        return f"Code {self.code} pour {self.user.email}"


class OnboardingQuestion(models.Model):
    TYPES = [('single', 'Choix unique'), ('multiple', 'Choix multiple')]
    text = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=200, blank=True)
    question_type = models.CharField(max_length=20, choices=TYPES, default='single')
    max_choices = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text}"


class OnboardingChoice(models.Model):
    question = models.ForeignKey(OnboardingQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    emoji = models.CharField(max_length=5, blank=True)
    recommendation_tag = models.CharField(max_length=100, blank=True)
    linked_category = models.ForeignKey(
        'Category', null=True, blank=True, on_delete=models.SET_NULL
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question.text[:30]} → {self.text}"


class UserOnboardingAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='onboarding_answers')
    question = models.ForeignKey(OnboardingQuestion, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(OnboardingChoice, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


class UserPreference(models.Model):
    BUDGET = [('low', 'Petit budget'), ('medium', 'Budget moyen'), ('high', 'Pas de limite')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    gender = models.CharField(max_length=20, blank=True)
    preferred_categories = models.JSONField(default=list)
    preference_tags = models.JSONField(default=list)
    budget_range = models.CharField(max_length=20, choices=BUDGET, default='medium')
    purchase_priority = models.CharField(max_length=50, blank=True)
    category_scores = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Préférences de {self.user.username}"


# ════════════════════════════════════════════════════════════════
# ═══ SECTION B — CATALOGUE & PANIER  (Personne B)            ═══
# ════════════════════════════════════════════════════════════════

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='📦')
    color = models.CharField(max_length=7, default='#C9A84C')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def average_rating(self):
        r = self.ratings.all()
        return round(sum(x.score for x in r) / len(r), 1) if r else 0

    @property
    def ratings_count(self):
        return self.ratings.count()

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return f"https://picsum.photos/seed/{self.slug}/400/300"

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} → {self.product.name} : {self.score}/5"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=1000)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS = [
        ('pending', 'En attente'), ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'), ('delivered', 'Livrée'), ('cancelled', 'Annulée'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def subtotal(self):
        return self.product_price * self.quantity


class ProductView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by')
    count = models.IntegerField(default=1)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')


# ════════════════════════════════════════════════════════════════
# ═══ SECTION C — RECOMMANDATIONS  (Personne C)               ═══
# ════════════════════════════════════════════════════════════════
# Personne C utilise Rating, Product, ProductView, UserPreference.
