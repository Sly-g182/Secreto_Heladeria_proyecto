# core/views.py
from django.shortcuts import render



def inicio(request):
    visitas = request.session.get('visitas', 0) + 1     
    request.session['visitas'] = visitas
    return render(request, 'inicio.html', {'visitas': visitas})

