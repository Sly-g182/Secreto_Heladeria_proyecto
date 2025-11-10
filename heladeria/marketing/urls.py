from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    path('', views.marketing_dashboard, name='marketing_dashboard'),

    # Promociones
    path('promocion/crear/', views.crear_promocion, name='crear_promocion'),
    path('promocion/editar/<int:pk>/', views.editar_promocion, name='editar_promocion'),
    path('promocion/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar_promocion'),

    # Campañas
    path('campana/crear/', views.crear_campana, name='crear_campana'),
    path('campana/editar/<int:pk>/', views.editar_campana, name='editar_campana'),
    path('campana/eliminar/<int:pk>/', views.eliminar_campana, name='eliminar_campana'),
    path('campanas/filtro/', views.campanas_disponibles, name='campanas_disponibles'),


    # Reportes
    path('reporte-clientes/', views.reporte_clientes, name='reporte_clientes'),
]
