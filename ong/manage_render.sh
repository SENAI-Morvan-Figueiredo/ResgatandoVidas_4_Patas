#!/bin/bash
echo "🚀 Iniciando script de deploy Render..."

# 1️⃣ Aplicar migrações
echo "📌 Aplicando migrações..."
python manage.py migrate --noinput

# 2️⃣ Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 3️⃣ Exportar variáveis de ambiente para garantir que o Python veja
export DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME}"
export DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL}"
export DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD}"

export DJANGO_SUPERUSER2_USERNAME="${DJANGO_SUPERUSER2_USERNAME}"
export DJANGO_SUPERUSER2_EMAIL="${DJANGO_SUPERUSER2_EMAIL}"
export DJANGO_SUPERUSER2_PASSWORD="${DJANGO_SUPERUSER2_PASSWORD}"


echo "👤 Verificando se superusuário existe..."
python manage.py shell << END
import os
from django.contrib.auth import get_user_model

User = get_user_model()

def criar_superuser(prefixo):
    username = os.environ.get(f"{prefixo}_USERNAME")
    email = os.environ.get(f"{prefixo}_EMAIL")
    password = os.environ.get(f"{prefixo}_PASSWORD")

    if not all([username, email, password]):
        print(f"⚠️ Variáveis de ambiente ausentes para {prefixo}")
        return

    if User.objects.filter(username=username).exists():
        print(f"ℹ️ Superusuário '{username}' já existe.")
        return

    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Superusuário '{username}' criado com sucesso!")

# Criar os dois superusuários
criar_superuser("DJANGO_SUPERUSER1")
criar_superuser("DJANGO_SUPERUSER2")
END

# 4️⃣ Iniciar o Gunicorn
echo "🟢 Iniciando Gunicorn..."
exec gunicorn ong.wsgi:application --bind 0.0.0.0:$PORT
