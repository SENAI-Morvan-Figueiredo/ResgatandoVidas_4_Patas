from django.urls import path
from .views import dashboard_admin_adocoes, excluir_gato_ajax, dashboard_admin_lar_temporario, dashboard_admin_adotados, excluir_adotado_ajax, adicionar_gato, registrar_adocao , registrar_lar_temporario , editar_gato

app_name = 'gatos'

urlpatterns = [
    path("dashboard_admin_adocoes", dashboard_admin_adocoes, name="dashboard_admin_adocoes"),   # Função para conseguir acessar a tela de DashBoard do Admin - Com os gatos para adoção
    path("excluir_gato_ajax/<int:gato_id>/", excluir_gato_ajax, name="excluir_gato_ajax"),    # Pop-up de confirmar exclusão
    path("excluir_adotado_ajax/<int:adotado_id>/", excluir_adotado_ajax, name="excluir_adotado_ajax"),    # Pop-up de confirmar exclusão
    path("dashboard_admin_lar_temporario", dashboard_admin_lar_temporario, name="dashboard_admin_lar_temporario"),    # Função para conseguir acessar a tela de DashBoard do Admin - Com os gatos para Lar_Temporario
    path("dashboard_admin_adotados", dashboard_admin_adotados, name="dashboard_admin_adotados"),    # Função para conseguir acessar a tela de DashBoard do Admin - Com os gatos Adotados
    path('adicionar_gato/', adicionar_gato, name='adicionar_gato'), # Função de Registrar gato
    path("registrar_lar_temporario/", registrar_lar_temporario, name="registrar_lar_temporario"),
    path("registrar_adocao/", registrar_adocao, name="registrar_adocao"),
    path('editar/<int:gato_id>/', editar_gato, name='editar_gato'), # Função de Editar gato
]
