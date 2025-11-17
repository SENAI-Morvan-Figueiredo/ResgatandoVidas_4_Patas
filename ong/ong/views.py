from django.shortcuts import render

def doacoes(request):
    return render(request, 'ong/doacao.html')

def home(request):
    return render(request, 'ong/home.html')
