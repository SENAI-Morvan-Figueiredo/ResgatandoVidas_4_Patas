from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from administrador.views import login_view, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path("administrador/", include("administrador.urls")), 
    path('adocoes/', include('adocoes.urls', namespace='adocoes')),
    path('doacoes/', views.doacoes, name = "doacoes"),
    path('lares_temporarios/', include('lares_temporarios.urls', namespace='lares_temporarios')),
    path('gatos/', include('gatos.urls')),
    path('', views.home, name='home'),
    # Alias para não quebrar os templates
    path('login/', login_view, name='login'),
    path("logout/", logout_view, name="logout"),  # Alias do logout
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)