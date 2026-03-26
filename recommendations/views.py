from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
import json

from .models import CustomUser, Category, Product, Rating, Comment, CartItem, Purchase
from .hybrid import hybrid_recommendations
from .content_based import content_based_recommendations
from .evaluation import evaluate_recommender


# ── AUTH ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            if not user.onboarding_done:
                return redirect('onboarding')
            return redirect('home')
        messages.error(request, 'Email ou mot de passe incorrect.')
    return render(request, 'recommendations/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
        else:
            # Compte inactif jusqu'à la confirmation email
            user = CustomUser.objects.create_user(
                username=username, email=email, password=password1
            )
            user.is_active = False
            user.save()

            # Génération du lien d'activation
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            activation_link = f"{protocol}://{domain}/activate/{uid}/{token}/"

            # Envoi de l'email HTML (uniquement si les credentials SMTP sont configurés)
            from django.conf import settings as dj_settings
            smtp_ok = bool(getattr(dj_settings, 'EMAIL_HOST_USER', None))

            if smtp_ok:
                try:
                    html_message = render_to_string(
                        'recommendations/emails/activation.html',
                        {'username': username, 'activation_link': activation_link}
                    )
                    send_mail(
                        subject="Activez votre compte RecoShop",
                        message=f"Bonjour {username},\n\nActivez votre compte : {activation_link}",
                        from_email=None,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    return redirect('email_sent')
                except Exception:
                    pass  # SMTP a échoué → on active directement ci-dessous

            # Pas de config SMTP ou échec : activer directement + connecter
            user.is_active = True
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, f'Bienvenue {username} ! Configurez votre profil.')
            return redirect('onboarding')

    return render(request, 'recommendations/register.html')


def email_sent_view(request):
    return render(request, 'recommendations/email_sent.html')


def activate_view(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, f'Bienvenue sur RecoShop, {user.username} ! Votre compte est activé.')
        return redirect('onboarding')
    else:
        return render(request, 'recommendations/activation_invalid.html')


@login_required
def onboarding_view(request):
    if request.user.onboarding_done:
        return redirect('home')
    if request.method == 'POST':
        user = request.user
        user.gender = request.POST.get('gender', '')
        interests = request.POST.getlist('interests')[:3]
        user.interests = ','.join(interests)
        user.budget = request.POST.get('budget', '')
        user.purchase_priority = request.POST.get('purchase_priority', '')
        user.onboarding_done = True
        user.save()
        messages.success(request, f'Profil configuré ! Découvrez vos recommandations personnalisées.')
        return redirect('home')
    return render(request, 'recommendations/onboarding.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ── LANDING (visiteurs non connectés) ────────────────────────────────────────

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'recommendations/landing.html')


def index_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('landing')


# ── HOME ──────────────────────────────────────────────────────────────────────

@login_required
def home_view(request):
    categories = Category.objects.annotate(product_count=Count('products')).all()
    featured = Product.objects.filter(is_featured=True).select_related('category')[:8]
    top_rated = Product.objects.annotate(avg_r=Avg('ratings__score')).order_by('-avg_r')[:8]
    recommendations = hybrid_recommendations(request.user, n=12)
    
    user_rating_count = Rating.objects.filter(user=request.user).count()
    
    context = {
        'categories': categories,
        'featured': featured,
        'top_rated': top_rated,
        'recommendations': recommendations,
        'user_rating_count': user_rating_count,
        'is_cold_start': user_rating_count == 0,
    }
    return render(request, 'recommendations/home.html', context)


# ── PRODUCTS ─────────────────────────────────────────────────────────────────

@login_required
def products_view(request):
    category_slug = request.GET.get('category', '')
    search_q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'featured')
    
    products = Product.objects.select_related('category').annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings')
    )
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_q:
        products = products.filter(
            Q(name__icontains=search_q) |
            Q(description__icontains=search_q) |
            Q(tags__icontains=search_q) |
            Q(brand__icontains=search_q)
        )
    
    sort_map = {
        'featured': '-is_featured',
        'price_asc': 'price',
        'price_desc': '-price',
        'rating': '-avg_rating',
        'newest': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-is_featured'))
    
    categories = Category.objects.annotate(product_count=Count('products')).all()
    current_category = Category.objects.filter(slug=category_slug).first() if category_slug else None
    
    sort_options = [
        ('Vedettes', 'featured'),
        ('Meilleures notes', 'rating'),
        ('Prix croissant', 'price_asc'),
        ('Prix décroissant', 'price_desc'),
        ('Plus récents', 'newest'),
    ]

    return render(request, 'recommendations/products.html', {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'search_q': search_q,
        'sort': sort,
        'sort_options': sort_options,
    })


@login_required
def product_detail_view(request, pk):
    product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
    comments = product.comments.select_related('user').order_by('-created_at')
    user_rating = Rating.objects.filter(user=request.user, product=product).first()
    in_cart = CartItem.objects.filter(user=request.user, product=product).exists()
    
    similar_ids = content_based_recommendations(product.id, Product.objects.all(), n=6)
    similar_products = list(Product.objects.filter(id__in=similar_ids)[:6])
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'comment':
            content = request.POST.get('content', '').strip()
            if content:
                Comment.objects.create(user=request.user, product=product, content=content)
                messages.success(request, 'Commentaire ajouté !')
        elif action == 'rate':
            score = int(request.POST.get('score', 0))
            if 1 <= score <= 5:
                Rating.objects.update_or_create(
                    user=request.user, product=product,
                    defaults={'score': score}
                )
                messages.success(request, f'Note {score}/5 enregistrée !')
        return redirect('product_detail', pk=pk)
    
    return render(request, 'recommendations/product_detail.html', {
        'product': product,
        'comments': comments,
        'user_rating': user_rating,
        'in_cart': in_cart,
        'similar_products': similar_products,
    })


# ── CART ─────────────────────────────────────────────────────────────────────

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product__category')
    total = sum(item.subtotal() for item in cart_items)
    categories_in_cart = {}
    for item in cart_items:
        cat = item.product.category.name
        if cat not in categories_in_cart:
            categories_in_cart[cat] = []
        categories_in_cart[cat].append(item)
    
    return render(request, 'recommendations/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'categories_in_cart': categories_in_cart,
    })


