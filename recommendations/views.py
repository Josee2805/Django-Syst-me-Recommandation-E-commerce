from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.views.decorators.http import require_POST
<<<<<<< Updated upstream
=======
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
>>>>>>> Stashed changes
import json
import logging

from .models import CustomUser, Category, Product, Rating, Comment, CartItem, Purchase
from .models import EmailVerificationCode, OnboardingAnswer
from .hybrid import hybrid_recommendations
from .content_based import content_based_recommendations
from .evaluation import evaluate_recommender

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# SECTION AUTH & ONBOARDING (Personne A)
# Remplace les vues register_view / login_view / activate_view
# ═══════════════════════════════════════════════════════════════

# ── Questions d'onboarding ───────────────────────────────────

ONBOARDING_QUESTIONS = [
    {
        'key': 'gender',
        'text': 'Tu es ?',
        'subtitle': 'Pour personnaliser tes recommandations',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Un homme',  'emoji': '👨', 'value': 'homme'},
            {'text': 'Une femme', 'emoji': '👩', 'value': 'femme'},
            {'text': 'Autre',     'emoji': '🧑', 'value': 'autre'},
        ]
    },
    {
        'key': 'categories',
        'text': "Quelles catégories t'intéressent ?",
        'subtitle': 'Sélectionne jusqu\'à 3 catégories',
        'type': 'multiple', 'max': 3,
        'choices': [
            {'text': 'Mode',                 'emoji': '👗', 'value': 'mode'},
            {'text': 'Électronique',          'emoji': '📱', 'value': 'electronique'},
            {'text': 'Maison',               'emoji': '🏠', 'value': 'maison'},
            {'text': 'Sport & Fitness',      'emoji': '⚽', 'value': 'sport'},
            {'text': 'Beauté & Soins',       'emoji': '💄', 'value': 'beaute'},
            {'text': 'Alimentation & Santé', 'emoji': '🥗', 'value': 'alimentation'},
            {'text': 'Gaming',               'emoji': '🎮', 'value': 'gaming'},
            {'text': 'Livres & Culture',     'emoji': '📚', 'value': 'livres'},
        ]
    },
    {
        'key': 'budget',
        'text': 'Ton budget moyen par achat ?',
        'subtitle': 'Pour des recommandations adaptées',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Petit budget',  'emoji': '💰', 'value': 'low',    'detail': 'Moins de 30€'},
            {'text': 'Budget moyen', 'emoji': '💳', 'value': 'medium', 'detail': '30€ – 150€'},
            {'text': 'Pas de limite','emoji': '🏆', 'value': 'high',   'detail': 'Plus de 150€'},
        ]
    },
    {
        'key': 'priority',
        'text': 'Ce qui influence le plus ton choix ?',
        'subtitle': 'Ta priorité principale',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Le prix',        'emoji': '💲', 'value': 'prix'},
            {'text': 'La qualité',     'emoji': '⭐', 'value': 'qualite'},
            {'text': 'Les promotions', 'emoji': '🔥', 'value': 'promotions'},
            {'text': 'Les nouveautés', 'emoji': '🆕', 'value': 'nouveautes'},
        ]
    },
    {
        'key': 'frequency',
        'text': 'Tu fais des achats en ligne ?',
        'subtitle': 'À quelle fréquence ?',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Rarement',              'emoji': '🌙', 'value': 'rarement'},
            {'text': 'Quelques fois/mois',    'emoji': '📅', 'value': 'mensuel'},
            {'text': 'Chaque semaine',        'emoji': '🛒', 'value': 'hebdo'},
            {'text': 'Presque tous les jours','emoji': '⚡', 'value': 'quotidien'},
        ]
    },
    {
        'key': 'discovery',
        'text': 'Comment tu préfères découvrir des produits ?',
        'subtitle': 'Plusieurs réponses possibles',
        'type': 'multiple', 'max': 3,
        'choices': [
            {'text': 'Recommandations perso','emoji': '🎯', 'value': 'reco'},
            {'text': 'Meilleures ventes',    'emoji': '🔝', 'value': 'bestseller'},
            {'text': 'Nouveautés',           'emoji': '✨', 'value': 'new'},
            {'text': 'Promotions & Soldes',  'emoji': '💸', 'value': 'promo'},
            {'text': 'Avis des clients',     'emoji': '💬', 'value': 'avis'},
        ]
    },
]


