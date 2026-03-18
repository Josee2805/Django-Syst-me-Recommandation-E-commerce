"""
Run with: python manage.py shell < recommendations/seed.py
OR add a management command.
"""
import os, django, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_reco.settings')
django.setup()

from recommendations.models import CustomUser, Category, Product, Rating

# ── CATEGORIES ──────────────────────────────────────────────────────────────
CATEGORIES = [
    ('Électronique',    'electronique',   '💻', '#1a1a2e', 'Smartphones, laptops, gadgets & tech'),
    ('Mode & Vêtements','mode',           '👗', '#8B4513', 'Tendances mode homme, femme & enfants'),
    ('Maison & Déco',   'maison',         '🏠', '#2d6a4f', 'Meubles, décoration & art de vivre'),
    ('Sport & Fitness', 'sport',          '⚽', '#d62828', 'Équipements sportifs & bien-être'),
    ('Beauté & Santé',  'beaute',         '💄', '#c77dff', 'Cosmétiques, soins & parfums'),
    ('Livres & Culture','livres',         '📚', '#4361ee', 'Romans, BD, art & musique'),
    ('Cuisine & Food',  'cuisine',        '🍳', '#f4a261', 'Ustensiles, épices & gourmandises'),
    ('Jeux & Jouets',   'jeux',           '🎮', '#06d6a0', 'Gaming, jeux de société & jouets'),
    ('Voyage & Outdoor','voyage',         '✈️',  '#0077b6', 'Bagages, camping & aventure'),
    ('Auto & Moto',     'auto',           '🚗', '#6c757d', 'Accessoires & équipements auto'),
    ('Bijoux & Luxe',   'bijoux',         '💎', '#D4AF37', 'Or, argent, montres & maroquinerie'),
    ('Bébé & Enfants',  'bebe',           '🍼', '#ffb3c6', 'Puériculture, vêtements & jouets'),
]

cats = {}
for name, slug, icon, color, desc in CATEGORIES:
    c, _ = Category.objects.get_or_create(slug=slug, defaults={
        'name': name, 'icon': icon, 'image_color': color, 'description': desc
    })
    cats[slug] = c
print(f"✅ {len(cats)} catégories créées")

