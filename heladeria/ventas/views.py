from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Venta
from .models import Producto
from .forms import AgregarAlCarritoForm
from django.shortcuts import render, redirect, get_object_or_404



@login_required
def ver_carrito(request):
    
    carrito = request.session.get('carrito', {})
    return render(request, 'ventas/carrito.html', {'carrito': carrito})

@login_required
def agregar_a_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = AgregarAlCarritoForm(request.POST)
        if form.is_valid():
            carrito = request.session.get('carrito', {})
            carrito[producto_id] = form.cleaned_data['cantidad']
            request.session['carrito'] = carrito
            return redirect('ver_carrito')
    else:
        form = AgregarAlCarritoForm(initial={'producto_id': producto_id})
    return render(request, 'ventas/agregar_carrito.html', {'form': form, 'producto': producto})

@login_required
def quitar_de_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    return redirect('ver_carrito')

@login_required
def finalizar_orden(request):
    
    carrito = request.session.get('carrito', {})
    if carrito:
        
        request.session['carrito'] = {}
    return render(request, 'ventas/finalizar.html')

@login_required
def historial_pedidos(request):
    ventas = Venta.objects.filter(cliente=request.user.cliente)
    return render(request, 'ventas/historial.html', {'ventas': ventas})

def ventas_simple(request):
    ventas = Venta.objects.all()  
    return render(request, "ventas/ventas.html", {"ventas": ventas})