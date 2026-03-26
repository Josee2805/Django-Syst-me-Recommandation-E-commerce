import time
import unicodedata
import requests
from django.core.management.base import BaseCommand
from recommendations.models import Product, Category

UNSPLASH_KEY = 'eUw0bzgtDDdqU9cUUG1Bb-1JP93sAqEOkHfJtDkNAaQ'
FALLBACK = 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=500'

# Overrides manuels (prioritaires sur la traduction automatique)
PRODUCT_KEYWORD_OVERRIDES = {
    # Electronique — marques connues
    'iPhone 15 Pro':             'premium smartphone titanium close-up',
    'Samsung Galaxy S24':        'android smartphone dark elegant',
    'Samsung Galaxy S24 Ultra':  'android smartphone black',
    'AirPods Pro':               'wireless earphones audio minimal white',
    'GoPro Hero 12':             'action camera waterproof',
    # Sport
    'Montre GPS Garmin':         'GPS sport smartwatch fitness',
    'Sac de sport Nike':         'sports duffel bag gym training',
    # Mode
    'Adidas Stan Smith':         'white leather sneakers clean minimal',
    # Maison
    'Tapis berbere':             'handmade moroccan rug wool colorful',
    # Beaute
    'Rouge a levres MAC':        'red lipstick beauty makeup cosmetics',
    'Dyson V15 Detect':          'cordless vacuum cleaner',
    'Veste en cuir vintage':     'vintage leather jacket biker',
    'Costume 3 pieces slim':     'mens slim fit suit',
    'Sac a main Tote premium':   'leather tote bag woman',
    'Jean slim dechire':         'ripped slim denim jeans',
    'Echarpe cachemire':         'cashmere scarf luxury',
    'Miroir baroque ovale':      'ornate oval wall mirror',
    'Literie 1000 fils':         'luxury cotton bed linen white',
    'Plante monstera XL':        'monstera plant indoor pot',
    'Tapis de course Pro':       'treadmill running machine gym',
    'Yoga mat premium':          'yoga mat exercise fitness',
    'Montre Garmin Fenix 7':     'GPS sport smartwatch',
    'Creme La Mer':              'luxury face cream skincare jar',
    'Atomic Habits':             'self improvement book reading',
    'Apprendre Django':          'python programming book developer',
    'Robot KitchenAid':          'stand mixer kitchen baking',
    'Machine Nespresso Vertuo':  'espresso coffee machine capsule',
    'Couteaux Wusthof set 7':    'kitchen knife set chef',
    'Nintendo Switch OLED':      'portable gaming console handheld',
    'LEGO Technic Ferrari':      'lego technic racing car',
    'Monopoly edition luxe':     'luxury board game family',
    'Valise Rimowa Original':    'aluminum luggage suitcase travel',
    'Sac a dos Osprey 65L':      'hiking backpack trekking outdoor',
    'Tente 4 saisons':           'camping tent outdoor mountain',
    'Montre Rolex Submariner':   'luxury diving watch silver',
    'Dashcam 4K Sony':           'dashboard car camera driving',
    'Siege baquet sport':        'racing car bucket seat red',
    'Poussette Bugaboo':         'baby stroller pram urban',
    'Lit bebe evolutif':         'baby crib wooden nursery',
}