# ── PRODUCTS ────────────────────────────────────────────────────────────────
PRODUCTS = [
    # Électronique
    ('iPhone 15 Pro Max', 'electronique', 1599.99, 1799.99, '📱', '#1a1a2e',
     'Dernier flagship Apple avec puce A17 Pro, appareil photo 48MP, titane.',
     'apple,smartphone,ios,camera,pro', 'Apple', True),
    ('Samsung Galaxy S24 Ultra', 'electronique', 1399.99, 1499.99, '📱', '#1c1c2e',
     'Galaxy AI, stylet S Pen intégré, écran 6.8" Dynamic AMOLED.',
     'samsung,android,smartphone,stylus,ai', 'Samsung', True),
    ('MacBook Pro M3', 'electronique', 2499.99, None, '💻', '#2c2c2e',
     'Puce M3 Ultra, 18h d\'autonomie, écran Liquid Retina XDR.',
     'apple,laptop,macos,m3,pro', 'Apple', True),
    ('Sony WH-1000XM5', 'electronique', 349.99, 399.99, '🎧', '#1a1a1a',
     'Meilleure réduction de bruit, 30h autonomie, audio Hi-Res.',
     'sony,casque,audio,anc,bluetooth', 'Sony', False),
    ('iPad Pro 12.9"', 'electronique', 1199.99, None, '📱', '#3a3a3c',
     'Écran Liquid Retina XDR, puce M2, compatible Apple Pencil.',
     'apple,tablette,ipad,m2,creative', 'Apple', False),
    ('Dell XPS 15', 'electronique', 1899.99, 2100.00, '💻', '#0f0f23',
     'Intel Core i9, RTX 4070, écran OLED 3.5K touche.',
     'dell,laptop,windows,gaming,oled', 'Dell', False),
    ('AirPods Pro 2', 'electronique', 279.99, 299.99, '🎵', '#e8e8e8',
     'Suppression active du bruit, audio spatial, charge MagSafe.',
     'apple,earbuds,anc,audio,wireless', 'Apple', False),
    ('Samsung 65" QLED 4K', 'electronique', 999.99, 1299.99, '📺', '#121212',
     'Neo QLED, 144Hz, HDR2000, parfait pour gaming et cinéma.',
     'samsung,tv,qled,4k,gaming', 'Samsung', False),
    ('GoPro Hero 12', 'electronique', 449.99, None, '📷', '#1a1a1a',
     'Vidéo 5.3K, stabilisation HyperSmooth 6.0, waterproof 10m.',
     'gopro,camera,action,video,waterproof', 'GoPro', False),
    ('Dyson V15 Detect', 'electronique', 699.99, 749.99, '🌀', '#d4af37',
     'Aspirateur sans fil avec laser détecteur de poussière.',
     'dyson,aspirateur,laser,cordless,clean', 'Dyson', False),

    # Mode
    ('Veste en cuir vintage', 'mode', 299.99, 399.99, '🧥', '#3d1c02',
     'Cuir véritable, coupe cintrée, style biker intemporel.',
     'cuir,veste,fashion,vintage,leather', 'Zara', True),
    ('Robe de soirée dorée', 'mode', 189.99, 249.99, '👗', '#D4AF37',
     'Tissu lamé doré, coupe midi, idéale pour les soirées de gala.',
     'robe,soiree,or,elegant,fashion', 'H&M', True),
    ('Sneakers Air Max 270', 'mode', 149.99, 169.99, '👟', '#ff6b35',
     'Coussin Air Max visible, semelle respirante, design iconique.',
     'nike,sneakers,air,running,sport', 'Nike', True),
    ('Costume 3 pièces slim', 'mode', 399.99, 499.99, '👔', '#1a1a2e',
     'Laine mérinos, coupe slim moderne, couleur navy.',
     'costume,slim,business,formal,suit', 'Hugo Boss', False),
    ('Sac à main Tote premium', 'mode', 229.99, None, '👜', '#5c3d2e',
     'Cuir grainé, fermeture dorée, intérieur velours.',
     'sac,tote,cuir,femme,fashion', 'Michael Kors', False),
    ('Jean slim déchiré', 'mode', 89.99, 119.99, '👖', '#1565C0',
     'Denim stretch, coupe slim, effet used authentique.',
     'jean,denim,slim,casual,homme', 'Levi\'s', False),
    ('Écharpe cachemire', 'mode', 159.99, 199.99, '🧣', '#8B0000',
     '100% cachemire mongol, tissé à la main, 180x30cm.',
     'echarpe,cachemire,luxe,winter,doux', 'Loro Piana', False),
    ('Chaussures Oxford', 'mode', 199.99, 249.99, '👞', '#3d1c02',
     'Cuir poli, semelle Goodyear welt, coloris cognac.',
     'chaussures,oxford,cuir,classique,homme', 'Clarks', False),

    # Maison
    ('Canapé panoramique', 'maison', 1299.99, 1599.99, '🛋️', '#a0522d',
     'Tissu chenille, 5 places, pieds chêne naturel.',
     'canape,salon,confort,design,maison', 'IKEA', True),
    ('Lampe de sol arc doré', 'maison', 349.99, 399.99, '💡', '#D4AF37',
     'Structure acier doré, abat-jour velours, hauteur 180cm.',
     'lampe,deco,or,salon,luminaire', 'Maisons du Monde', True),
    ('Miroir baroque ovale', 'maison', 279.99, 329.99, '🪞', '#D4AF37',
     'Cadre résine dorée, 80x120cm, effet vieilli élégant.',
     'miroir,baroque,or,deco,elegant', 'Maisons du Monde', False),
    ('Literie 1000 fils', 'maison', 189.99, 249.99, '🛏️', '#f5f5f5',
     'Coton égyptien 1000 fils, blanc ivoire, taille 180x200.',
     'literie,coton,luxe,blanc,dodo', 'Descamps', False),
    ('Cuisine modulaire', 'maison', 2499.99, None, '🍴', '#2d6a4f',
     'Portes laquées blanc mat, poignées or, plan granit noir.',
     'cuisine,modulaire,blanc,or,premium', 'Leroy Merlin', False),
    ('Plante monstera XL', 'maison', 89.99, None, '🌿', '#2d6a4f',
     'Monstera deliciosa, pot céramique blanc, hauteur 120cm.',
     'plante,monstera,vert,deco,natural', 'Fleur de Paris', False),

    # Sport
    ('Vélo électrique Urban', 'sport', 1499.99, 1799.99, '🚴', '#d62828',
     'Moteur 250W, batterie 504Wh, autonomie 100km, freins hydrauliques.',
     'velo,electrique,urban,ebike,sport', 'Trek', True),
    ('Tapis de course Pro', 'sport', 899.99, 1099.99, '🏃', '#1a1a1a',
     '22km/h max, inclinaison -3/+15%, écran 10" connecté.',
     'tapis,course,running,fitness,cardio', 'Technogym', True),
    ('Kettlebell set 5-30kg', 'sport', 299.99, None, '🏋️', '#1a1a1a',
     'Fonte émaillée, surface antidérapante, 6 paires incluses.',
     'kettlebell,musculation,fonte,fitness,gym', 'Cap Barbell', False),
    ('Yoga mat premium', 'sport', 89.99, 119.99, '🧘', '#7B2D8B',
     'Caoutchouc naturel, 6mm, antidérapant, sangle de transport.',
     'yoga,mat,bien-etre,fitness,relaxation', 'Manduka', False),
    ('Montre Garmin Fenix 7', 'sport', 699.99, 799.99, '⌚', '#1a1a2e',
     'GPS multiband, 18 jours autonomie, suivi 30+ sports.',
     'garmin,montre,gps,running,triathlon', 'Garmin', False),

    # Beauté
    ('Parfum N°5 Chanel', 'beaute', 189.99, None, '🌸', '#f5e6c8',
     'Eau de parfum iconique, flacon 100ml, aldehydique floral.',
     'parfum,chanel,floral,luxe,femme', 'Chanel', True),
    ('Crème La Mer', 'beaute', 299.99, None, '✨', '#c0c0c0',
     'Crème Miracle Broth, 60ml, anti-âge, hydratation intense.',
     'creme,lamer,antiage,soin,luxe', 'La Mer', True),
    ('Palette Natasha Denona', 'beaute', 149.99, None, '💄', '#c77dff',
     '15 fards yeux, mixte mat/shimmer, pigmentation pro.',
     'maquillage,palette,yeux,pro,couleur', 'Natasha Denona', False),
    ('Sérum Vitamin C', 'beaute', 69.99, 89.99, '🧴', '#f4a261',
     'Vitamine C 20%, acide hyaluronique, éclat & fermeté.',
     'serum,vitaminec,soin,eclat,anti-age', 'Ordinary', False),

    # Livres
    ('Atomic Habits', 'livres', 19.99, None, '📖', '#4361ee',
     'James Clear. Comment créer de bonnes habitudes et éliminer les mauvaises.',
     'livre,habits,productivite,development,bestseller', 'Gallimard', True),
    ('Sapiens', 'livres', 24.99, None, '🌍', '#2b2d42',
     'Yuval Noah Harari. Une brève histoire de l\'humanité.',
     'livre,histoire,humanite,sapiens,bestseller', 'Albin Michel', True),
    ('Dune', 'livres', 18.99, None, '🏜️', '#c9b458',
     'Frank Herbert. L\'épopée science-fiction intégrale.',
     'livre,scifi,dune,aventure,fantasy', 'Robert Laffont', False),
    ('Apprendre Django', 'livres', 39.99, None, '💻', '#4361ee',
     'Guide complet du développement web avec Django 4.x.',
     'livre,django,python,dev,programmation', 'O\'Reilly', False),

    # Cuisine
    ('Robot KitchenAid', 'cuisine', 599.99, 699.99, '🍰', '#d62828',
     'Robot pâtissier 6.9L, 10 vitesses, bol inox, rouge empire.',
     'kitchenaid,robot,patisserie,boulangerie,rouge', 'KitchenAid', True),
    ('Wok en fonte', 'cuisine', 129.99, 159.99, '🥘', '#1a1a1a',
     'Wok en fonte émaillée, 32cm, couvercle inclus, toutes plaques.',
     'wok,fonte,cuisine,asiatique,cuisson', 'Le Creuset', False),
    ('Machine Nespresso Vertuo', 'cuisine', 179.99, 219.99, '☕', '#2c1810',
     'Capsules Vertuo, 5 tailles de café, carafe 535ml.',
     'cafe,nespresso,vertuo,machine,expresso', 'Nespresso', False),
    ('Couteaux Wusthof set 7', 'cuisine', 349.99, None, '🔪', '#c0c0c0',
     'Acier inox Allemand X50CrMoV15, manche triple rivets, coffret.',
     'couteaux,wusthof,inox,chef,cuisine', 'Wüsthof', False),

    # Jeux
    ('PlayStation 5', 'jeux', 499.99, None, '🎮', '#003087',
     'Console PS5, manette DualSense, SSD ultra-rapide, 4K/120fps.',
     'ps5,console,gaming,sony,4k', 'Sony', True),
    ('Nintendo Switch OLED', 'jeux', 349.99, None, '🕹️', '#e4000f',
     'Écran OLED 7", dock Ethernet, manettes Joy-Con améliorés.',
     'nintendo,switch,oled,portable,gaming', 'Nintendo', True),
    ('LEGO Technic Ferrari', 'jeux', 399.99, None, '🏎️', '#e4000f',
     '1677 pièces, Ferrari 488 GTE à l\'échelle, motorisée.',
     'lego,technic,ferrari,construction,adulte', 'LEGO', False),
    ('Monopoly édition luxe', 'jeux', 79.99, None, '🎲', '#D4AF37',
     'Plateau bois, pions métal dorés, pièces en bois, boîte coffret.',
     'monopoly,jeu,famille,luxe,classique', 'Hasbro', False),

    # Voyage
    ('Valise Rimowa Original', 'voyage', 799.99, 899.99, '🧳', '#c0c0c0',
     'Aluminium, 4 roues multiaxiales, serrure TSA, 45L.',
     'rimowa,valise,aluminium,voyage,luxe', 'Rimowa', True),
    ('Sac à dos Osprey 65L', 'voyage', 289.99, 329.99, '🎒', '#1a5276',
     'Randonnée 65L, cadre aluminium, hip belt, anti-rain.',
     'osprey,sac,randonnee,trekking,outdoor', 'Osprey', False),
    ('Tente 4 saisons', 'voyage', 499.99, 599.99, '⛺', '#2d6a4f',
     'Double paroi, résiste -30°C, montage rapide 5 min.',
     'tente,camping,outdoor,randonnee,hiver', 'Mountain Hardwear', False),

    # Bijoux
    ('Montre Rolex Submariner', 'bijoux', 12999.99, None, '⌚', '#D4AF37',
     'Acier 904L, lunette céramique noire, bracelet Oyster, 300m.',
     'rolex,montre,luxe,submariner,or', 'Rolex', True),
    ('Collier diamant or blanc', 'bijoux', 2499.99, None, '💎', '#f5f5f5',
     'Or blanc 18 carats, diamant central 0.5ct, certificat GIA.',
     'collier,diamant,or,luxe,bijou', 'Cartier', True),
    ('Bracelet jonc or jaune', 'bijoux', 899.99, None, '💛', '#D4AF37',
     'Or jaune 18K, finition brossée, diamètre 60mm.',
     'bracelet,jonc,or,bijou,luxe', 'Bulgari', False),

    # Auto
    ('Dashcam 4K Sony', 'auto', 199.99, 249.99, '📷', '#1a1a2e',
     'Capteur Sony 4K, vision nocturne, GPS intégré, WiFi.',
     'dashcam,4k,camera,voiture,securite', 'Vantrue', False),
    ('Siège baquet sport', 'auto', 399.99, None, '🏁', '#d62828',
     'Baquet FIA, harnais 4 points, mousse haute densité, rouge.',
     'siege,baquet,sport,auto,feu', 'Sparco', False),

    # Bébé
    ('Poussette Bugaboo', 'bebe', 1099.99, 1299.99, '👶', '#ffb3c6',
     'Bugaboo Fox 5, suspension all-terrain, compatible siège auto.',
     'poussette,bebe,bugaboo,premium,confort', 'Bugaboo', True),
    ('Lit bébé évolutif', 'bebe', 399.99, 499.99, '🛏️', '#fff3e0',
     'Convertible berceau → lit enfant → banquette, bois massif.',
     'lit,bebe,evolutif,bois,naturel', 'Stokke', False),
]

