import logging
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404 , render , redirect
from django.contrib import messages
from django.core.exceptions import FieldError
from .models import LarTemporario , HistoricoLarTemporario , LarTemporarioAtual
from gatos.models import Gato
from .forms import LarTemporarioForm
from django.utils.timezone import now
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.mail import EmailMessage


logger = logging.getLogger(__name__)

class GatoListView(ListView):
    model = Gato
    template_name = 'lares_temporarios/lar_temporario_list.html'
    context_object_name = 'gatos'
    paginate_by = None  # controle manual como no outro app

    def get(self, request, *args, **kwargs):
        # controle do botão Ver Mais / Ver Menos
        self.show_all = request.GET.get('show_all', 'false').lower() == 'true'
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            qs = Gato.objects.filter(adotados__isnull=True, lar_temporario=1)

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

            # Limita a 8 gatos se não for show_all
            if not getattr(self, 'show_all', False):
                qs = qs[:8]

            return qs

        except Exception as e:
            logger.exception("Erro em GatoListView.get_queryset: %s", e)
            return Gato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_all'] = getattr(self, 'show_all', False)
        context['total_count'] = Gato.objects.filter(adotados__isnull=True, lar_temporario=1).count()
        return context



class GatoDetailView(DetailView):
    model = Gato
    template_name = 'lares_temporarios/lar_temporario_detail.html'
    context_object_name = 'gato'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Outros gatos para exibir — exclui o atual
        ctx['other_gatos'] = Gato.objects.filter(adotados__isnull=True).exclude(pk=self.object.pk)[:4]
        return ctx
        
# ---------------------------------------------------------------------------------------------------------------
# Função auxiliar para converter valores booleanos ou strings específicas em "Sim", "Não" ou "Parcialmente"
# ---------------------------------------------------------------------------------------------------------------
def bool_para_texto(valor, campo=None):
    """
    Traduz os valores do formulário de lar temporário para texto legível.
    Aceita booleanos True/False, strings 'sim', 'nao', 'parcialmente', e campos especiais.
    """
    if valor is None:
        return "—"

    # Campos Sim/Não/Parcialmente
    if campo in ['foi_lar_temporario', 'mora_casa', 'restrito']:
        if valor in [True, 'sim', 'Sim']:
            return "Sim"
        elif valor in [False, 'nao', 'Não', 'Nao']:
            return "Não"
        elif str(valor).lower() == 'parcialmente':
            return "Parcialmente"
        return "—"

    # Duração aproximada
    if campo == 'duracao_aproximada':
        mapping = {
            'um': "Até 1 mês",
            'tres': "1-3 meses",
            'seis': "3-6 meses",
            'indefinido': "Tempo indefinido"
        }
        return mapping.get(str(valor).lower(), "—")

    # Custos
    if campo == 'custos':
        mapping = {
            'sim': "Posso ajudar com os custos",
            'nao': "Prefiro receber os suprimentos",
            'parcialmente': "Posso ajudar parcialmente"
        }
        return mapping.get(str(valor).lower(), "—")
    
   # Campo visita
    if campo == 'visita':
        return "Sim" if valor is True else "Prefiro que vocês recolham o animal temporariamente para apresentar ao adotante"
    
    # Estrutura
    if campo == 'estrutura':
        mapping = {
            'sim': "Sim",
            'nao': "Não",
            'parcialmente': "Parcialmente"
        }
        return mapping.get(str(valor).lower(), "—")

    # Caso padrão
    return str(valor) if valor else "—"



