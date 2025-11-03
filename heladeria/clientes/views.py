# heladeria/clientes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ventas.models import Venta
from clientes.models import Cliente

# ¡IMPORTACIÓN CLAVE!
from .forms import ClienteUserCreationForm, EditarPerfilForm  # <-- añadimos el formulario de edición


# ----------------------------------------------------------------------------------
# Vista de registro
def register_view(request):
    if request.method == 'POST':
        form = ClienteUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('clientes:login')
    else:
        form = ClienteUserCreationForm()
    
    return render(request, 'clientes/register.html', {'form': form})


# ----------------------------------------------------------------------------------
# Vista de login
def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if not next_url:
                next_url = 'clientes:inicio'
            return redirect(next_url)
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'clientes/login.html', {'form': form})


# ----------------------------------------------------------------------------------
# Vista de logout
def logout_view(request):
    logout(request)
    return redirect('clientes:login')


# ----------------------------------------------------------------------------------
# Vista de inicio (dashboard)
def inicio_clientes(request):
    return render(request, 'inicio.html')


# ----------------------------------------------------------------------------------
# Vista del historial de pedidos
@login_required
def historial_pedidos(request):
    cliente = request.user.cliente  # OneToOne con User
    ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')
    return render(request, 'ventas/historial.html', {'pedidos': ventas})


# ----------------------------------------------------------------------------------
# NUEVA VISTA: Editar perfil del usuario
@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil se ha actualizado correctamente.")
            return redirect('clientes:inicio')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'clientes/editar.html', {'form': form})