@login_required
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.quantity += 1
        item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': CartItem.objects.filter(user=request.user).count()})
    messages.success(request, f'"{product.name}" ajouté au panier !')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
@require_POST
def update_cart(request, pk):
    item = get_object_or_404(CartItem, user=request.user, product_id=pk)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        item.delete()
    else:
        item.quantity = quantity
        item.save()
    return redirect('cart')


@login_required
@require_POST
def remove_from_cart(request, pk):
    CartItem.objects.filter(user=request.user, product_id=pk).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        total = sum(i.subtotal() for i in cart_items)
        return JsonResponse({
            'success': True,
            'cart_count': cart_items.count(),
            'total': float(total)
        })
    return redirect('cart')


@login_required
@require_POST
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('cart')
    for item in cart_items:
        Purchase.objects.create(user=request.user, product=item.product, quantity=item.quantity)
    cart_items.delete()
    messages.success(request, 'Commande passée avec succès ! Merci pour votre achat.')
    return redirect('home')


# ── PROFILE ──────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    user = request.user
    purchases = Purchase.objects.filter(user=user).select_related('product__category').order_by('-purchased_at')
    ratings = Rating.objects.filter(user=user).select_related('product').order_by('-created_at')
    
    rec_ids = hybrid_recommendations(user, n=8)
    
    eval_data = None
    if ratings.count() >= 3:
        eval_data = evaluate_recommender(user, [p.id for p in rec_ids])
    
    return render(request, 'recommendations/profile.html', {
        'purchases': purchases,
        'ratings': ratings,
        'recommendations': rec_ids,
        'eval_data': eval_data,
    })


@login_required
@require_POST
def update_profile(request):
    user = request.user
    user.username = request.POST.get('username', user.username).strip()
    user.bio = request.POST.get('bio', '').strip()
    if 'profile_pic' in request.FILES:
        user.profile_pic = request.FILES['profile_pic']
    user.save()
    
    p1 = request.POST.get('new_password1', '')
    p2 = request.POST.get('new_password2', '')
    if p1 and p1 == p2:
        user.set_password(p1)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Mot de passe mis à jour.')
    
    messages.success(request, 'Profil mis à jour !')
    return redirect('profile')


# ── RECOMMENDATIONS ──────────────────────────────────────────────────────────

@login_required
def recommendations_view(request):
    recs = hybrid_recommendations(request.user, n=20)
    user_ratings = Rating.objects.filter(user=request.user).count()
    eval_data = None
    if user_ratings >= 3:
        eval_data = evaluate_recommender(request.user, [p.id for p in recs])
    
    return render(request, 'recommendations/recommendations.html', {
        'recommendations': recs,
        'eval_data': eval_data,
        'user_ratings': user_ratings,
    })


# ── API ───────────────────────────────────────────────────────────────────────

@login_required
def api_rate(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        score = int(data.get('score', 0))
        if 1 <= score <= 5:
            product = get_object_or_404(Product, pk=pk)
            Rating.objects.update_or_create(
                user=request.user, product=product,
                defaults={'score': score}
            )
            return JsonResponse({'success': True, 'avg': product.average_rating()})
    return JsonResponse({'success': False}, status=400)