# ---------------------------------------------------------------------------------------------------------------
# VIEW para o formulário de Lar Temporário
# ---------------------------------------------------------------------------------------------------------------
def formulario_lar_temporario(request):
    gato_id = request.GET.get('gato')
    gato = None

    if gato_id:
        gato = get_object_or_404(Gato, pk=gato_id)

    if request.method == 'POST':
        form = LarTemporarioForm(request.POST)
        if form.is_valid():
            lar = form.save(commit=False)
            if gato:
                lar.gato = gato
            lar.save()

            # ----------------- CONSTRUÇÃO DO E-MAIL HTML -----------------
            email_html = f"""
            <h2>🐾 Novo Pedido de Lar Temporário Recebido</h2>
            <p>Você recebeu uma nova solicitação de lar temporário pelo site.</p>

            <h3>🐱 Informações do Gato</h3>
            <p><strong>Gato:</strong> {lar.gato.nome if lar.gato else "—"}</p>
            <p><strong>Data em que se inicia a sua disponibilidade para ser lar temporário:</strong> {lar.disponibilidade_inicio}</p>

            <hr>

            <h3>👤 Informações do Pretendente</h3>
            <p><strong>Nome:</strong> {lar.nome}</p>
            <p><strong>CPF:</strong> {lar.cpf}</p>
            <p><strong>Profissão:</strong> {lar.ocupacao_profissional}</p>
            <p><strong>E-mail:</strong> {lar.email}</p>
            <p><strong>Telefone:</strong> {lar.numero_contato}</p>

            <hr>

            <h3>🏠 Endereço</h3>
            <p><strong>Rua:</strong> {lar.rua}</p>
            <p><strong>Número:</strong> {lar.numero}</p>
            <p><strong>Bairro:</strong> {lar.bairro}</p>
            <p><strong>Cidade:</strong> {lar.cidade}</p>
            <p><strong>CEP:</strong> {lar.cep}</p>

            <hr>

            <h3>🏡 Experiência com Lar Temporário</h3>
            <p><strong>Já foi lar temporário antes?</strong> {bool_para_texto(lar.foi_lar_temporario, 'foi_lar_temporario')}</p>
            <p><strong>Reside em casa ou apartamento?</strong> {"Casa" if lar.mora_casa else "Apartamento"}</p>
            <p><strong>Animal ficará restrito?</strong> {bool_para_texto(lar.restrito, 'restrito')}</p>
            <p><strong>Estrutura segura:</strong> {bool_para_texto(lar.estrutura)}</p>
            <p><strong>Vai conseguir custear a estadia:</strong> {bool_para_texto(lar.custos)}</p>
            <p><strong>Duração aproximada:</strong> {bool_para_texto(lar.duracao_aproximada, 'duracao_aproximada')}</p>
            <p><strong>Receber visita do adotante?</strong> {bool_para_texto(lar.visita, 'visita')}</p>
            <hr>

            <h3>🐾 Outros Animais em Casa</h3>
            <p><strong>Possui outros animais?</strong> {lar.animal_externo or "—"}</p>
            """

            # Campo opcional de observações adicionais
            if lar.informacao_adicional:
                email_html += f"""
                <p><strong>Informações adicionais:</strong> {lar.informacao_adicional}</p>
                """

            email_html += f"""
            <hr>

            <h3>📅 Registro</h3>
            <p><strong>Criado em:</strong> {lar.created_at}</p>
            """

            # ----------------- ENVIO DO E-MAIL -----------------
            assunto = f"Novo pedido de lar temporário: {lar.nome}"
            destinatarios = ["raicarvalho343@gmail.com"]  # e-mail da ONG

            email = EmailMessage(
                subject=assunto,
                body=email_html,
                from_email="raicarvalho343@gmail.com",
                to=destinatarios,
            )
            email.content_subtype = "html"
            email.send()
            # ---------------------------------------------------

            messages.success(request, "Solicitação de lar temporário enviada com sucesso! ❤️🐾")
            return redirect('lares_temporarios:lar_temporario_sucess')

        else:
            print("❌ Erros no formulário:", form.errors)
            messages.error(request, "Há campos incorretos ou faltando. Confira as informações.")

    else:
        initial = {}
        if gato:
            initial['gato'] = gato
        form = LarTemporarioForm(initial=initial)

    return render(request, 'lares_temporarios/lar_temporario_form.html', {'form': form, 'gato': gato})

# -----------------------------------------------------------------------------------------------------------------------

class LarTemporarioSuccessView(TemplateView):
    template_name = 'lares_temporarios/lar_temporario_sucess.html'

# ------------------------


