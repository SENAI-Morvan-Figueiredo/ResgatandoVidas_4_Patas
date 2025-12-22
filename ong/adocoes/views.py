import logging
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Adocao, Adotados, Gato
from .forms import AdocaoForm
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import datetime
from lares_temporarios.models import LarTemporarioAtual
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------------------- Da tela adocao_list

# -----------------------------------------
# Função para aparecer a lista de gatos
# Gatos disponíveis para adoção
# -----------------------------------------


@method_decorator(cache_page(60 * 7), name='dispatch')  # 7 minutos
class GatoListView(ListView):
    model = Gato
    template_name = 'adocoes/adocao_list.html'
    context_object_name = 'gatos'
    paginate_by = None  # controlado manualmente

    def get(self, request, *args, **kwargs):
        # Verifica parâmetro para mostrar todos ou resumido
        self.show_all = request.GET.get('show_all', 'false').lower() == 'true'
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            qs = Gato.objects.filter(adotados__isnull=True)

            # Ordenação por created_at ou id
            try:
                qs = qs.order_by('-created_at')
            except Exception:
                qs = qs.order_by('-id')

            # Filtro por nome
            nome_filter = self.request.GET.get('nome')
            if nome_filter:
                qs = qs.filter(nome__icontains=nome_filter)

            # Filtro por sexo
            sexo_filter = self.request.GET.get('sexo')
            if sexo_filter == 'F':
                qs = qs.filter(sexo='F')
            elif sexo_filter == 'M':
                qs = qs.filter(sexo='M')

            # Mostrar somente 8 itens quando não “show_all”
            if not getattr(self, 'show_all', False):
                qs = qs[:8]

            return qs

        except Exception as e:
            logger.exception("Erro em GatoListView.get_queryset: %s", e)
            return Gato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_all'] = getattr(self, 'show_all', False)
        context['total_count'] = Gato.objects.filter(adotados__isnull=True).count()
        return context


# -------------------------------------------------------------------------------------------------- Da tela adocao_detail

# -----------------------------------------
# Função para aparecer informações 
# detalhadas do gato
# -----------------------------------------

@method_decorator(cache_page(60 * 5), name='dispatch')
class GatoDetailView(DetailView):
    model = Gato
    template_name = 'adocoes/adocao_detail.html'
    context_object_name = 'gato'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['other_gatos'] = Gato.objects.filter(adotados__isnull=True).exclude(pk=self.object.pk)[:4]
        return ctx


# -------------------------------------------------------------------------------------------------- Da tela adocao_success

# -------------------------------------------------------
# Função que confirma o sucesso do formulário de adoção
# -------------------------------------------------------

def adocao_sucess(request):
    return render(request, 'adocoes/adocao_sucess.html')


# -------------------------------------------------------------------------------------Formulário de Adoção

# ---------------------------------------------------------
# Função auxiliar para converter boolean → "Sim"/"Não"
# ---------------------------------------------------------
def bool_para_texto(valor):
    if valor is True:
        return "Sim"
    if valor is False:
        return "Não"
    return "—"


