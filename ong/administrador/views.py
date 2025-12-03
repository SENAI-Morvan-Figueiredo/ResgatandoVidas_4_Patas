from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from adocoes.models import Adotados
from gatos.models import Gato
from lares_temporarios.models import LarTemporarioAtual, HistoricoLarTemporario
from django.db.models import Q

# ---------------------------------------------------------------------------------------- Sistema de autenticação

# -----------------------------------------
# Função de logout
# -----------------------------------------

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

# -----------------------------------------
# Função de logout
# -----------------------------------------
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_adotados

# -------------------------------------------------------------------------
# View que vai mandar as informações para os cards e tambem para o filtro
# -------------------------------------------------------------------------

@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
def dashboard_admin_adotados(request):
    # Pega todos os registros de adoção com os relacionamentos otimizados
    adotados = Adotados.objects.select_related('adocao', 'gato')

    # Filtro por nome - nome do gato ou da pessoa
    nome = request.GET.get("nome")
    if nome:
        adotados = adotados.filter(
            Q(gato__nome__icontains=nome) |
            Q(adocao__nome__icontains=nome)
        )

    # Pega dados do adotante para facilitar no template
    for adotado in adotados:
        adotado.adotante_primeiro_nome = adotado.adocao.nome.split()[0] if adotado.adocao.nome else ''
        adotado.adotante_nome = adotado.adocao.nome
        adotado.adotante_email = adotado.adocao.email
        adotado.adotante_telefone = adotado.adocao.numero_contato

    context = {
        "adotados": adotados,
    }
    return render(request, "administrador/dashboard_admin_adotados.html", context)


# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_adocoes

# -------------------------------------------------------------------------
# View que vai mandar as informações para os cards e tambem para o filtro
# -------------------------------------------------------------------------

@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
def dashboard_admin_adocoes(request):
    # Pega todos os gatos
    gatos = Gato.objects.all()

    # Excluir gatos que já foram adotados
    gatos = gatos.exclude(id__in=Adotados.objects.values_list('gato_id', flat=True))

    # Filtro por nome
    nome = request.GET.get("nome")
    if nome:
        gatos = gatos.filter(nome__icontains=nome)

    # Filtro por sexo
    sexo = request.GET.get("sexo")
    if sexo in ["M", "F"]:
        gatos = gatos.filter(sexo=sexo)

    context = {
        "gatos": gatos,
    }
    return render(request, "administrador/dashboard_admin_adocoes.html", context)


# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_lar_temporario

# -------------------------------------------------------------------------
# View que vai mandar as informações para os cards e também para o filtro
# -------------------------------------------------------------------------

@login_required(login_url='login')  # Garante que só usuários logados possam acessar essa view
def dashboard_admin_lar_temporario(request):

    # Filtra apenas os gatos que precisam de lar temporário
    gatos = Gato.objects.filter(lar_temporario=True)

    # Excluir gatos que já foram adotados
    gatos = gatos.exclude(id__in=Adotados.objects.values_list('gato_id', flat=True))

    # Filtro por nome
    nome = request.GET.get("nome")
    if nome:
        gatos = gatos.filter(nome__icontains=nome)

    # Filtro por sexo
    sexo = request.GET.get("sexo")
    if sexo in ["M", "F"]:
        gatos = gatos.filter(sexo=sexo)

    # Pega os IDs dos gatos que estão em Lar Temporário atualmente
    gatos_em_lar_ids = LarTemporarioAtual.objects.values_list("gato_id", flat=True)

    # ================================
    # ADIÇÃO: pegar lar atual e histórico
    # ================================
    for gato in gatos:
        # Marca se o gato está ou não em lar
        gato.em_lar = gato.id in gatos_em_lar_ids

        # Puxa o lar atual desse gato (se existir)
        gato.lar_atual = (
            LarTemporarioAtual.objects
            .select_related("lar_temporario")
            .filter(gato=gato)
            .first()
        )
        if gato.lar_atual:
            lar = gato.lar_atual.lar_temporario
            # 🔥 CRIAR O ENDEREÇO COMPLETO AQUI!
            lar.endereco = f"{lar.rua}, {lar.numero}, {lar.bairro}, {lar.cidade} - CEP {lar.cep}"


        # Puxa todo o histórico deste gato
        gato.historico_lares = (
            HistoricoLarTemporario.objects
            .select_related("lar_temporario")
            .filter(gato=gato)
            .order_by("-data_inicio")
        )
        # 🔥 Criar endereço completo também para cada item do histórico
        for h in gato.historico_lares:
            l = h.lar_temporario
            h.endereco = f"{l.rua}, {l.numero}, {l.bairro}, {l.cidade} - CEP {l.cep}"


    context = {
        "gatos": gatos,
    }

    return render(request, "administrador/dashboard_admin_lar_temporario.html", context)
