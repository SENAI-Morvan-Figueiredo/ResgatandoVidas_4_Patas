from django.urls import path
from .views import excluir_gato_ajax, adicionar_gato, editar_gato

urlpatterns = [
    path('adicionar_gato/', adicionar_gato, name='adicionar_gato'), # Função de Registrar gato
    path('editar/<int:gato_id>/', editar_gato, name='editar_gato'), # Função de Editar gato 
    path("excluir_gato_ajax/<int:gato_id>/", excluir_gato_ajax, name="excluir_gato_ajax"),    # Pop-up de confirmar exclusão
    
]