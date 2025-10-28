from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    path('tienda/', views.producto_listado, name='producto_listado'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    path('carrito/quitar/<int:producto_id>/', views.quitar_de_carrito, name='quitar_de_carrito'),
    path('ordenar/', views.finalizar_orden, name='finalizar_orden'),
]
