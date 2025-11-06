from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Q

from ventas.models import Venta
from clientes.models import Cliente
from .forms import ClienteUserCreationForm, EditarPerfilForm, CambiarPasswordForm


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


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not next_url:
                next_url = 'clientes:inicio'
            messages.success(request, f"¡Bienvenido, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'clientes/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('clientes:login')


def inicio_clientes(request):
    return render(request, 'inicio.html')


@login_required
def historial_pedidos(request):
    cliente = request.user.cliente
    ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')
    return render(request, 'ventas/historial.html', {'pedidos': ventas})


@login_required
def editar_perfil(request):
    """Vista para editar los datos del perfil del usuario, incluyendo imagen de perfil."""
    cliente = Cliente.objects.get(user=request.user)

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()  # El form ya se encarga de actualizar User y Cliente, incluyendo imagen
            messages.success(request, "Tu perfil se ha actualizado correctamente.")
            return redirect('clientes:editar_perfil')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = EditarPerfilForm(instance=request.user)

    return render(request, 'clientes/editar.html', {'form': form, 'cliente': cliente})


@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario."""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            nueva_password = form.cleaned_data.get('nueva_password')
            user = request.user
            user.set_password(nueva_password)
            user.save()
            update_session_auth_hash(request, user)  # mantiene sesión activa
            messages.success(request, "Tu contraseña ha sido cambiada correctamente.")
            return redirect('clientes:editar_perfil')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = CambiarPasswordForm()

    return render(request, 'clientes/cambiar_password.html', {'form': form})


@staff_member_required
def reporte_clientes(request):
    """Vista del panel de administración que lista los clientes registrados."""
    q = request.GET.get('q', '').strip()
    if q:
        datos_clientes = Cliente.objects.filter(
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(rut__icontains=q)
        )
    else:
        datos_clientes = Cliente.objects.all()

    context = {'datos_clientes': datos_clientes, 'now': timezone.now()}
    return render(request, "clientes/reporte_clientes.html", context)
