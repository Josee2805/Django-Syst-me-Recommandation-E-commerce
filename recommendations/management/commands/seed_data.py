from django.core.management.base import BaseCommand
from recommendations.models import CustomUser, Category, Product, Rating
import random


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        CATEGORIES = [
            ('Électronique',    'electronique',   '💻', '#1a1a2e'),
            ('Mode & Vêtements','mode',           '👗', '#8B4513'),
            ('Maison & Déco',   'maison',         '🏠', '#2d6a4f'),
            ('Sport & Fitness', 'sport',          '⚽', '#d62828'),
            ('Beauté & Santé',  'beaute',         '💄', '#c77dff'),
            ('Livres & Culture','livres',         '📚', '#4361ee'),
            ('Cuisine & Food',  'cuisine',        '🍳', '#f4a261'),
            ('Jeux & Jouets',   'jeux',           '🎮', '#06d6a0'),
            ('Voyage & Outdoor','voyage',         '✈️',  '#0077b6'),
            ('Auto & Moto',     'auto',           '🚗', '#6c757d'),
            ('Bijoux & Luxe',   'bijoux',         '💎', '#D4AF37'),
            ('Bébé & Enfants',  'bebe',           '🍼', '#ffb3c6'),
        ]
        cats = {}
        for name, slug, icon, color in CATEGORIES:
            c, _ = Category.objects.get_or_create(slug=slug, defaults={
                'name': name, 'icon': icon, 'image_color': color
            })
            cats[slug] = c
        self.stdout.write(self.style.SUCCESS(f'✅ {len(cats)} catégories'))

        # (name, cat_slug, price, orig_price, emoji, color, desc, tags, brand, featured, image_url)
        PRODUCTS = [
            # ── Électronique ──
            ('iPhone 15 Pro',     'electronique', 650000, 700000, '📱', '#1a1a2e',
             'Puce A17 Pro, titane, 48MP ProRAW, Dynamic Island.',
             'apple,smartphone,ios,camera,pro',
             'Apple', True,
             'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&q=80'),

            ('Samsung Galaxy S24', 'electronique', 580000, None, '📱', '#1c1c2e',
             'Galaxy AI intégré, Snapdragon 8 Gen 3, écran 6.7".',
             'samsung,android,smartphone,ai,amoled',
             'Samsung', True,
             'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500&q=80'),

            ('MacBook Air M2',    'electronique', 950000, 1000000, '💻', '#2c2c2e',
             'Puce M2, 15h autonomie, écran Liquid Retina 13.6".',
             'apple,laptop,macos,m2,ultraportable',
             'Apple', True,
             'https://images.unsplash.com/photo-1611186871525-9be197a39a16?w=500&q=80'),

            ('AirPods Pro',       'electronique', 180000, None, '🎵', '#e8e8e8',
             'ANC adaptatif, audio spatial personnalisé, MagSafe.',
             'apple,earbuds,anc,audio,wireless',
             'Apple', False,
             'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500&q=80'),

            ('iPad Pro 12.9',     'electronique', 720000, None, '📱', '#3a3a3c',
             'Écran Liquid Retina XDR, puce M2, compatible Apple Pencil.',
             'apple,tablette,ipad,m2,pro',
             'Apple', False,
             'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500&q=80'),

            ('Sony WH-1000XM5',   'electronique', 220000, 260000, '🎧', '#1a1a1a',
             'Meilleure réduction de bruit du marché, 30h autonomie.',
             'sony,casque,audio,anc,hi-res',
             'Sony', False,
             'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80'),

            # ── Mode ──
            ('Nike Air Max 270',      'mode', 85000, 95000, '👟', '#ff6b35',
             'Coussin Air Max 270° pour un amorti exceptionnel.',
             'nike,sneakers,air,running,lifestyle',
             'Nike', True,
             'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80'),

            ('Adidas Stan Smith',      'mode', 65000, None, '👟', '#f5f5f5',
             'L\'icône du tennis devenue incontournable du streetwear.',
             'adidas,sneakers,classique,cuir,blanc',
             'Adidas', False,
             'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80'),

            ('Sac à main cuir',        'mode', 120000, 140000, '👜', '#5c3d2e',
             'Cuir pleine fleur tanné végétal, fermeture dorée.',
             'sac,cuir,femme,luxe,tote',
             'Maroquinerie', True,
             'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&q=80'),

            ('Montre classique homme', 'mode', 95000, None, '⌚', '#D4AF37',
             'Cadran guilloché, bracelet cuir brun, mouvement quartz.',
             'montre,homme,classique,or,cuir',
             'Horlogerie', False,
             'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'),

            ('Lunettes de soleil',     'mode', 35000, None, '😎', '#1a1a1a',
             'Monture acétate, verres polarisants UV400.',
             'lunettes,soleil,uv,style,acetate',
             'Optique', False,
             'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&q=80'),

            ('Veste en jean',          'mode', 45000, None, '🧥', '#1565C0',
             'Denim 100% coton, coupe droite, boutons dorés.',
             'jean,veste,denim,casual,vintage',
             'Denim Co.', False,
             'https://images.unsplash.com/photo-1601333144130-8cbb312386b6?w=500&q=80'),

            # ── Maison ──
            ('Lampe design LED',   'maison', 45000, None, '💡', '#D4AF37',
             'Structure métal doré, ampoule Edison, lumière chaude 2700K.',
             'lampe,led,deco,or,salon,design',
             'Déco Lumière', False,
             'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&q=80'),

            ('Cafetière premium',  'maison', 55000, 65000, '☕', '#2c1810',
             '15 bars, buse vapeur, bac 1.5L, café espresso parfait.',
             'cafe,expresso,machine,premium,barista',
             'CoffeeMaster', True,
             'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500&q=80'),

            ('Coussin décoratif',  'maison', 15000, None, '🛋️', '#a0522d',
             'Velours doux, 45×45cm, garnissage plumes recyclées.',
             'coussin,velours,deco,salon,confort',
             'Maison Textile', False,
             'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&q=80'),

            ("Plante d'intérieur", 'maison', 12000, None, '🌿', '#2d6a4f',
             'Facile d\'entretien, purifie l\'air, pot céramique inclus.',
             'plante,interieur,vert,deco,air',
             'Green Home', False,
             'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=500&q=80'),

            ('Bougie parfumée',    'maison', 8000, None, '🕯️', '#f5e6c8',
             'Cire de soja naturelle, 50h combustion, senteur vanille-bois.',
             'bougie,parfum,soja,ambiance,zen',
             'Parfums Maison', False,
             'https://images.unsplash.com/photo-1602928321679-560bb453f190?w=500&q=80'),

            ('Tapis berbère',      'maison', 75000, None, '🏠', '#a0522d',
             'Tissé main au Maroc, laine naturelle, motifs géométriques, 200×300cm.',
             'tapis,berbere,maroc,laine,artisanat',
             'Atlas Artisan', True,
             'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80'),

            # ── Sport ──
            ('Tapis de yoga',       'sport', 25000, None, '🧘', '#7B2D8B',
             'Caoutchouc naturel 6mm, antidérapant, marquages alignement.',
             'yoga,mat,fitness,bien-etre,antiderapant',
             'YogaLife', False,
             'https://images.unsplash.com/photo-1601925228957-7e5a4a0d3e1b?w=500&q=80'),

            ('Vélo de course',      'sport', 350000, 400000, '🚴', '#d62828',
             'Cadre aluminium allégé, 22 vitesses Shimano, freins disque.',
             'velo,course,route,shimano,carbon',
             'CyclePro', True,
             'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=500&q=80'),

            ('Haltères 10kg',       'sport', 40000, None, '🏋️', '#1a1a1a',
             'Paire 10kg, fonte chromée, grip antidérapant hexagonal.',
             'halteres,musculation,fonte,gym,force',
             'IronFit', False,
             'https://images.unsplash.com/photo-1585152968992-d2b9444408cc?w=500&q=80'),

            ('Montre GPS Garmin',   'sport', 180000, None, '⌚', '#1a1a2e',
             'GPS multiband, cardio poignet, 14 jours autonomie, running dynamics.',
             'garmin,montre,gps,running,sport',
             'Garmin', False,
             'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500&q=80'),

            ('Sac de sport Nike',   'sport', 35000, None, '🎒', '#1a1a2e',
             '35L, compartiment chaussures séparé, imperméable.',
             'nike,sac,sport,gym,training',
             'Nike', False,
             'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80'),

            ('Ballon de football',  'sport', 18000, None, '⚽', '#1a1a1a',
             'Taille 5, couture thermocollée, FIFA Quality Pro.',
             'football,ballon,sport,fifa,competition',
             'SportBall', False,
             'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=500&q=80'),

            # ── Beauté ──
            ('Parfum Chanel N°5',  'beaute', 150000, 170000, '🌸', '#f5e6c8',
             'L\'eau de parfum iconique depuis 1921. Floral aldéhydé, 100ml.',
             'parfum,chanel,floral,luxe,femme',
             'Chanel', True,
             'https://images.unsplash.com/photo-1541643600914-78b084683702?w=500&q=80'),

            ('Crème visage Nivea',  'beaute', 28000, None, '✨', '#c0c0c0',
             'Hydratation intense 24h, formule légère non grasse, tous types de peau.',
             'nivea,creme,hydratation,visage,soin',
             'Nivea', False,
             'https://images.unsplash.com/photo-1556228720-da4ef8ab9eed?w=500&q=80'),

            ('Palette maquillage',  'beaute', 32000, None, '💄', '#c77dff',
             '20 teintes harmonisées, finis mat & shimmer, longue tenue.',
             'maquillage,palette,yeux,ombre,shimmer',
             'MakeUp Pro', False,
             'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500&q=80'),

            ('Sérum Vitamin C',     'beaute', 22000, None, '🧴', '#f4a261',
             'Vitamine C 20% stabilisée, éclat immédiat, anti-taches, 30ml.',
             'serum,vitaminec,eclat,antiage,soin',
             'The Ordinary', False,
             'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&q=80'),

            ('Rouge à lèvres MAC',  'beaute', 18000, None, '💄', '#8B0000',
             'Formule crémeuse longue tenue, couleur intense, 50 teintes.',
             'mac,rouge,levres,maquillage,couleur',
             'MAC', False,
             'https://images.unsplash.com/photo-1586495777744-4e6232bf2e79?w=500&q=80'),

            ("Huile d'argan bio",   'beaute', 12000, None, '🌿', '#D4AF37',
             '100% pure, première pression à froid, certifiée bio, 50ml.',
             'argan,huile,bio,soin,naturel',
             'Argan Pur', False,
             'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500&q=80'),
        ]
        created = updated = 0
        for data in PRODUCTS:
            name, cat_slug, price, orig, emoji, color, desc, tags, brand, featured, image_url = data
            obj, c = Product.objects.update_or_create(
                name=name,
                defaults={
                    'category': cats[cat_slug], 'price': price, 'original_price': orig,
                    'image_emoji': emoji, 'image_color': color, 'description': desc,
                    'tags': tags, 'brand': brand, 'is_featured': featured,
                    'image_url': image_url,
                    'stock': random.randint(10, 200),
                }
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {created} produits créés, {updated} mis à jour'))

        # (email, username, password, gender, interests, budget, priority)
        USERS = [
            ('alice@luxemart.com',  'Alice',     'pass1234', 'femme',  'mode,beaute,maison',         'moyen',    'qualite'),
            ('bob@luxemart.com',    'Bob',        'pass1234', 'homme',  'electronique,sport,jeux',    'illimite', 'nouveautes'),
            ('clara@luxemart.com',  'Clara',      'pass1234', 'femme',  'beaute,mode,alimentation',   'petit',    'prix'),
            ('david@luxemart.com',  'David',      'pass1234', 'homme',  'electronique,maison',        'moyen',    'qualite'),
            ('emma@luxemart.com',   'Emma',       'pass1234', 'femme',  'sport,alimentation,beaute',  'moyen',    'promotions'),
            ('farid@luxemart.com',  'Farid',      'pass1234', 'homme',  'electronique,sport',         'illimite', 'qualite'),
            ('grace@luxemart.com',  'Grace',      'pass1234', 'femme',  'mode,maison,beaute',         'moyen',    'nouveautes'),
            ('hassan@luxemart.com', 'Hassan',     'pass1234', 'homme',  'sport,electronique',         'petit',    'prix'),
            ('demo@luxemart.com',   'Demo User',  'demo1234', 'homme',  'electronique,mode',          'moyen',    'qualite'),
        ]
        users = []
        for email, username, password, gender, interests, budget, priority in USERS:
            u, created = CustomUser.objects.get_or_create(email=email, defaults={'username': username})
            if created:
                u.set_password(password)
            u.gender = gender
            u.interests = interests
            u.budget = budget
            u.purchase_priority = priority
            u.onboarding_done = True
            u.save()
            users.append(u)
        self.stdout.write(self.style.SUCCESS(f'✅ {len(users)} utilisateurs'))

        all_products = list(Product.objects.all())
        rc = 0
        for user in users:
            sample = random.sample(all_products, min(20, len(all_products)))
            for product in sample:
                score = random.choices([1,2,3,4,5], weights=[5,10,20,35,30])[0]
                _, c = Rating.objects.get_or_create(user=user, product=product, defaults={'score': score})
                if c: rc += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {rc} notes créées'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Seed terminé ! Compte démo: demo@luxemart.com / demo1234'))
