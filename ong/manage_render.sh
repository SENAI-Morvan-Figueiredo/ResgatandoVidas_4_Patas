#!/bin/bash
echo "🚀 Iniciando script de deploy Render..."

# 1️⃣ Aplicar migrações
echo "📌 Aplicando migrações..."
python manage.py migrate --noinput

# 2️⃣ Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 3️⃣ Criar superusuário caso não exista
# Substitua USERNAME, EMAIL e PASSWORD pelos valores do seu superusuário
DJANGO_SUPERUSER_USERNAME="ÉosD"
DJANGO_SUPERUSER_EMAIL="seu_email@exemplo.com"
DJANGO_SUPERUSER_PASSWORD="sua_senha_segura"

echo "👤 Verificando se superusuário existe..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists():
    User.objects.create_superuser(
        username="$DJANGO_SUPERUSER_USERNAME",
        email="$DJANGO_SUPERUSER_EMAIL",
        password="$DJANGO_SUPERUSER_PASSWORD"
    )
    print("✅ Superusuário criado com sucesso!")
else:
    print("ℹ️ Superusuário já existe, nada feito.")
END

echo "🎉 Deploy concluído com sucesso!"
