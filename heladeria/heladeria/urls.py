from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación (login/logout/password_reset)
    path('accounts/', include('django.contrib.auth.urls')),

    # Aplicaciones principales
    path('clientes/', include('clientes.urls')),
    path('productos/', include('productos.urls')),
    path('ventas/', include('ventas.urls')),
    path('marketing/', include('marketing.urls')),
    path('', include('core.urls')),  # Página de inicio
]

# En modo DEBUG, servir archivos multimedia (avatars, imágenes, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