# ---------------------------------------------------------
# VIEW principal do formulário de adoção
# ---------------------------------------------------------
def formulario_adocao(request):
    print("DEBUG: Entrou na view formulario_adocao")  # início da view
    gato_id = request.GET.get("gato")
    print("DEBUG: gato_id recebido =", gato_id)

    gato = Gato.objects.filter(id=gato_id).first()
    print("DEBUG: gato encontrado =", gato)

    if not gato:
        messages.error(request, "Gato não encontrado.")
        print("DEBUG: Gato não encontrado, redirecionando")
        return redirect("adocoes:lista")

    if request.method == "POST":
        form = AdocaoForm(request.POST)
        
        # forçar o form a aceitar o gato específico
        form.fields['gato'].queryset = Gato.objects.filter(id=gato.id)

        if 'created_at' in form.fields:
            del form.fields['created_at']

        if form.is_valid():
            adocao = form.save(commit=False)
            adocao.gato = gato  # já atribuído
            adocao.save()

            # ---------------------------------------------
            #       CONSTRUÇÃO DO E-MAIL EM HTML
            # ---------------------------------------------
            email_html = f"""
            <h2>🐾 Novo Pedido de Adoção Recebido</h2>
            <p>Você recebeu uma nova solicitação de adoção pelo site.</p>

            <h3>🐱 Informações do Gato</h3>
            <p><strong>Gato:</strong> {adocao.gato.nome}</p>

            <hr>

            <h3>👤 Informações do Adotante</h3>
            <p><strong>Nome:</strong> {adocao.nome}</p>
            <p><strong>CPF:</strong> {adocao.cpf}</p>
            <p><strong>Idade:</strong> {adocao.idade} anos</p>
            <p><strong>Profissão:</strong> {adocao.ocupacao_profissional}</p>
            <p><strong>E-mail:</strong> {adocao.email}</p>
            <p><strong>Condições financeiras adequadas?</strong> {bool_para_texto(adocao.codicoes_financeiras)}</p>

            <hr>

            <h3>📍 Endereço</h3>
            <p><strong>Rua:</strong> {adocao.rua}</p>
            <p><strong>Número:</strong> {adocao.numero}</p>
            <p><strong>Bairro:</strong> {adocao.bairro}</p>
            <p><strong>Cidade:</strong> {adocao.cidade}</p>
            <p><strong>CEP:</strong> {adocao.cep}</p>

            <hr>

            <h3>📱 Contato</h3>
            <p><strong>Instagram:</strong> {adocao.instagram or "—"}</p>
            <p><strong>Telefone:</strong> {adocao.numero_contato}</p>

            <hr>

            <h3>🐾 Informações sobre Outros Animais</h3>
            <p><strong>Possui outros animais?</strong> {bool_para_texto(adocao.animal_externo)}</p>
            """

            # -------- CAMPO CONDICIONAL: TEM OUTROS ANIMAIS ----------
            if adocao.animal_externo:
                email_html += f"""
                <p><strong>Animais costumam dar voltinhas na rua ou casas vizinhas?</strong> {bool_para_texto(adocao.animal_externo_voltinhas)}</p>
                <p><strong>Espécie e idade:</strong> {adocao.animal_externo_especie_idade or "—"}</p>
                <p><strong>Algum não castrado?</strong> {bool_para_texto(adocao.animal_externo_nao_castrado)}</p>
                <p><strong>Vacinas em dia?</strong> {bool_para_texto(adocao.animal_externo_vacinacao)}</p>
                <p><strong>Testados para FIV/FELV?</strong> {bool_para_texto(adocao.animal_externo_testado)}</p>
                <p><strong>Ração oferecida:</strong> {adocao.animal_externo_racao or "—"}</p>
                """

            email_html += f"""
            <hr>

            <h3>🔄 Período de Adaptação</h3>
            <p><strong>Entende sobre período de adaptação?</strong> {bool_para_texto(adocao.periodo_adaptacao)}</p>

            <hr>

            <h3>🏠 Moradia</h3>
            <p><strong>Mora sozinho?</strong> {bool_para_texto(adocao.mora_sozinho)}</p>
            <p><strong>Moram crianças?</strong> {bool_para_texto(adocao.mora_crianca)}</p>
            <p><strong>Alguém não concorda?</strong> {bool_para_texto(adocao.alguem_nao_concorda)}</p>
            <p><strong>Alguém alérgico?</strong> {bool_para_texto(adocao.alguem_alergico)}</p>
            <p><strong>Imóvel próprio?</strong> {bool_para_texto(adocao.imovel_proprio)}</p>
            
            <hr>
            
            <p><strong>Reside em casa ou apartamento?</strong> {"Casa" if adocao.mora_casa else "Apartamento"}</p>
            """

            # ----------- CAMPOS CONDICIONAIS CASA / APARTAMENTO ---------------
            if adocao.mora_casa:
                email_html += f"""
                <p><strong>Muros baixos?</strong> {bool_para_texto(adocao.casa_muros_laterais_baixos)}</p>
                <p><strong>Possui quintal?</strong> {bool_para_texto(adocao.casa_quintal)}</p>
                <p><strong>Outras casas no quintal?</strong> {bool_para_texto(adocao.casa_quintal_mais_casa)}</p>
                <p><strong>Acesso à garagem?</strong> {bool_para_texto(adocao.casa_garagem)}</p>
                """
            else:
                email_html += f"""
                <p><strong>Apartamento telado?</strong> {bool_para_texto(adocao.apartamento_telada)}</p>
                <p><strong>Limitador no banheiro?</strong> {bool_para_texto(adocao.apartamento_limitador)}</p>
                """

            email_html += f"""
            <hr>

            <h3>📦 Mudanças e Estabilidade</h3>
            <p><strong>Mudança trabalho?</strong> {bool_para_texto(adocao.mudanca_trabalho)}</p>
            <p><strong>Mudança imóvel?</strong> {bool_para_texto(adocao.mudanca_imovel)}</p>
            <p><strong>Novo imóvel telado?</strong> {bool_para_texto(adocao.mudanca_imovel_seguranca)}</p>
            <p><strong>Compromete-se a comunicar o doador?</strong> {bool_para_texto(adocao.mudanca_imovel_comunicar)}</p>

            <hr>

            <h3>📘 Responsabilidades</h3>
            <p><strong>Está ciente que não pode repassar esse animal para outra pessoa:</strong> {bool_para_texto(adocao.repassar_animal)}</p>
            <p><strong>Em caso de desistência, está ciente que será obrigado a comunicar o doador para que o mesmo encontre um novo lar para o animal?</strong> {bool_para_texto(adocao.dessistencia)}</p>
            <p><strong>Responsável nas viagens:</strong> {adocao.viagens}</p>
            <p><strong>Animal ficará restrito?</strong> {bool_para_texto(adocao.restrito)}</p>
            <p><strong>Já precisou doar, devolver ou entregar na Zoonoses ou Ongs algum animal?</strong> {bool_para_texto(adocao.devolver_doar)}</p>
            """

            # ----------- EXPLICAÇÃO APARECE APENAS SE DEVOLVEU/DOOU ------------
            if adocao.devolver_doar:
                email_html += f"""
                <p><strong>Explicação:</strong> {adocao.devolver_doar_explique or "—"}</p>
                """

            email_html += f"""
            <p><strong>Aceita responder o doador sobre a adaptação e condições de vida e saúde do animal adotado sempre que esse achar necessário?</strong> {bool_para_texto(adocao.responder_doador)}</p>

            <hr>

            <h3>📅 Registro</h3>
            <p><strong>Criado em:</strong> {adocao.created_at}</p>
            """

            # ---------------------------------------------
            #              ENVIO DO E-MAIL
            # ---------------------------------------------
            assunto = f"Nova solicitação de adoção: {adocao.nome}"
            destinatarios = ["resgatandovidas4patas@gmail.com"]  # Trocar pelo e-mail da ONG

            email = EmailMessage(
                subject=assunto,
                body=email_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=destinatarios,
            )
            email.content_subtype = "html"
            email.send()
            

            # messages.success(request, "Sua solicitação foi enviada com sucesso! ❤️🐾")
            return redirect("adocoes:adocao_sucess")
        else:
            print("DEBUG: Form inválido")
            print("DEBUG: Erros do form:", form.errors)

    else:
        print("DEBUG: Método GET detectado")
        form = AdocaoForm()
        # remove campos não-editáveis
        if 'created_at' in form.fields:
            del form.fields['created_at']
            print("DEBUG: Campo created_at removido do form (GET)")

    return render(request, "adocoes/adocao_form.html", {"form": form, "gato": gato})


