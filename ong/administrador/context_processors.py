from gatos.models import Gato
from adocoes.models import Adotados

# Esta é uma função que vai funcionar em TODAS as páginas.
# Mas serão usadas nas telas de DashBoard do Admin - Para mostrar as quantidades

def dashboard_totals(request):
    # Gatos que ainda não foram adotados
    total_para_adocao = Gato.objects.exclude(id__in=Adotados.objects.values("gato")).count()

    # Gatos em lar temporário que ainda não foram adotados
    total_lar_temporario = Gato.objects.filter(lar_temporario=True).exclude(id__in=Adotados.objects.values("gato")).count()

    # Total de adoções realizadas
    total_adotados = Adotados.objects.count()

    return {
        "total_para_adocao": total_para_adocao,
        "total_lar_temporario": total_lar_temporario,
        "total_adotados": total_adotados,
    }
