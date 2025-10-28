from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login
    path('login/', include('django.contrib.auth.urls')),  # si usas auth por defecto

    # URLs de tus apps
    path('marketing/', include('marketing.urls')),
    path('productos/', include('productos.urls')),
    path('ventas/', include('ventas.urls')),
    path('clientes/', include('clientes.urls')),
    path('clientes/', include('clientes.urls')),

    # Página de inicio de core
    path('', include('core.urls')),  # '/' muestra inicio.html de core
]
