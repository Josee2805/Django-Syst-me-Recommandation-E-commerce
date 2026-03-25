"""
LuxeMart — recommendations/views.py
Sections A / B / C — ne modifier que sa propre section.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .forms import RegisterForm, LoginForm, VerifyCodeForm
from .models import (
    UserProfile, EmailVerificationCode,
    UserOnboardingAnswer, UserPreference,
)


# ════════════════════════════════════════════════════════════════
# ═══ SECTION A — AUTH & ONBOARDING  (Personne A)             ═══
# ════════════════════════════════════════════════════════════════

def _send_verification_code(user):
    """
    Génère un code OTP et l'envoie par email.
    Si l'envoi SMTP échoue (ex: config pas encore faite),
    le code est stocké en session et affiché sur la page de vérification.
    """
    from .models import EmailVerificationCode
    EmailVerificationCode.objects.filter(user=user).delete()
    code_obj = EmailVerificationCode.objects.create(user=user)

    subject = "🔐 Connexion à LuxeMart — Votre code de vérification"
    html_body = render_to_string('auth/email_code.html', {
        'user': user, 'code': code_obj.code, 'expires_minutes': 15,
    })
    text_body = (
        f"Bonjour {user.first_name},\n\n"
        f"Votre code de vérification LuxeMart : {code_obj.code}\n"
        f"Valable 15 minutes.\n\n"
        f"Si vous n'avez pas créé de compte, ignorez cet email."
    )

    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_body,
            fail_silently=False,
        )
        code_obj.email_sent = True
    except Exception as e:
        # Email non envoyé (SMTP non configuré) — on continue quand même
        # Le code sera affiché directement sur la page de vérification
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"[LuxeMart] Email non envoyé à {user.email} : {e}")
        code_obj.email_sent = False

    return code_obj


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'].lower(),
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_active=False,
            )
            UserProfile.objects.create(user=user)
            code_obj = _send_verification_code(user)
            request.session['pending_email'] = user.email

            # Si email non envoyé (SMTP pas configuré), on passe le code
            # en session pour l'afficher sur la page de vérification
            if not getattr(code_obj, 'email_sent', True):
                request.session['dev_code'] = code_obj.code
                messages.warning(
                    request,
                    f"⚠ Email non envoyé (SMTP non configuré). "
                    f"Votre code de test est affiché sur cette page."
                )
            else:
                messages.success(
                    request,
                    f"Compte créé ! Un code a été envoyé à {user.email}."
                )
            return redirect('verify_code')
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du compte : {e}")
    return render(request, 'auth/register.html', {'form': form})


def verify_code_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    pending_email = request.session.get('pending_email', '')
    dev_code = request.session.get('dev_code', '')   # code affiché si SMTP pas configuré

    form = VerifyCodeForm(request.POST or None, initial={'email': pending_email})
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()
        code  = form.cleaned_data['code']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Aucun compte trouvé avec cet email.")
            return render(request, 'auth/verify_code.html', {
                'form': form, 'pending_email': pending_email, 'dev_code': dev_code
            })
        try:
            code_obj = EmailVerificationCode.objects.get(user=user)
        except EmailVerificationCode.DoesNotExist:
            messages.error(request, "Aucun code actif. Demandez un nouveau code ci-dessous.")
            return render(request, 'auth/verify_code.html', {
                'form': form, 'pending_email': pending_email, 'dev_code': dev_code
            })
        if not code_obj.is_valid:
            messages.error(request, "Code expiré ou trop de tentatives. Demandez un nouveau code.")
            return render(request, 'auth/verify_code.html', {
                'form': form, 'pending_email': pending_email, 'dev_code': dev_code
            })
        if code_obj.code != code:
            code_obj.attempts += 1
            code_obj.save()
            remaining = max(0, 5 - code_obj.attempts)
            messages.error(request, f"Code incorrect. {remaining} tentative(s) restante(s).")
            return render(request, 'auth/verify_code.html', {
                'form': form, 'pending_email': pending_email, 'dev_code': dev_code
            })
        # ✅ Code valide
        user.is_active = True
        user.save()
        try:
            profile = user.profile
            profile.email_verified = True
            profile.save()
        except Exception:
            pass
        code_obj.delete()
        request.session.pop('pending_email', None)
        request.session.pop('dev_code', None)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Bienvenue {user.first_name} ! Email vérifié 🎉")
        return redirect('onboarding_start')
    return render(request, 'auth/verify_code.html', {
        'form': form, 'pending_email': pending_email, 'dev_code': dev_code
    })


def resend_code_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        try:
            user = User.objects.get(email=email, is_active=False)
            _send_verification_code(user)
            request.session['pending_email'] = email
            messages.success(request, "Nouveau code envoyé ! Vérifiez votre boîte mail.")
        except User.DoesNotExist:
            messages.error(request, "Aucun compte en attente pour cet email.")
    return redirect('verify_code')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email    = form.cleaned_data['email'].lower()
        password = form.cleaned_data['password']
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Identifiants incorrects.")
            return render(request, 'auth/login.html', {'form': form})
        if not user_obj.is_active:
            request.session['pending_email'] = email
            messages.warning(request, "Veuillez d'abord vérifier votre email.")
            return redirect('verify_code')
        user = authenticate(request, username=user_obj.username, password=password)
        if user:
            login(request, user)
            try:
                if not user.profile.onboarding_completed:
                    return redirect('onboarding_start')
            except Exception:
                pass
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, "Identifiants incorrects.")
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')


# ── Onboarding data ──────────────────────────────────────────────

ONBOARDING_QUESTIONS = [
    {
        'key': 'gender', 'text': 'Tu es ?',
        'subtitle': 'Aide-nous à personnaliser tes recommandations',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Un homme',  'emoji': '👨', 'tag': 'homme'},
            {'text': 'Une femme', 'emoji': '👩', 'tag': 'femme'},
            {'text': 'Autre',     'emoji': '🧑', 'tag': 'autre'},
        ]
    },
    {
        'key': 'categories', 'text': "Quelles catégories t'intéressent ?",
        'subtitle': 'Choisis jusqu\'à 3 catégories',
        'type': 'multiple', 'max': 3,
        'choices': [
            {'text': 'Mode',                 'emoji': '👗', 'tag': 'mode',         'cat': 'Mode'},
            {'text': 'Électronique',          'emoji': '📱', 'tag': 'electronique', 'cat': 'Électronique'},
            {'text': 'Maison',               'emoji': '🏠', 'tag': 'maison',       'cat': 'Maison'},
            {'text': 'Sport & Fitness',      'emoji': '⚽', 'tag': 'sport',        'cat': 'Sport'},
            {'text': 'Beauté & Soins',       'emoji': '💄', 'tag': 'beaute',       'cat': 'Beauté'},
            {'text': 'Alimentation & Santé', 'emoji': '🥗', 'tag': 'alimentation', 'cat': 'Cuisine'},
            {'text': 'Gaming',               'emoji': '🎮', 'tag': 'gaming',       'cat': 'Gaming'},
            {'text': 'Livres & Culture',     'emoji': '📚', 'tag': 'livres',       'cat': 'Livres'},
        ]
    },
    {
        'key': 'budget', 'text': 'Ton budget moyen par achat ?',
        'subtitle': 'Pour des recommandations adaptées',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Petit budget',  'emoji': '💰', 'tag': 'budget_low',    'detail': 'Moins de 30€'},
            {'text': 'Budget moyen', 'emoji': '💳', 'tag': 'budget_medium', 'detail': '30€ – 150€'},
            {'text': 'Pas de limite','emoji': '🏆', 'tag': 'budget_high',   'detail': 'Plus de 150€'},
        ]
    },
    {
        'key': 'priority', 'text': 'Ce qui influence le plus ton choix ?',
        'subtitle': 'Ta priorité principale',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Le prix',        'emoji': '💲', 'tag': 'price_sensitive'},
            {'text': 'La qualité',     'emoji': '⭐', 'tag': 'quality_focused'},
            {'text': 'Les promotions', 'emoji': '🔥', 'tag': 'deal_seeker'},
            {'text': 'Les nouveautés', 'emoji': '🆕', 'tag': 'trend_follower'},
        ]
    },
    {
        'key': 'frequency', 'text': 'Tu fais des achats en ligne ?',
        'subtitle': 'À quelle fréquence ?',
        'type': 'single', 'max': 1,
        'choices': [
            {'text': 'Rarement',              'emoji': '🌙', 'tag': 'freq_rare'},
            {'text': 'Quelques fois/mois',    'emoji': '📅', 'tag': 'freq_monthly'},
            {'text': 'Chaque semaine',        'emoji': '🛒', 'tag': 'freq_weekly'},
            {'text': 'Presque tous les jours','emoji': '⚡', 'tag': 'freq_daily'},
        ]
    },
    {
        'key': 'discovery', 'text': 'Comment tu préfères découvrir des produits ?',
        'subtitle': 'Plusieurs réponses possibles',
        'type': 'multiple', 'max': 3,
        'choices': [
            {'text': 'Recommandations perso','emoji': '🎯', 'tag': 'reco_lover'},
            {'text': 'Meilleures ventes',    'emoji': '🔝', 'tag': 'bestseller'},
            {'text': 'Nouveautés',           'emoji': '✨', 'tag': 'new_arrival'},
            {'text': 'Promotions & Soldes',  'emoji': '💸', 'tag': 'promo_hunter'},
            {'text': 'Avis des clients',     'emoji': '💬', 'tag': 'review_driven'},
        ]
    },
]


@login_required
def onboarding_start_view(request):
    try:
        if request.user.profile.onboarding_completed:
            return redirect('home')
    except Exception:
        pass
    return render(request, 'onboarding/start.html', {
        'total': len(ONBOARDING_QUESTIONS),
    })


@login_required
def onboarding_step_view(request, step):
    try:
        if request.user.profile.onboarding_completed:
            return redirect('home')
    except Exception:
        pass
    total = len(ONBOARDING_QUESTIONS)
    if step < 1 or step > total:
        return redirect('onboarding_complete')
    q_data   = ONBOARDING_QUESTIONS[step - 1]
    progress = int((step / total) * 100)
    if request.method == 'POST':
        selected = request.POST.getlist('answer')
        if not selected and q_data['type'] == 'single':
            messages.error(request, "Veuillez sélectionner une réponse.")
        else:
            max_c = q_data.get('max', 99)
            request.session[f'onboarding_{q_data["key"]}'] = selected[:max_c]
            request.session.modified = True
            return redirect('onboarding_step', step=step + 1) if step < total else redirect('onboarding_complete')
    return render(request, 'onboarding/step.html', {
        'q': q_data, 'step': step, 'total': total,
        'progress': progress, 'is_last': step == total,
        'selected': request.session.get(f'onboarding_{q_data["key"]}', []),
    })


@login_required
def onboarding_complete_view(request):
    from .models import Category
    user = request.user
    tags, categories, gender, budget, priority = [], [], '', 'medium', ''
    for q in ONBOARDING_QUESTIONS:
        selected = request.session.get(f'onboarding_{q["key"]}', [])
        for idx_str in selected:
            try:
                choice = q['choices'][int(idx_str)]
                tag = choice.get('tag', '')
                if tag:
                    tags.append(tag)
                cat_name = choice.get('cat', '')
                if cat_name:
                    try:
                        cat = Category.objects.get(name__icontains=cat_name)
                        if cat.id not in categories:
                            categories.append(cat.id)
                    except Exception:
                        pass
                if q['key'] == 'gender':
                    gender = tag
                if q['key'] == 'budget':
                    budget = 'low' if 'low' in tag else ('high' if 'high' in tag else 'medium')
                if q['key'] == 'priority':
                    priority = tag
            except (IndexError, ValueError):
                pass
    pref, _ = UserPreference.objects.get_or_create(user=user)
    pref.gender = gender
    pref.preferred_categories = categories
    pref.preference_tags = list(set(tags))
    pref.budget_range = budget
    pref.purchase_priority = priority
    pref.save()
    try:
        profile = user.profile
        profile.onboarding_completed = True
        profile.save()
    except Exception:
        pass
    for q in ONBOARDING_QUESTIONS:
        request.session.pop(f'onboarding_{q["key"]}', None)
    messages.success(request, "Préférences enregistrées. Bonne découverte sur LuxeMart ! 🎉")
    return render(request, 'onboarding/complete.html', {'preferences': pref})


# ════════════════════════════════════════════════════════════════
# ═══ SECTION B — CATALOGUE & PANIER  (Personne B)            ═══
# ════════════════════════════════════════════════════════════════

def home_view(request):
    from .models import Category
    from django.db.models import Count, Q
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    return render(request, 'shop/home.html', {'categories': categories})


def products_view(request):
    return render(request, 'shop/products.html', {'total_count': 0})


def product_detail_view(request, slug):
    return render(request, 'shop/product_detail.html')


@login_required
def cart_view(request):
    return render(request, 'shop/cart.html')


@login_required
def add_to_cart_view(request, slug):
    return redirect('cart')


@login_required
def update_cart_view(request, item_id):
    return redirect('cart')


@login_required
def remove_from_cart_view(request, item_id):
    return redirect('cart')


@login_required
def clear_cart_view(request):
    return redirect('cart')


@login_required
def checkout_view(request):
    return redirect('profile')


@login_required
def rate_product_view(request, slug):
    return redirect('product_detail', slug=slug)


@login_required
def comment_product_view(request, slug):
    return redirect('product_detail', slug=slug)


@login_required
def delete_comment_view(request, slug):
    return redirect('product_detail', slug=slug)


@login_required
def profile_view(request):
    return render(request, 'shop/profile.html')


# ════════════════════════════════════════════════════════════════
# ═══ SECTION C — RECOMMANDATIONS  (Personne C)               ═══
# ════════════════════════════════════════════════════════════════

@login_required
def recommendations_view(request):
    return render(request, 'recommendations/recommendations.html')
