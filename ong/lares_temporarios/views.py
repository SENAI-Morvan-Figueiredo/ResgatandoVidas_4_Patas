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

logger = logging.getLogger(__name__)

class GatoListView(ListView):
    model = Gato
    template_name = 'lares_temporarios/lar_temporario_list.html'
    context_object_name = 'gatos'
    paginate_by = 12

    def get_queryset(self):
        try:
            qs = Gato.objects.filter(adotados__isnull=True)
            try:
                qs = qs.order_by('-created_at')
            except FieldError:
                qs = qs.order_by('-id')
            q = self.request.GET.get('q')
            sexo_filter = self.request.GET.get('sexo')

            if q:
                qs = qs.filter(nome__icontains=q)

            if sexo_filter == 'fêmea':
                qs = qs.filter(sexo__lte=1)
            elif sexo_filter == 'macho':
                qs = qs.filter(sexo__gt=1)
            return qs

        except Exception as e:
            logger.exception("Erro em GatoListView.get_queryset: %s", e)
            return Gato.objects.none()


class GatoDetailView(DetailView):
    model = Gato
    template_name = 'lares_temporarios/lar_temporario_detail.html'
    context_object_name = 'gato'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Outros gatos para exibir — exclui o atual
        ctx['other_gatos'] = Gato.objects.filter(adotados__isnull=True).exclude(pk=self.object.pk)[:4]
        return ctx



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
            print(" LarTemporario salvo:", lar.pk)

            historico = HistoricoLarTemporario(
                gato=lar.gato,
                lar_temporario=lar,
                data_inicio=lar.disponibilidade_inicio
            )
            historico.save()
            print(" HistoricoLarTemporario salvo:", historico.pk)

            lar_atual = LarTemporarioAtual(
                gato=lar.gato,
                lar_temporario=lar,
                data_inicio=lar.disponibilidade_inicio
            )
            lar_atual.save()
            print(" LarTemporarioAtual salvo:", lar_atual.pk)

            messages.success(request, "Solicitação de lar temporário enviada com sucesso.")
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

class LarTemporarioSuccessView(TemplateView):
    template_name = 'lares_temporarios/lar_temporario_sucess.html'

# ------------------------