# -------------------------------------------------------------------------------------------------- Da tela adotados_list

# -----------------------------------------
# Função para aparecer a lista de gatos
# Gatos que já foram adotados
# -----------------------------------------

@method_decorator(cache_page(60 * 7), name='dispatch')  # 7 minutos
class AdotadosListView(ListView):
    model = Adotados
    template_name = 'adocoes/adotados_list.html'
    context_object_name = 'adotados'
    paginate_by = None  # controle manual igual na página de adoção

    def get(self, request, *args, **kwargs):
        self.show_all = request.GET.get('show_all', 'false').lower() == 'true'
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Adotados.objects.order_by('-created_at')

        if not getattr(self, 'show_all', False):
            qs = qs[:8]

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_all'] = getattr(self, 'show_all', False)
        ctx['total_count'] = Adotados.objects.count()
        return ctx

# -------------------------------------------------------------------------------------------------- Da tela registrar_adocao

# -----------------------------------------
# Função para registrar uma adoção
# -----------------------------------------

@login_required(login_url='login') # Garante que só usuários logados possam acessar essa view
def registrar_adocao(request):
    if request.method == "POST":
        gato_id = request.POST.get("gato")
        adotante_id = request.POST.get("adotante") 
        data_inicio = request.POST.get("data_inicio")
        foto = request.FILES.get("foto")

        gato = get_object_or_404(Gato, id=gato_id)
        adotante = get_object_or_404(Adocao, id=adotante_id)

        
        if Adotados.objects.filter(gato=gato).exists():
            messages.warning(request, f"O gato {gato.nome} já foi adotado!")
            return redirect("administrador:dashboard_admin_adocoes")

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
        return redirect("administrador:dashboard_admin_adotados")

    # ---------------- GET ----------------

    # remove apenas gatos já adotados
    gatos_adotados_ids = Adotados.objects.values_list("gato_id", flat=True)

    gatos_disponiveis = Gato.objects.exclude(id__in=gatos_adotados_ids)

    context = {
        "gatos": gatos_disponiveis,
        "adotantes": Adocao.objects.all(),  
    }

    return render(request, "adocoes/registrar_adocao.html", context)


