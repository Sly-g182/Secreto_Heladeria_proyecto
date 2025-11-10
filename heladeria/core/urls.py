from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('test-404/', views.test_404, name='test_404'),  # Ruta temporal de prueba
]
