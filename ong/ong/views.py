from django.shortcuts import render

def doacoes(request):
    return render(request, 'ong/doacao.html')

def home(request):
    return render(request, 'ong/home.html')

def home_adm(request):
    return render(request, 'administrador/home_adm.html')