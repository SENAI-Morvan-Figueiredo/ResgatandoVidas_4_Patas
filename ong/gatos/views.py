from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from gatos.models import Gato
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import GatoForm, CuidadoForm, TemperamentoForm, SociavelForm, MoradiaForm
from django.contrib.auth.decorators import login_required


# -------------------------------------------------------------------------------------------------- Da tela adicionar_gato_form

# -----------------------------------------
# View que vai adicionar o gato
# -----------------------------------------

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


# -----------------------------------------
# View que vai adicionar o gato
# -----------------------------------------

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


# -------------------------------------------------------------------------------------------------- Da tela dashboard_admin_adocoes

# -----------------------------------------
# Função para excluir um gatinho
# -----------------------------------------

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