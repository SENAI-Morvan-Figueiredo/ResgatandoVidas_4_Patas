from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path("", include("administrador.urls")), 
    path('adocoes/', include('adocoes.urls', namespace='adocoes')),
    path('doacoes/', views.doacoes, name = "doacoes"),
    path('lares_temporarios/', include('lares_temporarios.urls', namespace='lares_temporarios')),
    path('gatos/', include('gatos.urls')),
    path('home/', views.home, name='home'),
    path('home_adm/', views.home_adm, name='home_adm'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)