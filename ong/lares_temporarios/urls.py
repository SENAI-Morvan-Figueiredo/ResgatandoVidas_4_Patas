from django.urls import path
from . import views

app_name = 'lares_temporarios'

urlpatterns = [
    path('', views.GatoListView.as_view(), name='lista'),
    path('gato/<int:pk>/', views.GatoDetailView.as_view(), name='detail'),
    path('solicitar/', views.formulario_lar_temporario, name='formulario_lar_temporario'),
    path('obrigado/', views.LarTemporarioSuccessView.as_view(), name='lar_temporario_sucess'),
    path("registrar_lar_temporario/", views.registrar_lar_temporario, name="registrar_lar_temporario"),
    path("excluir_lar_temporario_atual_ajax/<int:gato_id>/", views.excluir_lar_temporario_atual_ajax, name="excluir_lar_temporario_atual_ajax"), # Pop-up de confirmar exclusão do lar temporário atual
    path("excluir_historico_lar_temporario_ajax/<int:adotado_id>/", views.excluir_historico_lar_temporario_ajax, name="excluir_historico_lar_temporario_ajax"), # Pop-up de confirmar exclusão do resgistro do histórico de lar temporário
    path("editar/<str:tipo>/<int:pk>/", views.editar_lar_temporario, name="editar_lar_temporario"), # Função de Editar Lar Temporário [tipo: 'atual' ou 'historico'
    path("finalizar/<int:gato_id>/", views.finalizar_lar_temporario, name="finalizar_lar_temporario"), # Função de Finalizar Lar Temporário
    path("buscar_lares/<int:gato_id>/", views.buscar_lares, name="buscar_lares"), # Função de Buscar Lares Temporários por Gato (AJAX)
]