#!/bin/bash
python manage.py migrate --noinput

echo "from django.contrib.auth.models import User; User.objects.create_superuser('ÉosD', 'raicarvalho343@gmail.com', 'G@tinho')" | python manage.py shell
