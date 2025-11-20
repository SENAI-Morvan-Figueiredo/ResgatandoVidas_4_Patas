from django.urls import path
from . import views

app_name = 'adocoes'

urlpatterns = [
    path('', views.GatoListView.as_view(), name='lista'),
    path('gato/<int:pk>/', views.GatoDetailView.as_view(), name='detail'),
    path('obrigado/', views.adocao_sucess, name='adocao_sucess'),
    path('solicitar/', views.formulario_adocao, name='formulario_adocao'),
    path('adotados/', views.AdotadosListView.as_view(), name='adotados_list'),

]