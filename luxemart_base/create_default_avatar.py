"""
Script à exécuter une fois pour créer l'image avatar par défaut.
Place ce fichier à la racine du projet et lance :
    python create_default_avatar.py
"""
import os, sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_reco.settings')

try:
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (100, 100), color='#1A1A2E')
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 90, 90], fill='#C9A84C')
    draw.ellipse([35, 25, 65, 55], fill='#1A1A2E')
    draw.ellipse([20, 55, 80, 95], fill='#1A1A2E')
    static_dir = os.path.join('recommendations', 'static', 'img')
    os.makedirs(static_dir, exist_ok=True)
    img.save(os.path.join(static_dir, 'default_avatar.png'))
    print("✅ default_avatar.png créé dans recommendations/static/img/")
except ImportError:
    # Créer un fichier SVG si Pillow n'est pas disponible
    static_dir = os.path.join('recommendations', 'static', 'img')
    os.makedirs(static_dir, exist_ok=True)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="50" fill="#1A1A2E"/>
  <circle cx="50" cy="38" r="18" fill="#C9A84C"/>
  <ellipse cx="50" cy="85" rx="28" ry="22" fill="#C9A84C"/>
</svg>'''
    with open(os.path.join(static_dir, 'default_avatar.png'), 'w') as f:
        f.write(svg)
    print("✅ default_avatar.svg créé (Pillow non disponible)")
