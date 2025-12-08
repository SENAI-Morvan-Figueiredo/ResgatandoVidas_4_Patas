from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    path("dashboard_admin_lar_temporario", views.dashboard_admin_lar_temporario, name="dashboard_admin_lar_temporario"),    # Função para conseguir acessar a tela de DashBoard do Admin - Com os gatos para Lar_Temporario
    path("dashboard_admin_adotados", views.dashboard_admin_adotados, name="dashboard_admin_adotados"),    # Função para conseguir acessar a tela de DashBoard do Admin - Com os gatos Adotados
    path("dashboard_admin_adocoes", views.dashboard_admin_adocoes, name="dashboard_admin_adocoes"),   # Função para conseguir acessar a tela de DashBoard do Admin - Com os gatos para adoção
]