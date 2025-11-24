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

echo "👤 Verificando se superusuário existe..."
python manage.py shell << END
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

print(f"DEBUG: username={username}, email={email}, password={'*' * len(password) if password else None}")

if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print("✅ Superusuário criado com sucesso!")
    else:
        print("ℹ️ Superusuário já existe, nada feito.")
else:
    print("⚠️ Variáveis de ambiente do superusuário não estão definidas!")
END

# 4️⃣ Iniciar o Gunicorn
echo "🟢 Iniciando Gunicorn..."
exec gunicorn ong.wsgi:application --bind 0.0.0.0:$PORT