# -----------------------------------------
# Função para editar um registro de adoção
# -----------------------------------------

@login_required(login_url='login')
def editar_adocao(request, pk):

    adotado = get_object_or_404(Adotados, id=pk)

    if request.method == "POST":
        gato_id = request.POST.get("gato")
        adotante_id = request.POST.get("adotante")
        data_inicio = request.POST.get("data_inicio")
        foto = request.FILES.get("foto")

        novo_gato = get_object_or_404(Gato, id=gato_id)
        novo_adotante = get_object_or_404(Adocao, id=adotante_id)

        if novo_gato != adotado.gato:
            if Adotados.objects.filter(gato=novo_gato).exists():
                messages.warning(request, f"O gato {novo_gato.nome} já foi adotado!")
                return redirect("administrador:dashboard_admin_adotados")

            antigo_gato = adotado.gato
            antigo_gato.adotado = False
            antigo_gato.save()

            novo_gato.adotado = True
            novo_gato.save()

        adotado.gato = novo_gato
        adotado.adocao = novo_adotante
        adotado.data_inicio = data_inicio

        if foto:
            adotado.imagem = foto

        adotado.save()

        messages.success(request, "Adoção atualizada com sucesso!")
        return redirect("administrador:dashboard_admin_adotados")

    gatos_adotados_ids = Adotados.objects.values_list("gato_id", flat=True)

    gatos_disponiveis = Gato.objects.exclude(id__in=gatos_adotados_ids).union(
        Gato.objects.filter(id=adotado.gato.id)
    )

    context = {
        "gatos": gatos_disponiveis,
        "adotantes": Adocao.objects.all(),
        "adotado": adotado
    }

    return render(request, "adocoes/registrar_adocao.html", context)


# -----------------------------------------
# Função para aparecer os adotantes vinculados a um gato específico
# -----------------------------------------

@login_required(login_url='login')
def buscar_adotantes_para_gato(request, gato_id):
    """
    Busca os registros de Adocao (formulários preenchidos) que estão vinculados 
    ao gato específico (gato_id).
    """
    # Filtra os objetos Adocao que têm o gato_id igual ao passado na URL
    # Presumindo que o seu modelo Adocao tem um campo ForeignKey para Gato.
    # Se o campo se chama 'gato', o filtro é:
    adotantes = Adocao.objects.filter(gato_id=gato_id).values('id', 'nome', 'email')
    
    # Converte o QuerySet para uma lista de dicionários e retorna como JSON
    return JsonResponse(list(adotantes), safe=False)

# -------------------------------------------------------------------------------------------------- Da tela dashboard_admin_adotados

# -----------------------------------------------------------------------------
# Função para excluir um registro de adoção - na tela dashboard_admin_adotados
# -----------------------------------------------------------------------------


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
    