# ── Helper : envoyer le code OTP ─────────────────────────────

def _send_otp_code(request, user):
    """Génère un code OTP et l'envoie par email. Retourne l'objet code."""
    EmailVerificationCode.objects.filter(user=user).delete()
    code_obj = EmailVerificationCode.objects.create(user=user)

    subject = f"🔐 Connexion à RecoShop — Votre code de vérification"
    html_message = render_to_string(
        'recommendations/emails/otp_code.html',
        {'user': user, 'code': code_obj.code, 'expires_minutes': 15}
    )
    text_message = (
        f"Bonjour {user.username},\n\n"
        f"Votre code de vérification RecoShop : {code_obj.code}\n"
        f"Valable 15 minutes.\n\n"
        f"Si vous n'avez pas créé de compte, ignorez cet email."
    )
    email_sent = False
    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        logger.warning(f"[RecoShop] Email non envoyé à {user.email} : {e}")

    code_obj.email_sent = email_sent
    return code_obj


# ── Inscription ───────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
<<<<<<< Updated upstream
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
=======
        email     = request.POST.get('email', '').strip().lower()
        username  = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validations
        error = None
        if not email or not username or not password1:
            error = 'Tous les champs sont obligatoires.'
        elif password1 != password2:
            error = 'Les mots de passe ne correspondent pas.'
        elif len(password1) < 8:
            error = 'Le mot de passe doit contenir au moins 8 caractères.'
>>>>>>> Stashed changes
        elif CustomUser.objects.filter(email=email).exists():
            error = 'Cet email est déjà utilisé.'
        elif CustomUser.objects.filter(username=username).exists():
            error = "Ce nom d'utilisateur est déjà pris."

        if error:
            messages.error(request, error)
            return render(request, 'recommendations/register.html', {
                'email': email, 'username': username
            })

        # Créer l'utilisateur inactif
        user = CustomUser.objects.create_user(
            username=username, email=email, password=password1
        )
        user.is_active = False
        user.save()

        # Envoyer le code OTP
        code_obj = _send_otp_code(request, user)
        request.session['pending_email'] = email

        if not code_obj.email_sent:
            # Fallback : afficher le code à l'écran si SMTP non configuré
            request.session['dev_code'] = code_obj.code
            messages.warning(
                request,
                "Email non envoyé (SMTP non configuré). "
                "Votre code de test s'affiche sur cette page."
            )
        else:
<<<<<<< Updated upstream
            user = CustomUser.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, f'Bienvenue sur LuxeMart, {username} !')
            return redirect('home')
    return render(request, 'recommendations/register.html')


=======
            messages.success(
                request,
                f"Compte créé ! Un code à 6 chiffres a été envoyé à {email}."
            )
        return redirect('verify_code')

    return render(request, 'recommendations/register.html')


# ── Vérification du code OTP ──────────────────────────────────

def verify_code_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    pending_email = request.session.get('pending_email', '')
    dev_code      = request.session.get('dev_code', '')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        code  = request.POST.get('code', '').strip()

        ctx = {'pending_email': email, 'dev_code': dev_code}

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Aucun compte trouvé avec cet email.")
            return render(request, 'recommendations/verify_code.html', ctx)

        try:
            code_obj = EmailVerificationCode.objects.get(user=user)
        except EmailVerificationCode.DoesNotExist:
            messages.error(request, "Aucun code actif. Demandez un nouveau code.")
            return render(request, 'recommendations/verify_code.html', ctx)

        if not code_obj.is_valid:
            messages.error(request, "Code expiré ou trop de tentatives. Demandez un nouveau code.")
            return render(request, 'recommendations/verify_code.html', ctx)

        if code_obj.code != code:
            code_obj.attempts += 1
            code_obj.save()
            remaining = max(0, 5 - code_obj.attempts)
            messages.error(request, f"Code incorrect. {remaining} tentative(s) restante(s).")
            return render(request, 'recommendations/verify_code.html', ctx)

        # ✅ Code valide — activer le compte
        user.is_active = True
        user.save()
        code_obj.delete()
        request.session.pop('pending_email', None)
        request.session.pop('dev_code', None)

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Bienvenue sur RecoShop, {user.username} ! 🎉")
        return redirect('onboarding_start')

    return render(request, 'recommendations/verify_code.html', {
        'pending_email': pending_email,
        'dev_code': dev_code,
    })


