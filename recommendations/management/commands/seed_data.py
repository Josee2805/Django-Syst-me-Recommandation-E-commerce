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

        PRODUCTS = [
            ('iPhone 15 Pro Max', 'electronique', 1599.99, 1799.99, '📱', '#1a1a2e', 'Dernier flagship Apple avec puce A17 Pro.', 'apple,smartphone,ios,camera', 'Apple', True),
            ('Samsung Galaxy S24 Ultra', 'electronique', 1399.99, 1499.99, '📱', '#1c1c2e', 'Galaxy AI, stylet S Pen intégré.', 'samsung,android,smartphone,ai', 'Samsung', True),
            ('MacBook Pro M3', 'electronique', 2499.99, None, '💻', '#2c2c2e', 'Puce M3 Ultra, 18h autonomie.', 'apple,laptop,macos,m3', 'Apple', True),
            ('Sony WH-1000XM5', 'electronique', 349.99, 399.99, '🎧', '#1a1a1a', 'Meilleure réduction de bruit 30h.', 'sony,casque,audio,anc', 'Sony', False),
            ('iPad Pro 12.9"', 'electronique', 1199.99, None, '📱', '#3a3a3c', 'Écran Liquid Retina XDR, puce M2.', 'apple,tablette,ipad,m2', 'Apple', False),
            ('Dell XPS 15', 'electronique', 1899.99, 2100.00, '💻', '#0f0f23', 'Intel Core i9, RTX 4070, OLED.', 'dell,laptop,windows,gaming', 'Dell', False),
            ('AirPods Pro 2', 'electronique', 279.99, 299.99, '🎵', '#e8e8e8', 'ANC, audio spatial, MagSafe.', 'apple,earbuds,anc,audio', 'Apple', False),
            ('Samsung 65" QLED 4K', 'electronique', 999.99, 1299.99, '📺', '#121212', 'Neo QLED, 144Hz, HDR2000.', 'samsung,tv,qled,4k', 'Samsung', False),
            ('GoPro Hero 12', 'electronique', 449.99, None, '📷', '#1a1a1a', 'Vidéo 5.3K, HyperSmooth 6.0.', 'gopro,camera,action,video', 'GoPro', False),
            ('Dyson V15 Detect', 'electronique', 699.99, 749.99, '🌀', '#d4af37', 'Aspirateur laser détecteur.', 'dyson,aspirateur,laser,cordless', 'Dyson', False),
            ('Veste en cuir vintage', 'mode', 299.99, 399.99, '🧥', '#3d1c02', 'Cuir véritable, coupe cintrée biker.', 'cuir,veste,fashion,vintage', 'Zara', True),
            ('Robe de soirée dorée', 'mode', 189.99, 249.99, '👗', '#D4AF37', 'Tissu lamé doré, coupe midi.', 'robe,soiree,or,elegant', 'H&M', True),
            ('Sneakers Air Max 270', 'mode', 149.99, 169.99, '👟', '#ff6b35', 'Coussin Air Max, design iconique.', 'nike,sneakers,air,running', 'Nike', True),
            ('Costume 3 pièces slim', 'mode', 399.99, 499.99, '👔', '#1a1a2e', 'Laine mérinos, coupe slim navy.', 'costume,slim,business,formal', 'Hugo Boss', False),
            ('Sac à main Tote premium', 'mode', 229.99, None, '👜', '#5c3d2e', 'Cuir grainé, fermeture dorée.', 'sac,tote,cuir,femme', 'Michael Kors', False),
            ('Jean slim déchiré', 'mode', 89.99, 119.99, '👖', '#1565C0', 'Denim stretch, effet used.', 'jean,denim,slim,casual', "Levi's", False),
            ('Écharpe cachemire', 'mode', 159.99, 199.99, '🧣', '#8B0000', '100% cachemire mongol, 180x30cm.', 'echarpe,cachemire,luxe,winter', 'Loro Piana', False),
            ('Chaussures Oxford', 'mode', 199.99, 249.99, '👞', '#3d1c02', 'Cuir poli, Goodyear welt, cognac.', 'chaussures,oxford,cuir,classique', 'Clarks', False),
            ('Canapé panoramique', 'maison', 1299.99, 1599.99, '🛋️', '#a0522d', 'Tissu chenille, 5 places, chêne.', 'canape,salon,confort,design', 'IKEA', True),
            ('Lampe de sol arc doré', 'maison', 349.99, 399.99, '💡', '#D4AF37', 'Structure acier doré, velours 180cm.', 'lampe,deco,or,salon', 'Maisons du Monde', True),
            ('Miroir baroque ovale', 'maison', 279.99, 329.99, '🪞', '#D4AF37', 'Cadre résine dorée, 80x120cm.', 'miroir,baroque,or,deco', 'Maisons du Monde', False),
            ('Literie 1000 fils', 'maison', 189.99, 249.99, '🛏️', '#f5f5f5', 'Coton égyptien 1000 fils, ivoire.', 'literie,coton,luxe,blanc', 'Descamps', False),
            ('Plante monstera XL', 'maison', 89.99, None, '🌿', '#2d6a4f', 'Pot céramique blanc, hauteur 120cm.', 'plante,monstera,vert,deco', 'Fleur de Paris', False),
            ('Vélo électrique Urban', 'sport', 1499.99, 1799.99, '🚴', '#d62828', 'Moteur 250W, 100km, hydraulique.', 'velo,electrique,urban,ebike', 'Trek', True),
            ('Tapis de course Pro', 'sport', 899.99, 1099.99, '🏃', '#1a1a1a', '22km/h max, inclinaison ±15%.', 'tapis,course,running,fitness', 'Technogym', True),
            ('Kettlebell set 5-30kg', 'sport', 299.99, None, '🏋️', '#1a1a1a', 'Fonte émaillée, 6 paires.', 'kettlebell,musculation,fonte,gym', 'Cap Barbell', False),
            ('Yoga mat premium', 'sport', 89.99, 119.99, '🧘', '#7B2D8B', 'Caoutchouc naturel 6mm, antidérap.', 'yoga,mat,bien-etre,fitness', 'Manduka', False),
            ('Montre Garmin Fenix 7', 'sport', 699.99, 799.99, '⌚', '#1a1a2e', 'GPS multiband, 18j autonomie.', 'garmin,montre,gps,running', 'Garmin', False),
            ('Parfum N°5 Chanel', 'beaute', 189.99, None, '🌸', '#f5e6c8', 'Eau de parfum 100ml, floral.', 'parfum,chanel,floral,luxe', 'Chanel', True),
            ('Crème La Mer', 'beaute', 299.99, None, '✨', '#c0c0c0', 'Miracle Broth 60ml, anti-âge.', 'creme,lamer,antiage,soin', 'La Mer', True),
            ('Palette Natasha Denona', 'beaute', 149.99, None, '💄', '#c77dff', '15 fards yeux, mat/shimmer pro.', 'maquillage,palette,yeux,pro', 'Natasha Denona', False),
            ('Sérum Vitamin C', 'beaute', 69.99, 89.99, '🧴', '#f4a261', 'Vitamine C 20%, éclat & fermeté.', 'serum,vitaminec,soin,eclat', 'The Ordinary', False),
            ('Atomic Habits', 'livres', 19.99, None, '📖', '#4361ee', 'James Clear. Bonnes habitudes.', 'livre,habits,productivite,bestseller', 'Gallimard', True),
            ('Sapiens', 'livres', 24.99, None, '🌍', '#2b2d42', 'Yuval Harari. Histoire humanité.', 'livre,histoire,humanite,bestseller', 'Albin Michel', True),
            ('Dune', 'livres', 18.99, None, '🏜️', '#c9b458', 'Frank Herbert. Épopée science-fiction.', 'livre,scifi,dune,aventure', 'Robert Laffont', False),
            ('Apprendre Django', 'livres', 39.99, None, '💻', '#4361ee', 'Guide complet Django 4.x.', 'livre,django,python,dev', "O'Reilly", False),
            ('Robot KitchenAid', 'cuisine', 599.99, 699.99, '🍰', '#d62828', 'Robot 6.9L, 10 vitesses, rouge.', 'kitchenaid,robot,patisserie,rouge', 'KitchenAid', True),
            ('Wok en fonte', 'cuisine', 129.99, 159.99, '🥘', '#1a1a1a', 'Fonte émaillée 32cm, couvercle.', 'wok,fonte,cuisine,asiatique', 'Le Creuset', False),
            ('Machine Nespresso Vertuo', 'cuisine', 179.99, 219.99, '☕', '#2c1810', 'Capsules Vertuo, 5 tailles café.', 'cafe,nespresso,vertuo,machine', 'Nespresso', False),
            ('Couteaux Wusthof set 7', 'cuisine', 349.99, None, '🔪', '#c0c0c0', 'Acier X50CrMoV15, 7 pièces.', 'couteaux,wusthof,inox,chef', 'Wüsthof', False),
            ('PlayStation 5', 'jeux', 499.99, None, '🎮', '#003087', 'Console PS5, DualSense, 4K/120fps.', 'ps5,console,gaming,sony,4k', 'Sony', True),
            ('Nintendo Switch OLED', 'jeux', 349.99, None, '🕹️', '#e4000f', 'OLED 7", Joy-Con améliorés.', 'nintendo,switch,oled,portable', 'Nintendo', True),
            ('LEGO Technic Ferrari', 'jeux', 399.99, None, '🏎️', '#e4000f', '1677 pièces, Ferrari 488 GTE.', 'lego,technic,ferrari,adulte', 'LEGO', False),
            ('Monopoly édition luxe', 'jeux', 79.99, None, '🎲', '#D4AF37', 'Plateau bois, pions métal dorés.', 'monopoly,jeu,famille,luxe', 'Hasbro', False),
            ('Valise Rimowa Original', 'voyage', 799.99, 899.99, '🧳', '#c0c0c0', 'Aluminium, 4 roues, TSA, 45L.', 'rimowa,valise,aluminium,luxe', 'Rimowa', True),
            ('Sac à dos Osprey 65L', 'voyage', 289.99, 329.99, '🎒', '#1a5276', 'Randonnée 65L, cadre alu.', 'osprey,sac,randonnee,trekking', 'Osprey', False),
            ('Tente 4 saisons', 'voyage', 499.99, 599.99, '⛺', '#2d6a4f', 'Double paroi, -30°C, 5 min montage.', 'tente,camping,outdoor,hiver', 'Mountain Hardwear', False),
            ('Montre Rolex Submariner', 'bijoux', 12999.99, None, '⌚', '#D4AF37', 'Acier 904L, céramique noire, 300m.', 'rolex,montre,luxe,submariner', 'Rolex', True),
            ('Collier diamant or blanc', 'bijoux', 2499.99, None, '💎', '#f5f5f5', 'Or blanc 18K, diamant 0.5ct GIA.', 'collier,diamant,or,luxe', 'Cartier', True),
            ('Bracelet jonc or jaune', 'bijoux', 899.99, None, '💛', '#D4AF37', 'Or jaune 18K, brossé, ø60mm.', 'bracelet,jonc,or,bijou', 'Bulgari', False),
            ('Dashcam 4K Sony', 'auto', 199.99, 249.99, '📷', '#1a1a2e', 'Capteur Sony 4K, GPS, WiFi.', 'dashcam,4k,camera,voiture', 'Vantrue', False),
            ('Siège baquet sport', 'auto', 399.99, None, '🏁', '#d62828', 'Baquet FIA, harnais 4pts, rouge.', 'siege,baquet,sport,auto', 'Sparco', False),
            ('Poussette Bugaboo', 'bebe', 1099.99, 1299.99, '👶', '#ffb3c6', 'Fox 5, all-terrain, siège auto.', 'poussette,bebe,bugaboo,premium', 'Bugaboo', True),
            ('Lit bébé évolutif', 'bebe', 399.99, 499.99, '🛏️', '#fff3e0', 'Berceau→lit→banquette, bois massif.', 'lit,bebe,evolutif,bois', 'Stokke', False),
        ]
        created = 0
        for data in PRODUCTS:
            name, cat_slug, price, orig, emoji, color, desc, tags, brand, featured = data
            _, c = Product.objects.get_or_create(name=name, defaults={
                'category': cats[cat_slug], 'price': price, 'original_price': orig,
                'image_emoji': emoji, 'image_color': color, 'description': desc,
                'tags': tags, 'brand': brand, 'is_featured': featured,
                'stock': random.randint(10, 200),
            })
            if c: created += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {created} produits créés'))

        USERS = [
            ('alice@luxemart.com', 'Alice', 'pass1234'),
            ('bob@luxemart.com', 'Bob', 'pass1234'),
            ('clara@luxemart.com', 'Clara', 'pass1234'),
            ('david@luxemart.com', 'David', 'pass1234'),
            ('emma@luxemart.com', 'Emma', 'pass1234'),
            ('farid@luxemart.com', 'Farid', 'pass1234'),
            ('grace@luxemart.com', 'Grace', 'pass1234'),
            ('hassan@luxemart.com', 'Hassan', 'pass1234'),
            ('demo@luxemart.com', 'Demo User', 'demo1234'),
        ]
        users = []
        for email, username, password in USERS:
            u, created = CustomUser.objects.get_or_create(email=email, defaults={'username': username})
            if created:
                u.set_password(password)
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
