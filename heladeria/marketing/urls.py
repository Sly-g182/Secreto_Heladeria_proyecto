from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    path('', views.marketing_dashboard, name='marketing_dashboard'),
    path('crear/', views.crear_promocion, name='crear_promocion'),
    path('editar/<int:pk>/', views.editar_promocion, name='editar_promocion'),
    path('reporte-clientes/', views.reporte_clientes, name='reporte_clientes'),
]
