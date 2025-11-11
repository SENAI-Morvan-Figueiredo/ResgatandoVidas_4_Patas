from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("email")  # pode ser email ou username
        senha = request.POST.get("senha")

        user = authenticate(request, username=username_or_email, password=senha)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "E-mail/Usuário ou senha inválidos.")
            return redirect("login")

    return render(request, "administrador/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "home.html")