def resend_code_view(request):
    """Renvoie un nouveau code OTP."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = CustomUser.objects.get(email=email, is_active=False)
            code_obj = _send_otp_code(request, user)
            request.session['pending_email'] = email
            if not code_obj.email_sent:
                request.session['dev_code'] = code_obj.code
                messages.warning(request, f"Code de test : {code_obj.code}")
            else:
                messages.success(request, "Nouveau code envoyé ! Vérifiez votre boîte mail.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Aucun compte en attente pour cet email.")
    return redirect('verify_code')


# ── Connexion ─────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        # CustomUser utilise email comme USERNAME_FIELD
        user = authenticate(request, username=email, password=password)
        if user:
            if not user.is_active:
                request.session['pending_email'] = email
                messages.warning(request, "Veuillez d'abord vérifier votre email.")
                return redirect('verify_code')
            login(request, user)
            # Rediriger vers l'onboarding si pas encore fait
            try:
                if not user.onboarding.completed:
                    return redirect('onboarding_start')
            except OnboardingAnswer.DoesNotExist:
                return redirect('onboarding_start')
            return redirect(request.GET.get('next', 'home'))

        messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'recommendations/login.html')


# ── Déconnexion ───────────────────────────────────────────────

>>>>>>> Stashed changes
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


<<<<<<< Updated upstream
# ── HOME ──────────────────────────────────────────────────────────────────────
=======
# ── Onboarding ────────────────────────────────────────────────

@login_required
def onboarding_start_view(request):
    try:
        if request.user.onboarding.completed:
            return redirect('home')
    except OnboardingAnswer.DoesNotExist:
        pass
    return render(request, 'recommendations/onboarding/start.html', {
        'total': len(ONBOARDING_QUESTIONS),
        'username': request.user.username,
    })


@login_required
def onboarding_step_view(request, step):
    try:
        if request.user.onboarding.completed:
            return redirect('home')
    except OnboardingAnswer.DoesNotExist:
        pass

    total = len(ONBOARDING_QUESTIONS)
    if step < 1 or step > total:
        return redirect('onboarding_complete')

    q_data   = ONBOARDING_QUESTIONS[step - 1]
    progress = int((step / total) * 100)

    if request.method == 'POST':
        selected = request.POST.getlist('answer')
        max_c = q_data.get('max', 99)
        request.session[f'ob_{q_data["key"]}'] = selected[:max_c]
        request.session.modified = True

        if step < total:
            return redirect('onboarding_step', step=step + 1)
        return redirect('onboarding_complete')

    return render(request, 'recommendations/onboarding/step.html', {
        'q': q_data,
        'step': step,
        'total': total,
        'progress': progress,
        'is_last': step == total,
        'selected': request.session.get(f'ob_{q_data["key"]}', []),
    })


@login_required
def onboarding_complete_view(request):
    """Sauvegarde les réponses et redirige vers l'accueil."""
    user = request.user

    # Récupérer les réponses depuis la session
    def _get(key):
        return request.session.get(f'ob_{key}', [])

    gender_sel   = _get('gender')
    cats_sel     = _get('categories')
    budget_sel   = _get('budget')
    priority_sel = _get('priority')
    freq_sel     = _get('frequency')
    disc_sel     = _get('discovery')

    gender   = ONBOARDING_QUESTIONS[0]['choices'][int(gender_sel[0])]['value']   if gender_sel   else ''
    budget   = ONBOARDING_QUESTIONS[2]['choices'][int(budget_sel[0])]['value']   if budget_sel   else ''
    priority = ONBOARDING_QUESTIONS[3]['choices'][int(priority_sel[0])]['value'] if priority_sel else ''
    frequency= ONBOARDING_QUESTIONS[4]['choices'][int(freq_sel[0])]['value']     if freq_sel     else ''

    cats = [ONBOARDING_QUESTIONS[1]['choices'][int(i)]['value'] for i in cats_sel
            if i.isdigit() and int(i) < len(ONBOARDING_QUESTIONS[1]['choices'])]
    disc = [ONBOARDING_QUESTIONS[5]['choices'][int(i)]['value'] for i in disc_sel
            if i.isdigit() and int(i) < len(ONBOARDING_QUESTIONS[5]['choices'])]

    ob, _ = OnboardingAnswer.objects.get_or_create(user=user)
    ob.gender               = gender
    ob.preferred_categories = cats
    ob.budget               = budget
    ob.purchase_priority    = priority
    ob.frequency            = frequency
    ob.discovery_mode       = disc
    ob.completed            = True
    ob.save()

    # Nettoyer la session
    for q in ONBOARDING_QUESTIONS:
        request.session.pop(f'ob_{q["key"]}', None)

    messages.success(request, "Vos préférences sont enregistrées. Bonne découverte ! 🎯")
    return render(request, 'recommendations/onboarding/complete.html', {'ob': ob})


