from django.core.management.base import BaseCommand
from recommendations.models import CustomUser, Category, Product, Rating
import random


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        CATEGORIES = [
            ('Electronique',    'electronique', '#1a1a2e',
             'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&q=80'),
            ('Mode & Vetements','mode',         '#8B4513',
             'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&q=80'),
            ('Maison & Deco',   'maison',       '#2d6a4f',
             'https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=600&q=80'),
            ('Sport & Fitness', 'sport',        '#d62828',
             'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&q=80'),
            ('Beaute & Sante',  'beaute',       '#c77dff',
             'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&q=80'),
            ('Livres & Culture','livres',       '#4361ee',
             'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=600&q=80'),
            ('Cuisine & Food',  'cuisine',      '#f4a261',
             'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&q=80'),
            ('Jeux & Jouets',   'jeux',         '#06d6a0',
             'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=600&q=80'),
            ('Voyage & Outdoor','voyage',       '#0077b6',
             'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&q=80'),
            ('Auto & Moto',     'auto',         '#6c757d',
             'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&q=80'),
            ('Bijoux & Luxe',   'bijoux',       '#D4AF37',
             'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600&q=80'),
            ('Bebe & Enfants',  'bebe',         '#ffb3c6',
             'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&q=80'),
        ]
        cats = {}
        for name, slug, color, image_url in CATEGORIES:
            c, _ = Category.objects.update_or_create(slug=slug, defaults={
                'name': name, 'image_color': color, 'image_url': image_url,
            })
            cats[slug] = c
        self.stdout.write(self.style.SUCCESS(f'OK: {len(cats)} categories'))

        # (name, cat_slug, price, orig_price, color, desc, tags, brand, featured, image_url)
        PRODUCTS = [

            # ── Electronique (10) ──
            ('iPhone 15 Pro', 'electronique', 650000, 700000, '#1a1a2e',
             'Puce A17 Pro, titane, 48MP ProRAW, Dynamic Island.',
             'apple,smartphone,ios,camera,pro', 'Apple', True,
             'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&q=80'),

            ('Samsung Galaxy S24', 'electronique', 580000, None, '#1c1c2e',
             'Galaxy AI integre, Snapdragon 8 Gen 3, ecran 6.7".',
             'samsung,android,smartphone,ai,amoled', 'Samsung', True,
             'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500&q=80'),

            ('MacBook Air M2', 'electronique', 950000, 1000000, '#2c2c2e',
             'Puce M2, 15h autonomie, ecran Liquid Retina 13.6".',
             'apple,laptop,macos,m2,ultraportable', 'Apple', True,
             'https://images.unsplash.com/photo-1611186871525-9be197a39a16?w=500&q=80'),

            ('AirPods Pro 2', 'electronique', 180000, None, '#e8e8e8',
             'ANC adaptatif, audio spatial personnalise, MagSafe.',
             'apple,earbuds,anc,audio,wireless', 'Apple', False,
             'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500&q=80'),

            ('iPad Pro 12.9', 'electronique', 720000, None, '#3a3a3c',
             'Ecran Liquid Retina XDR, puce M2, compatible Apple Pencil.',
             'apple,tablette,ipad,m2,pro', 'Apple', False,
             'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500&q=80'),

            ('Sony WH-1000XM5', 'electronique', 220000, 260000, '#1a1a1a',
             'Meilleure reduction de bruit du marche, 30h autonomie.',
             'sony,casque,audio,anc,hi-res', 'Sony', False,
             'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80'),

            ('Smart TV Samsung 55"', 'electronique', 480000, 550000, '#0d0d0d',
             '4K QLED, HDR10+, Tizen OS, 3 ports HDMI.',
             'tv,samsung,4k,qled,smart', 'Samsung', True,
             'https://images.unsplash.com/photo-1461151304267-38535e780c79?w=500&q=80'),

            ('GoPro Hero 12', 'electronique', 280000, None, '#1a1a1a',
             '5.3K video, HyperSmooth 6.0, waterproof 10m.',
             'gopro,camera,action,sport,video', 'GoPro', False,
             'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80'),

            ('Enceinte JBL Charge 5', 'electronique', 95000, None, '#e63946',
             'Son 360 degres, 20h autonomie, charge USB-C, waterproof.',
             'jbl,enceinte,bluetooth,waterproof,son', 'JBL', False,
             'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&q=80'),

            ('Dell XPS 15', 'electronique', 1100000, 1200000, '#2c2c2e',
             'Core i7 13e gen, 16GB RAM, SSD 512GB, ecran OLED 15.6".',
             'dell,laptop,xps,windows,pro', 'Dell', False,
             'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80'),

            # ── Mode (10) ──
            ('Nike Air Max 270', 'mode', 85000, 95000, '#ff6b35',
             'Coussin Air Max 270 degres pour un amorti exceptionnel.',
             'nike,sneakers,air,running,lifestyle', 'Nike', True,
             'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80'),

            ('Adidas Stan Smith', 'mode', 65000, None, '#f5f5f5',
             "L'icone du tennis devenue incontournable du streetwear.",
             'adidas,sneakers,classique,cuir,blanc', 'Adidas', False,
             'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80'),

            ('Sac a main cuir', 'mode', 120000, 140000, '#5c3d2e',
             'Cuir pleine fleur tanne vegetal, fermeture doree.',
             'sac,cuir,femme,luxe,tote', 'Maroquinerie', True,
             'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&q=80'),

            ('Montre classique homme', 'mode', 95000, None, '#D4AF37',
             'Cadran guilloche, bracelet cuir brun, mouvement quartz.',
             'montre,homme,classique,or,cuir', 'Horlogerie', False,
             'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'),

            ('Lunettes de soleil', 'mode', 35000, None, '#1a1a1a',
             'Monture acetate, verres polarisants UV400.',
             'lunettes,soleil,uv,style,acetate', 'Optique', False,
             'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&q=80'),

            ('Veste en jean', 'mode', 45000, None, '#1565C0',
             'Denim 100% coton, coupe droite, boutons dores.',
             'jean,veste,denim,casual,vintage', 'Denim Co.', False,
             'https://images.unsplash.com/photo-1601333144130-8cbb312386b6?w=500&q=80'),

            ('Robe elegante soiree', 'mode', 75000, 90000, '#8B1A4A',
             'Soie naturelle, decollete dos nu, coupe ajustee, taille 36-44.',
             'robe,soiree,elegance,femme,soie', 'Couture Paris', True,
             'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500&q=80'),

            ('Pull cachemire premium', 'mode', 68000, None, '#c8a882',
             'Cachemire grade A, 2 fils, coupe oversized, 5 coloris.',
             'pull,cachemire,luxe,hiver,chaud', 'Cachemire&Co', False,
             'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=500&q=80'),

            ('Ceinture cuir homme', 'mode', 22000, None, '#4a2c0a',
             'Cuir full grain, boucle argentee mat, largeur 35mm.',
             'ceinture,cuir,homme,classique,accessoire', 'Maroquinerie', False,
             'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80'),

            ('Chapeau fedora', 'mode', 28000, None, '#6b5035',
             'Laine 100%, ruban noir, bord 7cm, taille ajustable.',
             'chapeau,fedora,homme,style,laine', 'Hatwork', False,
             'https://images.unsplash.com/photo-1514327605112-b887c0e61c0a?w=500&q=80'),

            # ── Maison (8) ──
            ('Lampe design LED', 'maison', 45000, None, '#D4AF37',
             'Structure metal dore, ampoule Edison, lumiere chaude 2700K.',
             'lampe,led,deco,or,salon,design', 'Deco Lumiere', False,
             'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&q=80'),

            ('Cafetiere premium', 'maison', 55000, 65000, '#2c1810',
             '15 bars, buse vapeur, bac 1.5L, cafe espresso parfait.',
             'cafe,expresso,machine,premium,barista', 'CoffeeMaster', True,
             'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500&q=80'),

            ('Coussin decoratif velours', 'maison', 15000, None, '#a0522d',
             'Velours doux, 45x45cm, garnissage plumes recyclees.',
             'coussin,velours,deco,salon,confort', 'Maison Textile', False,
             'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&q=80'),

            ("Plante d'interieur", 'maison', 12000, None, '#2d6a4f',
             "Facile d'entretien, purifie l'air, pot ceramique inclus.",
             'plante,interieur,vert,deco,air', 'Green Home', False,
             'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=500&q=80'),

            ('Bougie parfumee', 'maison', 8000, None, '#f5e6c8',
             'Cire de soja naturelle, 50h combustion, senteur vanille-bois.',
             'bougie,parfum,soja,ambiance,zen', 'Parfums Maison', False,
             'https://images.unsplash.com/photo-1602928321679-560bb453f190?w=500&q=80'),

            ('Tapis berbere', 'maison', 75000, None, '#a0522d',
             'Tisse main au Maroc, laine naturelle, motifs geometriques, 200x300cm.',
             'tapis,berbere,maroc,laine,artisanat', 'Atlas Artisan', True,
             'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80'),

            ('Miroir rond dore', 'maison', 38000, None, '#D4AF37',
             'Cadre metal dore, diametre 60cm, fixation murale incluse.',
             'miroir,dore,deco,salon,chambre', 'Deco Home', False,
             'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=500&q=80'),

            ('Cadre photo triptyque', 'maison', 18000, None, '#2c2c2c',
             'Set 3 cadres assortis, bois noir, formats 10x15, 20x25, 30x40.',
             'cadre,photo,deco,bois,salon', 'Frame Studio', False,
             'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=500&q=80'),

            # ── Sport (8) ──
            ('Tapis de yoga premium', 'sport', 25000, None, '#7B2D8B',
             'Caoutchouc naturel 6mm, antiderapant, marquages alignement.',
             'yoga,mat,fitness,bien-etre,antiderapant', 'YogaLife', False,
             'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=500&q=80'),

            ('Velo de course', 'sport', 350000, 400000, '#d62828',
             'Cadre aluminium allege, 22 vitesses Shimano, freins disque.',
             'velo,course,route,shimano,carbon', 'CyclePro', True,
             'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=500&q=80'),

            ('Halteres 10kg', 'sport', 40000, None, '#1a1a1a',
             'Paire 10kg, fonte chromee, grip antiderapant hexagonal.',
             'halteres,musculation,fonte,gym,force', 'IronFit', False,
             'https://images.unsplash.com/photo-1585152968992-d2b9444408cc?w=500&q=80'),

            ('Montre GPS Garmin', 'sport', 180000, None, '#1a1a2e',
             'GPS multiband, cardio poignet, 14 jours autonomie, running dynamics.',
             'garmin,montre,gps,running,sport', 'Garmin', False,
             'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500&q=80'),

            ('Sac de sport Nike', 'sport', 35000, None, '#1a1a2e',
             '35L, compartiment chaussures separe, impermeable.',
             'nike,sac,sport,gym,training', 'Nike', False,
             'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80'),

            ('Ballon de football', 'sport', 18000, None, '#1a1a1a',
             'Taille 5, couture thermocollee, FIFA Quality Pro.',
             'football,ballon,sport,fifa,competition', 'SportBall', False,
             'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=500&q=80'),

            ('Raquette de tennis', 'sport', 55000, 65000, '#2c7a2c',
             'Wilson Pro Staff 97, 305g, cordage inclus, niveau intermediaire.',
             'tennis,raquette,wilson,sport,competition', 'Wilson', False,
             'https://images.unsplash.com/photo-1554068865-24ceec13d068?w=500&q=80'),

            ('Corde a sauter pro', 'sport', 12000, None, '#d62828',
             'Cable acier reglable, poignees ergonomiques, compteur integre.',
             'corde,sauter,cardio,fitness,boxing', 'SportPro', False,
             'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500&q=80'),

            # ── Beaute (8) ──
            ('Parfum Chanel N5', 'beaute', 150000, 170000, '#f5e6c8',
             "L'eau de parfum iconique depuis 1921. Floral aldehydee, 100ml.",
             'parfum,chanel,floral,luxe,femme', 'Chanel', True,
             'https://images.unsplash.com/photo-1541643600914-78b084683702?w=500&q=80'),

            ('Creme visage Nivea', 'beaute', 28000, None, '#c0c0c0',
             'Hydratation intense 24h, formule legere non grasse.',
             'nivea,creme,hydratation,visage,soin', 'Nivea', False,
             'https://images.unsplash.com/photo-1556228720-da4ef8ab9eed?w=500&q=80'),

            ('Palette maquillage 20 teintes', 'beaute', 32000, None, '#c77dff',
             '20 teintes harmonisees, finis mat & shimmer, longue tenue.',
             'maquillage,palette,yeux,ombre,shimmer', 'MakeUp Pro', False,
             'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500&q=80'),

            ('Serum Vitamin C 20%', 'beaute', 22000, None, '#f4a261',
             'Vitamine C 20% stabilisee, eclat immediat, anti-taches, 30ml.',
             'serum,vitaminec,eclat,antiage,soin', 'The Ordinary', False,
             'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&q=80'),

            ('Rouge a levres MAC', 'beaute', 18000, None, '#8B0000',
             'Formule cremeuse longue tenue, couleur intense, 50 teintes.',
             'mac,rouge,levres,maquillage,couleur', 'MAC', False,
             'https://images.unsplash.com/photo-1586495777744-4e6232bf2e79?w=500&q=80'),

            ("Huile d'argan bio", 'beaute', 12000, None, '#D4AF37',
             '100% pure, premiere pression a froid, certifiee bio, 50ml.',
             'argan,huile,bio,soin,naturel', 'Argan Pur', False,
             'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500&q=80'),

            ('Brosse dentaire electrique', 'beaute', 45000, None, '#e8e8e8',
             'Oral-B Pro, 3 modes, timer 2min, 3 brossettes incluses.',
             'brosse,dentaire,electrique,oral-b,hygiene', 'Oral-B', False,
             'https://images.unsplash.com/photo-1559591937-abc7a093c63a?w=500&q=80'),

            ('Fond de teint Fenty', 'beaute', 38000, None, '#c77dff',
             '50 teintes inclusives, couvrance modulable, SPF 15.',
             'fenty,fond,teint,inclusif,maquillage', 'Fenty Beauty', True,
             'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=500&q=80'),

            # ── Livres (8) ──
            ('Atomic Habits', 'livres', 15000, None, '#4361ee',
             'Transformez vos habitudes, transformez votre vie. Bestseller mondial.',
             'livre,habitudes,developpement,james clear,bestseller', 'Gallimard', True,
             'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80'),

            ("L'Alchimiste", 'livres', 9000, None, '#8B6914',
             'Paulo Coelho. Un berger et sa quete de la legende personnelle.',
             'roman,paulo coelho,philosophie,voyage,initiation', 'A. Carriere', False,
             'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80'),

            ('Sapiens', 'livres', 12000, None, '#2c3e50',
             "Une breve histoire de l'humanite par Yuval Noah Harari.",
             'histoire,humanite,harari,essai,science', 'Albin Michel', False,
             'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500&q=80'),

            ('Harry Potter T1', 'livres', 8000, None, '#7f1d1d',
             "Harry Potter a l'ecole des sorciers — edition illustree.",
             'roman,fantasy,jeunesse,magie,rowling', 'Gallimard Jeunesse', False,
             'https://images.unsplash.com/photo-1551269901-5c5e14c25df7?w=500&q=80'),

            ('1984 - George Orwell', 'livres', 8500, None, '#1a1a2e',
             'Dystopie culte. Big Brother vous surveille. Edition integrale.',
             'roman,dystopie,orwell,classique,politique', 'Folio', False,
             'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=500&q=80'),

            ('Le Petit Prince', 'livres', 7000, None, '#f4a261',
             "Saint-Exupery. L'histoire du petit prince venu d'une autre planete.",
             'roman,classique,jeunesse,poetique,universel', 'Gallimard', False,
             'https://images.unsplash.com/photo-1519791883288-dc8bd696e667?w=500&q=80'),

            ('Rich Dad Poor Dad', 'livres', 11000, None, '#D4AF37',
             'Robert Kiyosaki. Apprenez a faire travailler votre argent pour vous.',
             'finance,investissement,kiyosaki,richesse,education', 'Leduc', False,
             'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=500&q=80'),

            ('Think and Grow Rich', 'livres', 9500, None, '#2c3e50',
             'Napoleon Hill. Les secrets des plus grands hommes d\'affaires.',
             'finance,succes,napoleon hill,mindset,richesse', 'Ixelles Ed.', False,
             'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80'),

            # ── Cuisine (8) ──
            ('Robot patissier KitchenAid', 'cuisine', 280000, 320000, '#e63946',
             'Bol inox 4.8L, 10 vitesses, 15+ accessoires inclus.',
             'kitchenaid,patisserie,robot,cuisine,boulangerie', 'KitchenAid', True,
             'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500&q=80'),

            ('Couteau de chef japonais', 'cuisine', 65000, None, '#1a1a1a',
             'Lame acier damas 67 couches, manche pakkawood, 20cm.',
             'couteau,japonais,damas,chef,cuisine', 'Miyabi', False,
             'https://images.unsplash.com/photo-1593618998160-e34014e67546?w=500&q=80'),

            ('Livre de recettes Gordon Ramsay', 'cuisine', 22000, None, '#8B0000',
             '100 recettes de l\'etoile Michelin pour cuisiner comme un pro.',
             'cuisine,recettes,gordon ramsay,gastronomie,chef', 'Marabout', False,
             'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=500&q=80'),

            ('Poele antiadhesive Tefal', 'cuisine', 35000, None, '#c0392b',
             'Revetement Titanium Expert, compatible induction, 28cm.',
             'poele,tefal,induction,antiadhesif,cuisine', 'Tefal', False,
             'https://images.unsplash.com/photo-1584270354949-c26b0d5b4a0c?w=500&q=80'),

            ('Mixeur Vitamix 5200', 'cuisine', 195000, 220000, '#2c3e50',
             '2HP, 10 vitesses, verre Tritan 1.4L, garantie 7 ans.',
             'mixeur,vitamix,blender,smoothie,pro', 'Vitamix', True,
             'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=500&q=80'),

            ('Moules silicone patisserie', 'cuisine', 14000, None, '#f4a261',
             'Set 6 moules flexibles, antiadhesifs, -40C a +230C.',
             'moule,silicone,patisserie,four,gateau', 'Lekue', False,
             'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=500&q=80'),

            ('Machine espresso De Longhi', 'cuisine', 145000, 170000, '#1a1a1a',
             '15 bars, buse vapeur rotative, reservoir 1.8L, auto-nettoyage.',
             'delonghi,espresso,cafe,barista,machine', 'De Longhi', True,
             'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500&q=80'),

            ('Planche a decouper bambou', 'cuisine', 18000, None, '#c8a882',
             'Bambou massif anti-bacterien, gorge jus, 40x28cm.',
             'planche,bambou,cuisine,naturel,antibacterien', 'Totally Bamboo', False,
             'https://images.unsplash.com/photo-1588515724527-074a7a56616c?w=500&q=80'),

            # ── Jeux (8) ──
            ('PlayStation 5', 'jeux', 450000, 500000, '#00439c',
             'Console next-gen, SSD ultra rapide, DualSense haptique.',
             'ps5,playstation,sony,console,gaming', 'Sony', True,
             'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=500&q=80'),

            ('Nintendo Switch OLED', 'jeux', 220000, None, '#e60012',
             'Ecran OLED 7", dock ameliore, 64 Go stockage interne.',
             'nintendo,switch,oled,portable,gaming', 'Nintendo', True,
             'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=500&q=80'),

            ('LEGO Technic 4x4', 'jeux', 75000, None, '#f7d32c',
             'Set 2200 pieces, moteur Power Functions, suspension reelle.',
             'lego,technic,construction,enfant,4x4', 'LEGO', False,
             'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=500&q=80'),

            ('Manette Xbox Series X', 'jeux', 35000, None, '#107c10',
             'Sans fil Bluetooth, grip texture, compatible PC & Xbox.',
             'xbox,manette,microsoft,gaming,wireless', 'Microsoft', False,
             'https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=500&q=80'),

            ('PC Gaming Asus ROG', 'jeux', 850000, 950000, '#00ff87',
             'RTX 4070, Ryzen 7, 32GB RAM, SSD 1TB NVMe.',
             'pc,gaming,asus,rog,rtx', 'Asus', True,
             'https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=500&q=80'),

            ('Jeu echecs luxe', 'jeux', 42000, None, '#8B6914',
             'Pieces en bois sculpte, echiquier pliable, 40x40cm.',
             'echecs,bois,strategie,luxe,classique', 'Chess & Co', False,
             'https://images.unsplash.com/photo-1586165368502-1bad197a6461?w=500&q=80'),

            ('Drone DJI Mini 3', 'jeux', 295000, None, '#1a1a1a',
             '4K HDR, 38 min autonomie, poids 249g, stabilisation 3 axes.',
             'drone,dji,mini,4k,photographie', 'DJI', False,
             'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=500&q=80'),

            ('Casque VR Meta Quest 2', 'jeux', 185000, 210000, '#e8e8e8',
             'Standalone, 128GB, 90Hz, bibliotheque 500+ jeux.',
             'vr,meta,quest,realite,virtuelle', 'Meta', False,
             'https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=500&q=80'),

            # ── Voyage (8) ──
            ('Valise Samsonite 75cm', 'voyage', 95000, 120000, '#1a3a5c',
             'Polycarbonate leger, 4 roues 360, serrure TSA, 94L.',
             'valise,samsonite,voyage,trolley,tsa', 'Samsonite', True,
             'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=500&q=80'),

            ('Sac a dos randonnee 50L', 'voyage', 55000, None, '#2d6a4f',
             'Waterproof, dos ventile, ceinture lombaire, 50 litres.',
             'sac,randonnee,trekking,outdoor,montagne', 'Osprey', False,
             'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=500&q=80'),

            ('Appareil photo Sony Alpha', 'voyage', 380000, None, '#1a1a1a',
             'Capteur APS-C 24MP, 4K, stabilisation 5 axes, autofocus IA.',
             'sony,photo,appareil,alpha,mirrorless', 'Sony', False,
             'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80'),

            ('Adaptateur universel voyageur', 'voyage', 12000, None, '#6c757d',
             'Compatible 150+ pays, 3 USB-A + 1 USB-C, indicateur LED.',
             'adaptateur,voyage,universal,usb,electrique', 'TravelPro', False,
             'https://images.unsplash.com/photo-1573920111312-04f1b25c6b85?w=500&q=80'),

            ('Guide du Routard Asie', 'voyage', 18000, None, '#f4a261',
             "Asie du Sud-Est 2024, cartes detaillees, bons plans locaux.",
             'guide,voyage,asie,routard,tourisme', 'Hachette', False,
             'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=500&q=80'),

            ('Masque de sommeil Silk', 'voyage', 8000, None, '#2c1810',
             'Soie 100% naturelle, reglable, bloque 99% lumiere.',
             'masque,sommeil,soie,voyage,avion', 'Silk Dreams', False,
             'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=500&q=80'),

            ('Trousse toilette cuir', 'voyage', 32000, None, '#4a2c0a',
             'Cuir vegan, impermeable, compartiments organises, 26x14cm.',
             'trousse,toilette,cuir,voyage,organiseur', 'TravelKit', False,
             'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&q=80'),

            ('Ecouteurs Sony voyage', 'voyage', 160000, 185000, '#1a1a1a',
             'Reduction bruit active, 30h autonomie, pliable, etui inclus.',
             'ecouteurs,sony,anc,voyage,silence', 'Sony', True,
             'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80'),

            # ── Auto (8) ──
            ('Dashcam 4K 70mai', 'auto', 45000, None, '#1a1a1a',
             'Resolution 4K, vision nocturne, WiFi, parking mode 24h.',
             'dashcam,voiture,camera,4k,wifi', '70mai', True,
             'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=500&q=80'),

            ('GPS Garmin DriveSmart', 'auto', 85000, None, '#0077b6',
             'Ecran 6.95", cartes Europe a vie, alertes trafic direct.',
             'gps,garmin,navigation,voiture,europe', 'Garmin', False,
             'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=500&q=80'),

            ('Chargeur voiture USB-C 65W', 'auto', 8000, None, '#f4a261',
             'Double port USB-C + USB-A, charge rapide 65W, compact.',
             'chargeur,voiture,usbc,rapide,65w', 'Anker', False,
             'https://images.unsplash.com/photo-1581093458791-9f3c3250a8b0?w=500&q=80'),

            ('Kit nettoyage auto 12 pieces', 'auto', 22000, None, '#2c3e50',
             'Microfibres premium, brosse interieur, aspirateur portable.',
             'nettoyage,voiture,auto,kit,microfibre', 'AutoClean', False,
             'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=500&q=80'),

            ('Parfum voiture Maserati', 'auto', 18000, None, '#D4AF37',
             'Diffuseur clip grille, fragrance cuir & bois, rechargeable.',
             'parfum,voiture,diffuseur,luxe,cuir', 'Maserati', False,
             'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=500&q=80'),

            ('Siege auto enfant Maxi-Cosi', 'auto', 95000, 110000, '#e63946',
             'Groupe 1/2/3, isofix, protection laterale, 9-36kg.',
             'siege,auto,enfant,isofix,securite', 'Maxi-Cosi', True,
             'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80'),

            ('Compresseur pneu portable', 'auto', 28000, None, '#1a1a2e',
             'Gonflage auto en 3 min, USB-C, ecran digital, 150PSI.',
             'compresseur,pneu,portable,auto,urgence', 'AirMax', False,
             'https://images.unsplash.com/photo-1565043666747-69f6646db940?w=500&q=80'),

            ('Organiseur coffre voiture', 'auto', 15000, None, '#2c2c2c',
             'Pliable, fixation par sangle, 3 compartiments, 30L.',
             'organiseur,coffre,voiture,rangement,auto', 'TrunkOrg', False,
             'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=500&q=80'),

            # ── Bijoux (8) ──
            ('Bracelet or 18 carats', 'bijoux', 185000, 210000, '#D4AF37',
             'Or jaune 18 carats, maille gourmette, longueur 19cm, 4.2g.',
             'bracelet,or,18carats,luxe,bijou', 'Joaillerie Luxe', True,
             'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500&q=80'),

            ('Collier perles naturelles', 'bijoux', 95000, None, '#f5e6c8',
             "Perles d'eau douce AAA, fermoir argent 925, 42cm.",
             'collier,perles,naturel,argent,femme', 'Perles Fines', False,
             'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80'),

            ('Bague diamant solitaire', 'bijoux', 450000, None, '#e8e8e8',
             'Diamant 0.5ct GIA, serti griffes, or blanc 18 carats.',
             'bague,diamant,solitaire,or,blanc,fiancailles', 'Diamonds & Co', True,
             'https://images.unsplash.com/photo-1543294001-f7cd5d7fb516?w=500&q=80'),

            ('Montre Tissot Everytime', 'bijoux', 180000, None, '#c0c0c0',
             'Mouvement quartz Swiss Made, saphir anti-reflet, 30m waterproof.',
             'montre,tissot,suisse,luxe,classique', 'Tissot', False,
             'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'),

            ('Boucles oreilles or', 'bijoux', 65000, None, '#D4AF37',
             'Or 18 carats, creoles 3cm, finition polie, fermoir securise.',
             'boucles,oreilles,or,creoles,femme', 'Joaillerie', False,
             'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80'),

            ('Pendentif croix argent', 'bijoux', 28000, None, '#c0c0c0',
             'Argent massif 925, chaine 45cm incluse, boite cadeau.',
             'pendentif,croix,argent,925,cadeau', 'Silver Art', False,
             'https://images.unsplash.com/photo-1573408301185-9519f94a978a?w=500&q=80'),

            ('Bague argent pierre lune', 'bijoux', 42000, None, '#e8e8e8',
             'Pierre de lune naturelle, argent 925, taille ajustable.',
             'bague,argent,pierre,lune,boheme', 'Stone & Silver', False,
             'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80'),

            ('Bracelet jonc acier', 'bijoux', 22000, None, '#c0c0c0',
             'Acier inoxydable, finition or rose, diametre 6cm.',
             'bracelet,jonc,acier,or rose,tendance', 'ModJewel', False,
             'https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=500&q=80'),

            # ── Bebe (6) ──
            ('Poussette Chicco Trio', 'bebe', 185000, 210000, '#ffb3c6',
             'Trio combine, chassis aluminium leger, nacelle + siege auto.',
             'poussette,bebe,chicco,trio,nacelle', 'Chicco', True,
             'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80'),

            ('Hochet musical Fisher-Price', 'bebe', 12000, None, '#f9c74f',
             'Sons et lumieres apaisantes, stimule l\'eveil, 0-12 mois.',
             'hochet,musical,bebe,eveil,jouet', 'Fisher-Price', False,
             'https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=500&q=80'),

            ('Lot pyjamas bebe bio', 'bebe', 22000, None, '#c8f0e0',
             'Pack 3 pyjamas coton bio certifie GOTS, zip, 0-3 mois.',
             'pyjama,bebe,bio,coton,gots', 'Petit Bateau', False,
             'https://images.unsplash.com/photo-1522771930-78848d9293e8?w=500&q=80'),

            ("Tapis d'eveil musical", 'bebe', 35000, None, '#a8dadc',
             '5 arches amovibles, 20 sons, miroir, tapis doux 95x80cm.',
             'tapis,eveil,bebe,musical,arches', 'Tiny Love', False,
             'https://images.unsplash.com/photo-1566140967423-9d7f2a64f3bf?w=500&q=80'),

            ('Baignoire bebe pliable', 'bebe', 28000, None, '#b3d9ff',
             'Pliable en 3 secondes, antiderapant, de la naissance a 6 mois.',
             'baignoire,bebe,pliable,bain,securite', 'BabyDam', False,
             'https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=500&q=80'),

            ('Mobile musical lit bebe', 'bebe', 25000, None, '#ffd6e7',
             '12 melodies, rotation 360, fixation universel, telecommande.',
             'mobile,musical,bebe,lit,nuit', 'Baby Einstein', False,
             'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80'),
        ]

        created = updated = 0
        for data in PRODUCTS:
            name, cat_slug, price, orig, color, desc, tags, brand, featured, image_url = data
            obj, c = Product.objects.update_or_create(
                name=name,
                defaults={
                    'category': cats[cat_slug], 'price': price, 'original_price': orig,
                    'image_color': color, 'description': desc,
                    'tags': tags, 'brand': brand, 'is_featured': featured,
                    'image_url': image_url,
                    'stock': random.randint(10, 200),
                }
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'OK: {created} produits crees, {updated} mis a jour'))

        USERS = [
            ('alice@recoshop.com',  'Alice',  'pass1234', 'femme',  'mode,beaute',          'moyen',   'qualite'),
            ('bob@recoshop.com',    'Bob',    'pass1234', 'homme',  'electronique,jeux',    'illimite','nouveautes'),
            ('clara@recoshop.com',  'Clara',  'pass1234', 'femme',  'maison,beaute',        'moyen',   'qualite'),
            ('david@recoshop.com',  'David',  'pass1234', 'homme',  'sport,voyage',         'moyen',   'prix'),
            ('emma@recoshop.com',   'Emma',   'pass1234', 'femme',  'livres,alimentation',  'petit',   'qualite'),
            ('farid@recoshop.com',  'Farid',  'pass1234', 'homme',  'auto,electronique',    'moyen',   'promotions'),
            ('grace@recoshop.com',  'Grace',  'pass1234', 'femme',  'bijoux,mode',          'illimite','qualite'),
            ('hassan@recoshop.com', 'Hassan', 'pass1234', 'homme',  'sport,jeux',           'petit',   'prix'),
            ('demo@recoshop.com',   'Demo',   'demo1234', 'femme',  'mode,electronique',    'moyen',   'nouveautes'),
        ]
        users = []
        for email, username, password, gender, interests, budget, priority in USERS:
            u, created_u = CustomUser.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created_u:
                u.set_password(password)
            u.gender = gender
            u.interests = interests
            u.budget = budget
            u.purchase_priority = priority
            u.onboarding_done = True
            u.save()
            users.append(u)
        self.stdout.write(self.style.SUCCESS(f'OK: {len(users)} utilisateurs'))

        all_products = list(Product.objects.all())
        rc = 0
        for user in users:
            sample = random.sample(all_products, min(20, len(all_products)))
            for product in sample:
                score = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                _, c = Rating.objects.get_or_create(user=user, product=product, defaults={'score': score})
                if c:
                    rc += 1
        self.stdout.write(self.style.SUCCESS(f'OK: {rc} notes creees'))
        self.stdout.write(self.style.SUCCESS('Seed termine ! demo@recoshop.com / demo1234'))
