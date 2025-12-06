from django.urls import path
from . import views

app_name = 'adocoes'

urlpatterns = [
    path('', views.GatoListView.as_view(), name='lista'),
    path('gato/<int:pk>/', views.GatoDetailView.as_view(), name='detail'),
    path('obrigado/', views.adocao_sucess, name='adocao_sucess'),
    path('solicitar/', views.formulario_adocao, name='formulario_adocao'),
    path('adotados/', views.AdotadosListView.as_view(), name='adotados_list'),
    path("registrar_adocao/", views.registrar_adocao, name="registrar_adocao"),
    path("excluir_adotado_ajax/<int:adotado_id>/", views.excluir_adotado_ajax, name="excluir_adotado_ajax"),    # Pop-up de confirmar exclusão
    path("editar/<int:pk>/", views.editar_adocao, name="editar_adocao"),
    path('buscar_adotantes/<int:gato_id>/', views.buscar_adotantes_para_gato, name='buscar_adotantes'),
    
]