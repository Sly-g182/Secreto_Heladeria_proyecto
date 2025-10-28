from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    path('carrito/quitar/<int:producto_id>/', views.quitar_de_carrito, name='quitar_de_carrito'),
    path('ordenar/', views.finalizar_orden, name='finalizar_orden'),
    path('historial/', views.historial_pedidos, name='historial_pedidos'),
    path('', views.ventas_simple, name='ventas'),
    
]