CATEGORY_KEYWORD_MAP = {
    # Electronique
    'electronique':      'electronics technology gadgets modern',
    'electronic':        'electronics technology gadgets modern',
    'informatique':      'computer technology workspace minimal',
    # Mode / Vetements
    'mode':              'fashion luxury clothing boutique elegant',
    'fashion':           'fashion luxury clothing boutique elegant',
    'vetements':         'clothing fashion apparel stylish',
    'chaussures':        'shoes sneakers footwear fashion',
    'sacs':              'luxury handbag leather fashion bag',
    # Maison
    'maison':            'modern home interior scandinavian decor',
    'deco':              'interior design home decoration elegant',
    # Sport
    'sport':             'sport fitness active outdoor athlete',
    'fitness':           'gym workout fitness equipment',
    # Beaute / Sante
    'beaute':            'beauty skincare cosmetics luxury perfume',
    'sante':             'health wellness natural organic',
    'cosmetique':        'cosmetics makeup beauty products',
    # Cuisine / Food
    'cuisine':           'gourmet food cooking kitchen chef',
    'food':              'gourmet food restaurant fine dining',
    # Jeux / Jouets
    'jeux':              'games board games entertainment',
    'jouets':            'colorful toys children playful',
    # Voyage
    'voyage':            'travel adventure destination wanderlust',
    'travel':            'travel adventure landscape destination',
    # Auto / Moto
    'auto':              'luxury car automotive sports vehicle',
    'voiture':           'sports car luxury automotive',
    'moto':              'motorcycle adventure road freedom',
    # Bebe / Enfants
    'bebe':              'baby nursery pastel soft newborn',
    'enfant':            'children kids colorful playful',
    'enfants':           'children kids colorful toys',
    # Livres / Culture
    'livres':            'books library reading knowledge',
    'culture':           'art culture museum gallery',
    # Bijoux / Luxe
    'bijoux':            'jewelry gold diamonds luxury accessories',
    'luxe':              'luxury lifestyle elegant premium',
    'montres':           'luxury watch timepiece elegant gold',
}


def strip_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


def translate_to_english(text):
    """Traduit le texte en anglais via deep-translator (Google Translate)."""
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source='auto', target='en').translate(text)
        return result if result else text
    except Exception as e:
        print(f"  Traduction echouee pour '{text}': {e}")
        return text


def get_product_query(product):
    """
    Determine le mot-cle de recherche pour un produit:
    1. Override manuel si disponible.
    2. Sinon, traduction automatique du nom.
    Ajoute la categorie traduite pour affiner la recherche.
    """
    normalized = strip_accents(product.name)

    # 1. Override manuel
    if normalized in PRODUCT_KEYWORD_OVERRIDES:
        return PRODUCT_KEYWORD_OVERRIDES[normalized]

    # 2. Traduction automatique
    translated = translate_to_english(product.name)
    # Ajouter le nom de la categorie traduit pour affiner
    cat_translated = translate_to_english(product.category.name) if product.category else ''
    if cat_translated and cat_translated.lower() not in translated.lower():
        return f"{translated} {cat_translated}"
    return translated


def get_category_query(category):
    """Determine le mot-cle pour une categorie via le mapping ou la traduction."""
    key = strip_accents(category.slug.lower().replace('-', ' '))
    for k, v in CATEGORY_KEYWORD_MAP.items():
        if k in key or key in k:
            return v
    # Fallback: traduction automatique du nom
    return translate_to_english(category.name) + ' store lifestyle'


def fetch_image(query, orientation='squarish', size_suffix='&w=800&q=80&fit=crop'):
    """Cherche une photo sur Unsplash et retourne l'URL optimisee."""
    try:
        response = requests.get(
            'https://api.unsplash.com/search/photos',
            headers={'Authorization': f'Client-ID {UNSPLASH_KEY}'},
            params={
                'query': query,
                'per_page': 5,
                'orientation': orientation,
                'content_filter': 'high',
                'order_by': 'relevant',
            },
            timeout=10,
        )
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                photo = results[1] if len(results) > 1 else results[0]
                base_url = photo['urls']['raw']
                return f"{base_url}{size_suffix}"
        elif response.status_code == 403:
            print('  Limite API atteinte (403) - pause 60s')
            time.sleep(60)
        elif response.status_code == 401:
            print('  Authentification echouee (401) - cle API invalide')
        elif response.status_code == 429:
            print('  Rate limit (429) - pause 30s')
            time.sleep(30)
        else:
            print(f'  Erreur HTTP {response.status_code}')
    except Exception as e:
        print(f'  Erreur reseau: {e}')
    return None


