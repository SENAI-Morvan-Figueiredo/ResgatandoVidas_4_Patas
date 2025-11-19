from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    # Captura o "next" tanto no GET quanto no POST
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        username_or_email = request.POST.get("email")
        senha = request.POST.get("senha")

        user = authenticate(request, username=username_or_email, password=senha)

        if user is not None:
            login(request, user)

            # 🔹 Se "next" existir, volta para a página que o usuário queria acessar
            if next_url:
                return redirect(next_url)
            else:
                return redirect("home")  # Página padrão após login
        else:
            messages.error(request, "E-mail/Usuário ou senha inválidos.")
            return redirect("login")

    # 🔹 Passa o "next" para o template, para manter o valor no formulário
    return render(request, "administrador/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    return redirect("login")


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home.html")
