import logging
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from gatos.models import Gato
from lares_temporarios.models import LarTemporarioAtual , LarTemporario , HistoricoLarTemporario
from adocoes.models import Adotados , Adocao
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import GatoForm, CuidadoForm, TemperamentoForm, SociavelForm, MoradiaForm
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_adocoes

# View que vai mandar as informações para os cards e tambem para o filtro
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


class GatoCreateView(CreateView):
    model = Gato
    form_class = GatoForm
    template_name = 'gatos/adicionar_gato_form.html'
    success_url = reverse_lazy('dashboard_admin_adocoes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.POST or None
        files = self.request.FILES or None

        context['gato_form'] = context.get('form')  # principal
        context['cuidado_form'] = kwargs.get('cuidado_form') or CuidadoForm(data, prefix='cuidado')
        context['temperamento_form'] = kwargs.get('temperamento_form') or TemperamentoForm(data, prefix='temperamento')
        context['moradia_form'] = kwargs.get('moradia_form') or MoradiaForm(data, prefix='moradia')
        context['sociavel_form'] = kwargs.get('sociavel_form') or SociavelForm(data, prefix='sociavel')
        return context

    def post(self, request, *args, **kwargs):
        # todos os forms de uma vez
        form = self.get_form()
        cuidado_form = CuidadoForm(request.POST, prefix='cuidado')
        temperamento_form = TemperamentoForm(request.POST, prefix='temperamento')
        moradia_form = MoradiaForm(request.POST, prefix='moradia')
        sociavel_form = SociavelForm(request.POST, prefix='sociavel')


        if all([
            form.is_valid(),
            cuidado_form.is_valid(),
            temperamento_form.is_valid(),
            moradia_form.is_valid(),
            sociavel_form.is_valid()
        ]):
            
            cuidado = cuidado_form.save()
            temperamento = temperamento_form.save()
            moradia = moradia_form.save()
            sociavel = sociavel_form.save()

            gato = form.save(commit=False)
            gato.cuidado = cuidado
            gato.temperamento = temperamento
            gato.moradia = moradia
            gato.sociavel = sociavel
            gato.save()
    
            messages.success(request, "Gato e informações relacionadas salvos com sucesso!")
            return redirect(self.success_url)
        else:

            self.object = None  # Necessário para renderizar o template corretamente
            context = self.get_context_data(
                form=form,
                cuidado_form=cuidado_form,
                temperamento_form=temperamento_form,
                moradia_form=moradia_form,
                sociavel_form=sociavel_form
            )
            print("❌ Formulário inválido:", form.errors)
            for f in [cuidado_form, temperamento_form, moradia_form, sociavel_form]:
                if f.errors:
                     print(f"⚠️ Erros em {f.__class__.__name__}:", f.errors)
            return self.render_to_response(context)
      

# -------------------------------------------------------------------------------------------------- Da tela adicionar_gato_form

# View que vai adicionar o gato
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


# ---------------------------------------------------------------------------------------- Da tela dashboard_admin_adotados

# View que vai mandar as informações para os cards e tambem para o filtro
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
@require_POST
def excluir_adotado_ajax(request, adotado_id):
    try:
        adotado = Adotados.objects.get(id=adotado_id)
        adotado.delete()  
        return JsonResponse({"status": "ok", "mensagem": f"Gato {adotado.gato.nome} excluído com sucesso!"})
    except Adotados.DoesNotExist:
        return JsonResponse({"status": "erro", "mensagem": "Registro não encontrado."}, status=404)
    

# ---------------------------------------------------------------------------------------- Da tela formulario_lar_temporario

def registrar_lar_temporario(request):
    if request.method == "POST":
        gato_id = request.POST.get("gato")
        lar_id = request.POST.get("lar")
        data_inicio = request.POST.get("data_inicio")

        gato = get_object_or_404(Gato, id=gato_id)
        lar = get_object_or_404(LarTemporario, id=lar_id)

        # Verifica se já está em lar atual
        if LarTemporarioAtual.objects.filter(gato=gato).exists():
            messages.warning(request, f"O gato {gato.nome} já está em um lar temporário ativo.")
            return redirect("gatos:dashboard_admin_lar_temporario")

        # Cria lar atual
        lar_atual = LarTemporarioAtual.objects.create(
            gato=gato,
            lar_temporario=lar,
            data_inicio=data_inicio
        )

        # Marca o gato como estando em lar temporário
        gato.lar_temporario = True
        gato.save()

        # Cria histórico
        HistoricoLarTemporario.objects.create(
            gato=gato,
            lar_temporario=lar,
            data_inicio=data_inicio
        )

        messages.success(request, "Lar temporário registrado com sucesso!")
        return redirect("gatos:dashboard_admin_lar_temporario")

    # --------------------------
    # GET → Exibir formulário
    # --------------------------

    # IDs dos gatos adotados
    adotados_ids = Adotados.objects.values_list("gato_id", flat=True)

    # IDs dos gatos que já têm lar temporário atual
    em_lar_ids = LarTemporarioAtual.objects.values_list("gato_id", flat=True)

    # Filtrando gatos disponíveis
    gatos_disponiveis = (
        Gato.objects.filter(lar_temporario=True)          # precisam de lar
            .exclude(id__in=adotados_ids)                # não estão adotados
            .exclude(id__in=em_lar_ids)                  # não estão em lar ativo
    )

    context = {
        "gatos": gatos_disponiveis,
        "lares": LarTemporario.objects.all(),
    }

    return render(request, "gatos/registrar_lar_temporario.html", context)


# ----------------------------------------------

def registrar_adocao(request):
    if request.method == "POST":
        gato_id = request.POST.get("gato")
        adotante_id = request.POST.get("adotante")  # nome do select no HTML
        data_inicio = request.POST.get("data_inicio")
        foto = request.FILES.get("foto")

        gato = get_object_or_404(Gato, id=gato_id)
        adotante = get_object_or_404(Adocao, id=adotante_id)

        # --- impedir adoção duplicada ---
        if Adotados.objects.filter(gato=gato).exists():
            messages.warning(request, f"O gato {gato.nome} já foi adotado!")
            return redirect("gatos:dashboard_admin_adocoes")

        # --- registro da adoção ---
        Adotados.objects.create(
            imagem=foto,
            gato=gato,
            adocao=adotante,
            data_inicio=data_inicio or datetime.today().date()
        )

        # --- marca o gato como adotado ---
        gato.adotado = True
        gato.save()

        # --- remove do lar atual se ele estava ---
        LarTemporarioAtual.objects.filter(gato=gato).delete()

        messages.success(request, "Adoção registrada com sucesso!")
        return redirect("gatos:dashboard_admin_adocoes")

    # ---------------- GET ----------------

    # remove apenas gatos já adotados
    gatos_adotados_ids = Adotados.objects.values_list("gato_id", flat=True)

    gatos_disponiveis = Gato.objects.exclude(id__in=gatos_adotados_ids)

    context = {
        "gatos": gatos_disponiveis,
        "adotantes": Adocao.objects.all(),  # tabela adotante
    }

    return render(request, "gatos/registrar_adocao.html", context)