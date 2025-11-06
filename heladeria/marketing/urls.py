from django.urls import path
from . import views  # vistas de marketing

app_name = 'marketing'

urlpatterns = [
    path('', views.marketing_dashboard, name='marketing_dashboard'),

    # Promociones
    path('promocion/crear/', views.crear_promocion, name='crear_promocion'),
    path('promocion/editar/<int:pk>/', views.editar_promocion, name='editar_promocion'),
    path('promocion/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar_promocion'),

    # Campañas
    path('campaña/crear/', views.crear_campaña, name='crear_campaña'),
    path('campaña/editar/<int:pk>/', views.editar_campaña, name='editar_campaña'),
    path('campaña/eliminar/<int:pk>/', views.eliminar_campaña, name='eliminar_campaña'),

    # Reportes
    path('reporte-clientes/', views.reporte_clientes, name='reporte_clientes'),
]
