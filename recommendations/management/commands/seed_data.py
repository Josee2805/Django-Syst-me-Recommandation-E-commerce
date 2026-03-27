from django.core.management.base import BaseCommand
from recommendations.models import CustomUser, Category, Product, Rating
import random


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        CATEGORIES = [
            ('Électronique',    'electronique',   '💻', '#1a1a2e',
             'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&q=80'),
            ('Mode & Vêtements','mode',           '👗', '#8B4513',
             'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&q=80'),
            ('Maison & Déco',   'maison',         '🏠', '#2d6a4f',
             'https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=600&q=80'),
            ('Sport & Fitness', 'sport',          '⚽', '#d62828',
             'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&q=80'),
            ('Beauté & Santé',  'beaute',         '💄', '#c77dff',
             'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&q=80'),
            ('Livres & Culture','livres',         '📚', '#4361ee',
             'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=600&q=80'),
            ('Cuisine & Food',  'cuisine',        '🍳', '#f4a261',
             'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&q=80'),
            ('Jeux & Jouets',   'jeux',           '🎮', '#06d6a0',
             'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=600&q=80'),
            ('Voyage & Outdoor','voyage',         '✈️',  '#0077b6',
             'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&q=80'),
            ('Auto & Moto',     'auto',           '🚗', '#6c757d',
             'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&q=80'),
            ('Bijoux & Luxe',   'bijoux',         '💎', '#D4AF37',
             'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600&q=80'),
            ('Bébé & Enfants',  'bebe',           '🍼', '#ffb3c6',
             'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&q=80'),
        ]
        cats = {}
        for name, slug, icon, color, image_url in CATEGORIES:
            c, _ = Category.objects.update_or_create(slug=slug, defaults={
                'name': name, 'icon': icon, 'image_color': color, 'image_url': image_url,
            })
            cats[slug] = c
        self.stdout.write(self.style.SUCCESS(f'OK: {len(cats)} catégories'))

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

            # ── Livres & Culture ──
            ('Atomic Habits',          'livres', 15000, None, '📖', '#4361ee',
             'Transformez vos habitudes, transformez votre vie. Bestseller mondial.',
             'livre,habitudes,developpement,james clear,bestseller',
             'Gallimard', True,
             'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80'),

            ("L'Alchimiste",           'livres', 9000, None, '📖', '#8B6914',
             'Paulo Coelho. Un berger et sa quête de la légende personnelle.',
             'roman,paulo coelho,philosophie,voyage,initiation',
             'Éditions Anne Carrière', False,
             'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80'),

            ('Sapiens',                'livres', 12000, None, '📚', '#2c3e50',
             'Une brève histoire de l\'humanité par Yuval Noah Harari.',
             'histoire,humanite,harari,essai,science',
             'Albin Michel', False,
             'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500&q=80'),

            ('Harry Potter T1',        'livres', 8000, None, '📗', '#7f1d1d',
             'Harry Potter à l\'école des sorciers — édition illustrée.',
             'roman,fantasy,jeunesse,magie,rowling',
             'Gallimard Jeunesse', False,
             'https://images.unsplash.com/photo-1551269901-5c5e14c25df7?w=500&q=80'),

            # ── Cuisine & Food ──
            ('Robot pâtissier KitchenAid', 'cuisine', 280000, 320000, '🥣', '#e63946',
             'Bol inox 4.8L, 10 vitesses, + de 15 accessoires inclus.',
             'kitchenaid,patisserie,robot,cuisine,boulangerie',
             'KitchenAid', True,
             'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500&q=80'),

            ('Couteau de chef japonais', 'cuisine', 65000, None, '🔪', '#1a1a1a',
             'Lame acier damas 67 couches, manche pakkawood, 20cm.',
             'couteau,japonais,damas,chef,cuisine',
             'Miyabi', False,
             'https://images.unsplash.com/photo-1593618998160-e34014e67546?w=500&q=80'),

            ('Livre de recettes Gordon Ramsay', 'cuisine', 22000, None, '📕', '#8B0000',
             '100 recettes de l\'étoilé Michelin pour cuisiner comme un pro.',
             'cuisine,recettes,gordon ramsay,gastronomie,chef',
             'Marabout', False,
             'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=500&q=80'),

            ('Poêle antiadhésive Tefal', 'cuisine', 35000, None, '🍳', '#c0392b',
             'Revêtement Titanium Expert, compatible induction, 28cm.',
             'poele,tefal,induction,antiadhesif,cuisine',
             'Tefal', False,
             'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500&q=80'),

            # ── Jeux & Jouets ──
            ('PlayStation 5',          'jeux', 450000, 500000, '🎮', '#00439c',
             'Console next-gen, SSD ultra rapide, DualSense haptique.',
             'ps5,playstation,sony,console,gaming',
             'Sony', True,
             'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=500&q=80'),

            ('Nintendo Switch OLED',   'jeux', 220000, None, '🕹️', '#e60012',
             'Écran OLED 7", dock amélioré, 64 Go stockage interne.',
             'nintendo,switch,oled,portable,gaming',
             'Nintendo', True,
             'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=500&q=80'),

            ('LEGO Technic 4x4',       'jeux', 75000, None, '🧱', '#f7d32c',
             'Set 2200 pièces, moteur Power Functions, suspension réelle.',
             'lego,technic,construction,enfant,4x4',
             'LEGO', False,
             'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=500&q=80'),

            ('Manette Xbox Series X',  'jeux', 35000, None, '🎮', '#107c10',
             'Sans fil Bluetooth, grip texturé, compatible PC & Xbox.',
             'xbox,manette,microsoft,gaming,wireless',
             'Microsoft', False,
             'https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=500&q=80'),

            # ── Voyage & Outdoor ──
            ('Valise Samsonite 75cm',  'voyage', 95000, 120000, '🧳', '#1a3a5c',
             'Polycarbonate léger, 4 roues 360°, serrure TSA, 94L.',
             'valise,samsonite,voyage,trolley,tsa',
             'Samsonite', True,
             'https://images.unsplash.com/photo-1553531580-a3b6c4d5e8f0?w=500&q=80'),

            ('Sac à dos randonnée 50L', 'voyage', 55000, None, '🎒', '#2d6a4f',
             'Waterproof, dos ventilé, ceinture lombaire, 50 litres.',
             'sac,randonnee,trekking,outdoor,montagne',
             'Osprey', False,
             'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=500&q=80'),

            ('Appareil photo Sony Alpha', 'voyage', 380000, None, '📷', '#1a1a1a',
             'Capteur APS-C 24MP, 4K, stabilisation 5 axes, autofocus IA.',
             'sony,photo,appareil,alpha,mirrorless',
             'Sony', False,
             'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80'),

            ('Adaptateur universel',   'voyage', 12000, None, '🔌', '#6c757d',
             'Compatible 150+ pays, 3 USB-A + 1 USB-C, indicateur LED.',
             'adaptateur,voyage,universal,usb,electrique',
             'TravelPro', False,
             'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500&q=80'),

            # ── Auto & Moto ──
            ('Dashcam 4K 70mai',       'auto', 45000, None, '📹', '#1a1a1a',
             'Résolution 4K, vision nocturne, WiFi, parking mode 24h.',
             'dashcam,voiture,camera,4k,wifi',
             '70mai', True,
             'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=500&q=80'),

            ('GPS auto Garmin DriveSmart', 'auto', 85000, None, '🗺️', '#0077b6',
             'Écran 6.95", cartes Europe à vie, alertes trafic en direct.',
             'gps,garmin,navigation,voiture,europe',
             'Garmin', False,
             'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=500&q=80'),

            ('Chargeur voiture USB-C 65W', 'auto', 8000, None, '⚡', '#f4a261',
             'Double port USB-C + USB-A, charge rapide 65W, compact.',
             'chargeur,voiture,usbc,rapide,65w',
             'Anker', False,
             'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&q=80'),

            ('Balai de voiture premium', 'auto', 18000, None, '🚗', '#6c757d',
             'Kit nettoyage auto 12 pièces, microfibres et aspirateur portable.',
             'nettoyage,voiture,auto,kit,microfibre',
             'AutoClean', False,
             'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=500&q=80'),

            # ── Bijoux & Luxe ──
            ('Bracelet or 18 carats',  'bijoux', 185000, 210000, '📿', '#D4AF37',
             'Or jaune 18 carats, maille gourmette, longueur 19cm, 4.2g.',
             'bracelet,or,18carats,luxe,bijou',
             'Joaillerie Luxe', True,
             'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500&q=80'),

            ('Collier perles naturelles', 'bijoux', 95000, None, '📿', '#f5e6c8',
             'Perles d\'eau douce AAA, fermoir argent 925, 42cm.',
             'collier,perles,naturel,argent,femme',
             'Perles Fines', False,
             'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80'),

            ('Bague diamant solitaire', 'bijoux', 450000, None, '💍', '#e8e8e8',
             'Diamant 0.5ct GIA, serti griffes, or blanc 18 carats.',
             'bague,diamant,solitaire,or,blanc,fiancailles',
             'Diamonds & Co', True,
             'https://images.unsplash.com/photo-1543294001-f7cd5d7fb516?w=500&q=80'),

            ('Montre Tissot Everytime', 'bijoux', 180000, None, '⌚', '#c0c0c0',
             'Mouvement quartz Swiss Made, saphir anti-reflet, 30m waterproof.',
             'montre,tissot,suisse,luxe,classique',
             'Tissot', False,
             'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'),

            # ── Bébé & Enfants ──
            ('Poussette Chicco Trio',  'bebe', 185000, 210000, '👶', '#ffb3c6',
             'Trio combiné, châssis aluminium léger, nacelle + siège auto.',
             'poussette,bebe,chicco,trio,nacelle',
             'Chicco', True,
             'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80'),

            ('Hochet musical Fisher-Price', 'bebe', 12000, None, '🔔', '#f9c74f',
             'Sons et lumières apaisantes, stimule l\'éveil, 0-12 mois.',
             'hochet,musical,bebe,eveil,jouet',
             'Fisher-Price', False,
             'https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=500&q=80'),

            ('Lot pyjamas bébé bio',   'bebe', 22000, None, '🍼', '#c8f0e0',
             'Pack 3 pyjamas coton bio certifié GOTS, zip, 0-3 mois.',
             'pyjama,bebe,bio,coton,gots',
             'Petit Bateau', False,
             'https://images.unsplash.com/photo-1522771930-78848d9293e8?w=500&q=80'),

            ('Tapis d\'éveil musical',  'bebe', 35000, None, '🎵', '#a8dadc',
             '5 arches amovibles, 20 sons, miroir, tapis doux 95×80cm.',
             'tapis,eveil,bebe,musical,arches',
             'Tiny Love', False,
             'https://images.unsplash.com/photo-1612539465796-3f2ec74c5fe4?w=500&q=80'),
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
        self.stdout.write(self.style.SUCCESS(f'OK: {created} produits créés, {updated} mis à jour'))

        USERS = [
            ('alice@recoshop.com',  'Alice',  'pass1234'),
            ('bob@recoshop.com',    'Bob',    'pass1234'),
            ('clara@recoshop.com',  'Clara',  'pass1234'),
            ('david@recoshop.com',  'David',  'pass1234'),
            ('emma@recoshop.com',   'Emma',   'pass1234'),
            ('farid@recoshop.com',  'Farid',  'pass1234'),
            ('grace@recoshop.com',  'Grace',  'pass1234'),
            ('hassan@recoshop.com', 'Hassan', 'pass1234'),
            ('demo@recoshop.com',   'Demo',   'demo1234'),
        ]
        users = []
        for email, username, password in USERS:
            u, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                u.set_password(password)
                u.save()
            users.append(u)
        self.stdout.write(self.style.SUCCESS(f'OK: {len(users)} utilisateurs'))

        all_products = list(Product.objects.all())
        rc = 0
        for user in users:
            sample = random.sample(all_products, min(20, len(all_products)))
            for product in sample:
                score = random.choices([1,2,3,4,5], weights=[5,10,20,35,30])[0]
                _, c = Rating.objects.get_or_create(user=user, product=product, defaults={'score': score})
                if c: rc += 1
        self.stdout.write(self.style.SUCCESS(f'OK: {rc} notes créées'))
        self.stdout.write(self.style.SUCCESS('\nSeed terminé ! Compte démo : demo@recoshop.com / demo1234'))
