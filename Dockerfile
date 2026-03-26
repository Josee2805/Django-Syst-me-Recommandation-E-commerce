# ── Image de base ──────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Évite les .pyc et bufferise stdout/stderr immédiatement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ── Dépendances système (psycopg2-binary en a besoin) ──────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# ── Répertoire de travail ──────────────────────────────────────────────────────
WORKDIR /app

# ── Dépendances Python ─────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Code source ────────────────────────────────────────────────────────────────
COPY . .

# ── Script de démarrage ────────────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ── Port exposé ────────────────────────────────────────────────────────────────
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
