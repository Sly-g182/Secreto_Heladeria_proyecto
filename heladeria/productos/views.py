from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from datetime import date

from marketing.models import Promocion
from .models import Producto
from clientes.models import Cliente
from ventas.models import Venta, DetalleVenta


def producto_listado(request):
    """Muestra productos en stock con promociones."""
    hoy = date.today()
    productos_en_stock = Producto.objects.filter(stock__gt=0).select_related('categoria')
    promociones_activas = Promocion.objects.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy).prefetch_related('productos')
    
    promociones_por_producto = {}
    for promo in promociones_activas:
        productos_aplicables = promo.productos.all() or productos_en_stock
        for producto in productos_aplicables:
            promociones_por_producto.setdefault(producto.id, []).append({
                'nombre': promo.nombre,
                'descuento': promo.valor_descuento,
                'tipo': promo.tipo
            })

    categorias = {}
    for producto in productos_en_stock:
        categorias.setdefault(producto.categoria.nombre, []).append(producto)

    return render(request, 'productos/listado.html', {
        'categorias': categorias.items(),
        'promociones_por_producto': promociones_por_producto,
    })


@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def agregar_a_carrito(request, producto_id):
    """Agrega productos al carrito en sesión."""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad <= 0:
            messages.error(request, "Cantidad inválida")
            return redirect('productos:producto_listado')

        carrito = request.session.get('carrito', {})
        pid = str(producto_id)
        if pid in carrito:
            carrito[pid]['cantidad'] += cantidad
        else:
            carrito[pid] = {'id': producto.id, 'nombre': producto.nombre, 'precio': str(producto.precio), 'cantidad': cantidad}

        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f"{producto.nombre} añadido al pedido.")
    return redirect('productos:producto_listado')


@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def ver_carrito(request):
    """Muestra el carrito."""
    carrito = request.session.get('carrito', {})
    productos_en_carrito, total_general = [], 0

    for id_str, item in list(carrito.items()):
        try:
            producto = Producto.objects.get(id=int(id_str))
            subtotal = float(item['precio']) * item['cantidad']
            productos_en_carrito.append({'id': producto.id, 'nombre': producto.nombre,
                                            'cantidad': item['cantidad'], 'precio_unitario': float(item['precio']),
                                            'subtotal': subtotal})
            total_general += subtotal
        except Producto.DoesNotExist:
            del carrito[id_str]
            request.session.modified = True

    return render(request, 'productos/carrito.html', {'productos': productos_en_carrito, 'total_general': total_general})


@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def quitar_de_carrito(request, producto_id):
    """Elimina producto del carrito."""
    carrito = request.session.get('carrito', {})
    pid = str(producto_id)
    if pid in carrito:
        del carrito[pid]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.info(request, "Producto eliminado del pedido.")
    return redirect('productos:ver_carrito')


@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def finalizar_orden(request):
    """Convierte carrito en venta y detalles."""
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect('productos:producto_listado')

    try:
        with transaction.atomic():
            cliente = get_object_or_404(Cliente, user=request.user)
            venta = Venta.objects.create(cliente=cliente)
            total_venta = 0
            hoy = date.today()

            for id_str, item in carrito.items():
                producto = get_object_or_404(Producto, id=int(id_str))
                cantidad = item['cantidad']
                if producto.stock < cantidad:
                    raise Exception(f"Stock insuficiente para {producto.nombre}.")

                
                promociones = Promocion.objects.filter(productos=producto, fecha_inicio__lte=hoy, fecha_fin__gte=hoy, tipo='PORCENTAJE')
                precio_unitario = producto.precio
                if promociones.exists():
                    precio_unitario *= (1 - max(p.valor_descuento for p in promociones) / 100)

                subtotal = precio_unitario * cantidad
                total_venta += subtotal

                DetalleVenta.objects.create(venta=venta, producto=producto, cantidad=cantidad,
                                            precio_unitario=precio_unitario, subtotal=subtotal)

                producto.stock -= cantidad
                producto.save()

            venta.total = total_venta
            venta.save()

            del request.session['carrito']
            request.session.modified = True

            messages.success(request, f"Pedido #{venta.id} completado con éxito.")
            return redirect('ventas:historial_pedidos')

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('productos:ver_carrito')
