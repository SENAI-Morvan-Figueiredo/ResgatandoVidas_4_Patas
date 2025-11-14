import logging
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from gatos.models import Gato
from lares_temporarios.models import LarTemporarioAtual
from adocoes.models import Adotados
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import GatoForm, CuidadoForm, TemperamentoForm, SociavelForm, MoradiaForm
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.decorators import login_required


# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_adocoes

# View que vai mandar as informações para os cards e tambem para o filtro
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
    return render(request, "gatos/dashboard_admin_adocoes.html", context)


# Função para excluir um gatinho - na tela dashboard_admin_adocoes
# Juntamente com a Pop-up de confirmação de exclusão
@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
@require_POST
def excluir_gato_ajax(request, gato_id):
    try:
        gato = Gato.objects.get(id=gato_id)
        gato.delete()  
        return JsonResponse({"status": "ok", "mensagem": f"Gato {gato.nome} excluído com sucesso!"})
    except Gato.DoesNotExist:
        return JsonResponse({"status": "erro", "mensagem": "Gato não encontrado."}, status=404)
    
    
# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_lar_temporario

# View que vai mandar as informações para os cards e tambem para o filtro
@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
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

    # Marca cada gato se ele está ou não em lar temporário
    for gato in gatos:
        gato.em_lar = gato.id in gatos_em_lar_ids

    context = {
        "gatos": gatos,
    }

    return render(request, "gatos/dashboard_admin_lar_temporario.html", context)


logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------------------- Da tela adicionar_gato_form

# View que vai adicionar o gato
@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
def adicionar_gato(request):
    # Se o método for POST, significa que o usuário clicou em “Enviar” no formulário
    if request.method == 'POST':
        # Pega as informações dos forms - instância
        gato_form = GatoForm(request.POST, request.FILES)
        cuidado_form = CuidadoForm(request.POST)
        temperamento_form = TemperamentoForm(request.POST)
        sociavel_form = SociavelForm(request.POST)
        moradia_form = MoradiaForm(request.POST)

        # Verificação se todos estão válidos (tipo de dado, campos obrigatorios) - vai vê se foi preenchido da forma certa
        if all([
            gato_form.is_valid(),
            cuidado_form.is_valid(),
            temperamento_form.is_valid(),
            sociavel_form.is_valid(),
            moradia_form.is_valid()
        ]):
            
            # Salva cada formulário auxiliar primeiro
            cuidado = cuidado_form.save()
            temperamento = temperamento_form.save()
            sociavel = sociavel_form.save()
            moradia = moradia_form.save()

            # Cria o gato, associando os objetos salvos
            gato = gato_form.save(commit=False) # Cria o objeto gato, mas ainda não salva no bd
            gato.cuidado = cuidado
            gato.temperamento = temperamento
            gato.sociavel = sociavel
            gato.moradia = moradia
            gato.save() # Após todos as informações inseridas, salva no bd

            return redirect('gatos:dashboard_admin_adocoes') # Se tudo der certinho, vai te redirecionar para a tela de dashboard_admin_adocoes

    # Caso não seja o método POST - Cria todos os formulários vazios, prontos para preenchimento.
    else:
        gato_form = GatoForm()
        cuidado_form = CuidadoForm()
        temperamento_form = TemperamentoForm()
        sociavel_form = SociavelForm()
        moradia_form = MoradiaForm()

    # Envio dos formulários para o template
    context = {
        'gato_form': gato_form,
        'cuidado_form': cuidado_form,
        'temperamento_form': temperamento_form,
        'sociavel_form': sociavel_form,
        'moradia_form': moradia_form,
    }

    return render(request, 'gatos/adicionar_gato_form.html', context)

# ---------------------------------------------------------------------------------------- Da tela adicionar_gato_form - Função de editar gato

@login_required(login_url='login')
def editar_gato(request, gato_id):
    # Busca o gato e suas relações - para preencher os formulários com os dados existentes
    gato = get_object_or_404(Gato, id=gato_id)
    cuidado = gato.cuidado
    temperamento = gato.temperamento
    sociavel = gato.sociavel
    moradia = gato.moradia

    # Se o método for POST, significa que o usuário clicou em “Enviar” no formulário
    if request.method == 'POST':
        gato_form = GatoForm(request.POST, request.FILES, instance=gato)
        cuidado_form = CuidadoForm(request.POST, instance=cuidado)
        temperamento_form = TemperamentoForm(request.POST, instance=temperamento)
        sociavel_form = SociavelForm(request.POST, instance=sociavel)
        moradia_form = MoradiaForm(request.POST, instance=moradia)

        # Verificação se todos estão válidos (tipo de dado, campos obrigatorios) - vai vê se foi preenchido da forma certa
        if all([
            gato_form.is_valid(),
            cuidado_form.is_valid(),
            temperamento_form.is_valid(),
            sociavel_form.is_valid(),
            moradia_form.is_valid()
        ]):
            # Salva os formulários atualizados
            gato_form.save()
            cuidado_form.save()
            temperamento_form.save()
            sociavel_form.save()
            moradia_form.save()
            return redirect('gatos:dashboard_admin_adocoes')

    # Caso não seja o método POST - Cria todos os formulários preenchidos com os dados existentes.
    else:
        gato_form = GatoForm(instance=gato)
        cuidado_form = CuidadoForm(instance=cuidado)
        temperamento_form = TemperamentoForm(instance=temperamento)
        sociavel_form = SociavelForm(instance=sociavel)
        moradia_form = MoradiaForm(instance=moradia)

    context = {
        'gato_form': gato_form,
        'cuidado_form': cuidado_form,
        'temperamento_form': temperamento_form,
        'sociavel_form': sociavel_form,
        'moradia_form': moradia_form,
    }

    return render(request, 'gatos/adicionar_gato_form.html', context)


# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_adotados

# View que vai mandar as informações para os cards e tambem para o filtro
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
    return render(request, "gatos/dashboard_admin_adotados.html", context)

# Função para excluir um registro de adoção - na tela dashboard_admin_adotaos
# Juntamente com a Pop-up de confirmação de exclusão
@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
@require_POST
def excluir_adotado_ajax(request, adotado_id):
    try:
        adotado = Adotados.objects.get(id=adotado_id)
        adotado.delete()  
        return JsonResponse({"status": "ok", "mensagem": f"Gato {adotado.gato.nome} excluído com sucesso!"})
    except Adotados.DoesNotExist:
        return JsonResponse({"status": "erro", "mensagem": "Registro não encontrado."}, status=404)