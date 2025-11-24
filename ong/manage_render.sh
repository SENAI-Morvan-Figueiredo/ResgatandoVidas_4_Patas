#!/bin/bash
echo "🚀 Iniciando script de deploy Render..."

# 1️⃣ Aplicar migrações
echo "📌 Aplicando migrações..."
python manage.py migrate --noinput

# 2️⃣ Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 3️⃣ Criar superusuário caso não exista usando variáveis de ambiente
DJANGO_SUPERUSER_USERNAME="ÉosD"
DJANGO_SUPERUSER_EMAIL="$EMAIL_HOST_USER"
DJANGO_SUPERUSER_PASSWORD="$SENHA_HOST_PASSWORD"

echo "👤 Verificando se superusuário existe..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = "$DJANGO_SUPERUSER_USERNAME"
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print("✅ Superusuário criado com sucesso!")
else:
    print("ℹ️ Superusuário já existe, nada feito.")
END

# 4️⃣ Iniciar o Gunicorn para manter o serviço ativo
echo "🟢 Iniciando Gunicorn..."
exec gunicorn ong.wsgi:application --bind 0.0.0.0:$PORT
