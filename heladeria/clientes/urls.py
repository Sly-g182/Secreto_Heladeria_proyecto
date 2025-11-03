from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.inicio_clientes, name='inicio'),             
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('historial/', views.historial_pedidos, name='historial_pedidos'),
    path('editar/', views.editar_perfil, name='editar')

]
