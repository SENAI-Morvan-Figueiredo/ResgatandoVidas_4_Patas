from django.shortcuts import render
from django.views.decorators.cache import cache_page

def doacoes(request):
    return render(request, 'ong/doacao.html')

@cache_page(60 * 7)  # 7 minutos
def home(request):
    return render(request, 'ong/home.html')