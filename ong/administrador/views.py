from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Adminstrador

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        try:
            admin = Adminstrador.objects.get(email=email, senha=senha)
            request.session["admin_id"] = admin.id
            request.session["admin_email"] = admin.email
            return redirect("home")
        except Adminstrador.DoesNotExist:
            messages.error(request, "Email ou senha inválidos.")
            return redirect("login")

    return render(request, "administrador/login.html")


def logout_view(request):
    request.session.flush()  # remove todos os dados da sessão
    return redirect("login")

def dashboard_view(request):
    if not request.session.get("admin_id"):
        return redirect("login")  # se não estiver logado, volta para o login
      
    return render(request, "home.html")