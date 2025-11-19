import logging
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now

from .models import Adocao, Adotados, Gato
from .forms import AdocaoForm

logger = logging.getLogger(__name__)


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


class GatoDetailView(DetailView):
    model = Gato
    template_name = 'adocoes/adocao_detail.html'
    context_object_name = 'gato'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['other_gatos'] = Gato.objects.filter(adotados__isnull=True).exclude(pk=self.object.pk)[:4]
        return ctx


def adocao_sucess(request):
    return render(request, 'adocoes/adocao_sucess.html')


def formulario_adocao(request):
    gato_id = request.GET.get('gato')
    gato = None
    if gato_id:
        gato = get_object_or_404(Gato, id=gato_id)

    if request.method == 'POST':
        form = AdocaoForm(request.POST)
        if form.is_valid():
            gato = adocao.gato
            adocao = form.save(commit=False)

            if gato:
                adocao.gato = gato

            adocao.save()
            gato.adotado = True
            gato.save()
            Adotados.objects.create(
                imagem=gato.imagem,
                gato=gato,
                adocao=adocao,
                data_inicio=now().date(),
            )
            return redirect('adocoes:adocao_sucess')
        else:
             messages.error(request, "Alguns campos estão incorretos ou faltando. Por favor, confira as informações.")
    else:
        form = AdocaoForm()

    return render(request, 'adocoes/adocao_form.html', {'form': form, 'gato': gato})


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