# ── Pages statiques auth ──────────────────────────────────────

def email_sent_view(request):
    return render(request, 'recommendations/email_sent.html')


def index_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('landing')


# ═══════════════════════════════════════════════════════════════
# VUES EXISTANTES (ta camarade — NE PAS MODIFIER)
# ═══════════════════════════════════════════════════════════════

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'recommendations/landing.html')

>>>>>>> Stashed changes

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
            Q(name__icontains=search_q) | Q(description__icontains=search_q) |
            Q(tags__icontains=search_q) | Q(brand__icontains=search_q)
        )
    sort_map = {'featured': '-is_featured', 'price_asc': 'price', 'price_desc': '-price',
                'rating': '-avg_rating', 'newest': '-created_at'}
    products = products.order_by(sort_map.get(sort, '-is_featured'))
    categories = Category.objects.annotate(product_count=Count('products')).all()
    current_category = Category.objects.filter(slug=category_slug).first() if category_slug else None
<<<<<<< Updated upstream
    
    return render(request, 'recommendations/products.html', {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'search_q': search_q,
        'sort': sort,
=======
    sort_options = [('Vedettes','featured'),('Meilleures notes','rating'),
                    ('Prix croissant','price_asc'),('Prix décroissant','price_desc'),('Plus récents','newest')]
    return render(request, 'recommendations/products.html', {
        'products': products, 'categories': categories,
        'current_category': current_category, 'search_q': search_q,
        'sort': sort, 'sort_options': sort_options,
>>>>>>> Stashed changes
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
                Rating.objects.update_or_create(user=request.user, product=product, defaults={'score': score})
                messages.success(request, f'Note {score}/5 enregistrée !')
        return redirect('product_detail', pk=pk)
    return render(request, 'recommendations/product_detail.html', {
        'product': product, 'comments': comments,
        'user_rating': user_rating, 'in_cart': in_cart, 'similar_products': similar_products,
    })


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
        'cart_items': cart_items, 'total': total, 'categories_in_cart': categories_in_cart,
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
        return JsonResponse({'success': True, 'cart_count': cart_items.count(), 'total': float(total)})
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
        'purchases': purchases, 'ratings': ratings,
        'recommendations': rec_ids, 'eval_data': eval_data,
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


@login_required
def recommendations_view(request):
    recs = hybrid_recommendations(request.user, n=20)
    user_ratings = Rating.objects.filter(user=request.user).count()
    eval_data = None
    if user_ratings >= 3:
        eval_data = evaluate_recommender(request.user, [p.id for p in recs])
    return render(request, 'recommendations/recommendations.html', {
        'recommendations': recs, 'eval_data': eval_data, 'user_ratings': user_ratings,
    })


@login_required
def api_rate(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        score = int(data.get('score', 0))
        if 1 <= score <= 5:
            product = get_object_or_404(Product, pk=pk)
            Rating.objects.update_or_create(user=request.user, product=product, defaults={'score': score})
            return JsonResponse({'success': True, 'avg': product.average_rating()})
    return JsonResponse({'success': False}, status=400)