created_count = 0
for data in PRODUCTS:
    name, cat_slug, price, orig_price, emoji, color, desc, tags, brand, featured = data
    p, created = Product.objects.get_or_create(name=name, defaults={
        'category': cats[cat_slug],
        'price': price,
        'original_price': orig_price,
        'image_emoji': emoji,
        'image_color': color,
        'description': desc,
        'tags': tags,
        'brand': brand,
        'is_featured': featured,
        'stock': random.randint(10, 200),
    })
    if created:
        created_count += 1

print(f"✅ {created_count} produits créés")

# ── USERS ───────────────────────────────────────────────────────────────────
USERS = [
    ('alice@luxemart.com', 'Alice', 'pass1234'),
    ('bob@luxemart.com', 'Bob', 'pass1234'),
    ('clara@luxemart.com', 'Clara', 'pass1234'),
    ('david@luxemart.com', 'David', 'pass1234'),
    ('emma@luxemart.com', 'Emma', 'pass1234'),
    ('farid@luxemart.com', 'Farid', 'pass1234'),
    ('grace@luxemart.com', 'Grace', 'pass1234'),
    ('hassan@luxemart.com', 'Hassan', 'pass1234'),
    ('ines@luxemart.com', 'Ines', 'pass1234'),
    ('julien@luxemart.com', 'Julien', 'pass1234'),
    ('demo@luxemart.com', 'Demo User', 'demo1234'),
]

users = []
for email, username, password in USERS:
    u, created = CustomUser.objects.get_or_create(email=email, defaults={
        'username': username
    })
    if created:
        u.set_password(password)
        u.save()
    users.append(u)

print(f"✅ {len(users)} utilisateurs créés")

# ── RATINGS ──────────────────────────────────────────────────────────────────
all_products = list(Product.objects.all())
rating_count = 0

# Each user rates 15-25 random products
for user in users:
    sample_products = random.sample(all_products, min(20, len(all_products)))
    for product in sample_products:
        score = random.choices([1,2,3,4,5], weights=[5,10,20,35,30])[0]
        Rating.objects.get_or_create(user=user, product=product, defaults={'score': score})
        rating_count += 1

print(f"✅ {rating_count} notes créées")
print("\n🎉 Seed terminé ! Compte démo: demo@luxemart.com / demo1234")