class Command(BaseCommand):
    help = 'Recupere les images Unsplash pour les produits et les categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Refetch meme les elements qui ont deja une image_url',
        )
        parser.add_argument(
            '--retry-fallback',
            action='store_true',
            help='Relance uniquement les produits qui ont l\'image fallback',
        )
        parser.add_argument(
            '--products-only',
            action='store_true',
            help='Traiter uniquement les produits',
        )
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='Traiter uniquement les categories',
        )

    def handle(self, *args, **kwargs):
        do_products   = not kwargs['categories_only']
        do_categories = not kwargs['products_only']

        # ── PRODUITS ──────────────────────────────────────────────────────────
        if do_products:
            self.stdout.write(self.style.MIGRATE_HEADING(
                '\n' + '=' * 42 + '\n  IMAGES PRODUITS\n' + '=' * 42
            ))

            if kwargs['all']:
                products = Product.objects.select_related('category').all()
            elif kwargs['retry_fallback']:
                products = Product.objects.select_related('category').filter(image_url=FALLBACK)
            else:
                products = Product.objects.select_related('category').filter(image_url__isnull=True)

            products = list(products)
            total = len(products)

            if total == 0:
                self.stdout.write(self.style.SUCCESS(
                    '  Tous les produits ont deja une image.\n'
                    '  Utilisez --all pour forcer le rechargement.'
                ))
            else:
                self.stdout.write(f'  {total} produits a traiter\n')
                success = fallback_count = 0

                for i, product in enumerate(products, 1):
                    name_safe = strip_accents(product.name)
                    self.stdout.write(f'\n  [{i}/{total}] {name_safe}')

                    query = get_product_query(product)
                    self.stdout.write(f'    Recherche : "{query}"')

                    image_url = fetch_image(
                        query,
                        orientation='squarish',
                        size_suffix='&w=600&q=80&fit=crop',
                    )

                    if image_url:
                        product.image_url = image_url
                        product.save(update_fields=['image_url'])
                        self.stdout.write(self.style.SUCCESS('    Image trouvee'))
                        success += 1
                    else:
                        product.image_url = FALLBACK
                        product.save(update_fields=['image_url'])
                        self.stdout.write(self.style.WARNING('    Fallback utilise'))
                        fallback_count += 1

                    if i < total:
                        time.sleep(2)

                self.stdout.write(self.style.SUCCESS(
                    f'\n  Produits : {success} images / {fallback_count} fallbacks / {total} total'
                ))

        # ── CATEGORIES ────────────────────────────────────────────────────────
        if do_categories:
            self.stdout.write(self.style.MIGRATE_HEADING(
                '\n' + '=' * 42 + '\n  IMAGES CATEGORIES\n' + '=' * 42
            ))

            categories = Category.objects.all() if kwargs['all'] else Category.objects.filter(image_url__isnull=True)
            categories = list(categories)
            total = len(categories)

            if total == 0:
                self.stdout.write(self.style.SUCCESS(
                    '  Toutes les categories ont deja une image.\n'
                    '  Utilisez --all pour forcer le rechargement.'
                ))
            else:
                self.stdout.write(f'  {total} categories a traiter\n')
                success = fallback_count = 0

                for i, cat in enumerate(categories, 1):
                    name_safe = strip_accents(cat.name)
                    query = get_category_query(cat)
                    self.stdout.write(f'\n  [{i}/{total}] {name_safe}')
                    self.stdout.write(f'    Recherche : "{query}"')

                    image_url = fetch_image(
                        query,
                        orientation='landscape',
                        size_suffix='&w=900&q=80&fit=crop',
                    )

                    if image_url:
                        cat.image_url = image_url
                        cat.save(update_fields=['image_url'])
                        self.stdout.write(self.style.SUCCESS('    Image trouvee'))
                        success += 1
                    else:
                        cat.image_url = None
                        cat.save(update_fields=['image_url'])
                        self.stdout.write(self.style.WARNING('    Aucune image trouvee'))
                        fallback_count += 1

                    if i < total:
                        time.sleep(2)

                self.stdout.write(self.style.SUCCESS(
                    f'\n  Categories : {success} images / {fallback_count} sans image / {total} total'
                ))

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n' + '=' * 42 + '\n  TERMINE\n' + '=' * 42
        ))
