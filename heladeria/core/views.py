# core/views.py
from django.shortcuts import render
from django.http import HttpResponseNotFound

def inicio(request):
    visitas = request.session.get('visitas', 0) + 1     
    request.session['visitas'] = visitas
    return render(request, 'inicio.html', {'visitas': visitas})

# ================================
# Vista temporal para probar 404
# ================================
def test_404(request):
    # Forzamos un 404 y mostramos tu template 404.html
    return HttpResponseNotFound(render(request, "404.html").content)
