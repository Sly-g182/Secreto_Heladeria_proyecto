# heladeria/clientes/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ventas.models import Venta
from django.shortcuts import render, get_object_or_404

from ventas.models import Venta
from clientes.models import Cliente
from django.contrib.auth.decorators import login_required


# ¡IMPORTACIÓN CLAVE! Asegúrate de que este archivo existe y contiene tu formulario personalizado.
from .forms import ClienteUserCreationForm 

# Vistas de autenticación
# ----------------------------------------------------------------------------------

# Vista de registro
def register_view(request):
    if request.method == 'POST':
        # USANDO EL FORMULARIO PERSONALIZADO ClienteUserCreationForm
        form = ClienteUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('clientes:login')
    else:
        # USANDO EL FORMULARIO PERSONALIZADO ClienteUserCreationForm
        form = ClienteUserCreationForm()
    
    return render(request, 'clientes/register.html', {'form': form})

# ---

# Vista de login
def login_view(request):
    # Obtener 'next' de POST o GET. Si es None o '' (cadena vacía), usa el valor por defecto.
    next_url = request.POST.get('next') or request.GET.get('next')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # SOLUCIÓN DEL ERROR NoReverseMatch: Establecer el valor por defecto si es nulo.
            if not next_url:
                next_url = 'clientes:inicio' # 'clientes:inicio' es tu ruta raíz de clientes
                
            return redirect(next_url)
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'clientes/login.html', {'form': form})

# ---

# Vista de logout
def logout_view(request):
    logout(request)
    return redirect('clientes:login')

# ---

# Vista de inicio de clientes (Dashboard)
def inicio_clientes(request):
    # Ya que tu plantilla 'inicio.html' está en la app 'core/templates/',
    # la llamamos sin prefijo.
    return render(request, 'inicio.html')


def historial_pedidos(request):
    # Obtener el cliente del usuario logueado
    cliente = request.user.cliente  # si tienes OneToOne entre User y Cliente
    # Obtener todas las ventas de ese cliente
    ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')

    return render(request, 'ventas/historial.html', {'pedidos': ventas})
