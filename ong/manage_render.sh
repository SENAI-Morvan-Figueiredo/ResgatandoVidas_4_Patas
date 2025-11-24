#!/bin/bash
# Script para executar migrações e iniciar o servidor no Render

echo "🚀 Iniciando script de deploy Render..."

# Garantir que o script pare se ocorrer qualquer erro
set -e

echo "📌 Aplicando migrações..."
python3 manage.py makemigrations --noinput || true
python3 manage.py migrate --noinput

echo "📦 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput

echo "🔥 Iniciando Gunicorn..."
gunicorn ong.wsgi:application --bind 0.0.0.0:10000

echo "from django.contrib.auth.models import User; User.objects.create_superuser('ÉosD', 'raicarvalho343@gmail.com', 'G@tinho')" | python manage.py shell
