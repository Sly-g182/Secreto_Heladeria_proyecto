from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from datetime import date
from decimal import Decimal
from django.db.models import Q

from marketing.models import Promocion
from .models import Producto
from clientes.models import Cliente
from ventas.models import Venta, DetalleVenta


# --------------------------------------------------------------------------
# -------------------------- LISTADO DE PRODUCTOS --------------------------
# --------------------------------------------------------------------------

def producto_listado(request):
    hoy = date.today()

    # --- PARÁMETROS DE FILTRO Y ORDEN ---
    orden = request.GET.get('orden', '')
    dir = request.GET.get('dir', 'asc')
    categorias_param = request.GET.get('categoria', '')
    solo_promos = request.GET.get('promos', '')  # parámetro para ver solo productos con promociones

    # --- GUARDAR SELECCIÓN DEL PAGINADOR EN SESIÓN ---
    per_page = request.GET.get('per_page')
    if per_page:
        request.session['per_page'] = per_page
    per_page = int(request.session.get('per_page', 6))

    # --- BASE QUERY ---
    productos = Producto.objects.filter(stock__gt=0).select_related('categoria')

    # --- FILTRO POR CATEGORÍA ---
    if categorias_param:
        nombres_categorias = [c.strip() for c in categorias_param.split(',') if c.strip()]
        if nombres_categorias:
            productos = productos.filter(categoria__nombre__in=nombres_categorias)

    # --- PROMOCIONES ACTIVAS ---
    promociones_activas = Promocion.objects.filter(
        activa=True, fecha_inicio__lte=hoy, fecha_fin__gte=hoy
    ).prefetch_related('productos')

    promociones_por_producto = {}
    precios_con_descuento = {}

    for promo in promociones_activas:
        productos_aplicables = promo.productos.all() if promo.productos.exists() else productos
        for p in productos_aplicables:
            promociones_por_producto.setdefault(p.id, []).append({
                "nombre": promo.nombre,
                "descuento": promo.valor_descuento,
                "tipo": promo.tipo
            })

    # --- FILTRO: SOLO PRODUCTOS CON PROMOCIONES ---
    if solo_promos:
        productos = productos.filter(id__in=promociones_por_producto.keys())

    # --- ORDENAMIENTO ASC/DESC ---
    if orden:
        if dir == 'desc':
            productos = productos.order_by(f'-{orden}')
        else:
            productos = productos.order_by(orden)
    else:
        productos = productos.order_by('nombre')

    # --- CALCULAR PRECIO FINAL ---
    for p in productos:
        precio_final = Decimal(p.precio)
        if p.id in promociones_por_producto:
            for promo in promociones_por_producto[p.id]:
                valor_desc = Decimal(promo["descuento"] or 0)
                if promo["tipo"] == "PORCENTAJE":
                    precio_final *= (Decimal("1.0") - valor_desc / Decimal("100"))
                elif promo["tipo"] == "VALOR_FIJO":
                    precio_final -= valor_desc
            precio_final = max(precio_final, Decimal("0"))
        precios_con_descuento[p.id] = {
            "precio_unitario": precio_final,
            "precio_original": Decimal(p.precio),
        }

    # --- AGRUPAR Y PAGINAR POR CATEGORÍA ---
    categorias_dict = {}
    for producto in productos:
        cat = producto.categoria.nombre if producto.categoria else "Sin categoría"
        categorias_dict.setdefault(cat, []).append(producto)

    categorias_paginadas = {}
    for nombre, lista in categorias_dict.items():
        paginator = Paginator(lista, per_page)
        page_number = request.GET.get(f"page_{nombre}", 1)
        categorias_paginadas[nombre] = paginator.get_page(page_number)

    # --- CATEGORÍAS DISPONIBLES PARA EL SELECT ---
    categorias_disponibles = (
        Producto.objects.filter(stock__gt=0, categoria__isnull=False)
        .values_list("categoria__nombre", flat=True)
        .distinct()
        .order_by("categoria__nombre")
    )

    return render(request, "productos/listado.html", {
        "categorias": categorias_paginadas.items(),
        "promociones_por_producto": promociones_por_producto,
        "precios_con_descuento": precios_con_descuento,
        "dir": dir,
        "orden": orden,
        "categorias_disponibles": categorias_disponibles,
        "categorias_filtradas": categorias_param.split(',') if categorias_param else [],
        "per_page": per_page,
        "solo_promos": solo_promos,
    })


# --------------------------------------------------------------------------
# ------------------------- FUNCIONES DE CARRITO ---------------------------
# --------------------------------------------------------------------------

@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def agregar_a_carrito(request, producto_id):
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
            carrito[pid] = {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': cantidad
            }

        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f"{producto.nombre} añadido al pedido.")
    return redirect(request.META.get('HTTP_REFERER', 'productos:producto_listado'))


@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos_en_carrito = []
    total_general = Decimal('0')
    hoy = date.today()

    for id_str, item in list(carrito.items()):
        try:
            producto = Producto.objects.get(id=int(id_str))
            precio_unitario = Decimal(producto.precio)
            precio_original = Decimal(producto.precio)
            cantidad = item['cantidad']

            promociones = Promocion.objects.filter(
                activa=True, productos=producto,
                fecha_inicio__lte=hoy, fecha_fin__gte=hoy
            )

            subtotal = Decimal('0')
            if promociones.exists():
                aplicado_2x1 = False
                for promo in promociones:
                    if promo.tipo == '2X1':
                        pares = cantidad // 2
                        subtotal = precio_unitario * (cantidad - pares)
                        aplicado_2x1 = True
                        break
                    if promo.valor_descuento is not None:
                        valor_desc = Decimal(promo.valor_descuento)
                        if promo.tipo == 'PORCENTAJE':
                            precio_unitario *= (Decimal('1.0') - valor_desc / Decimal('100'))
                        elif promo.tipo == 'VALOR_FIJO':
                            precio_unitario -= valor_desc
                if not aplicado_2x1:
                    precio_unitario = max(precio_unitario, Decimal('0'))
                    subtotal = precio_unitario * cantidad
            else:
                subtotal = precio_unitario * cantidad

            total_general += subtotal
            productos_en_carrito.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio_original': precio_original,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            del carrito[id_str]
            request.session.modified = True

    return render(request, 'productos/carrito.html', {
        'productos': productos_en_carrito,
        'total_general': total_general
    })


@login_required
@user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url='/admin/')
def quitar_de_carrito(request, producto_id):
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
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect('productos:producto_listado')

    try:
        with transaction.atomic():
            cliente = get_object_or_404(Cliente, user=request.user)
            venta = Venta.objects.create(cliente=cliente)
            total_venta = Decimal('0')
            hoy = date.today()

            for id_str, item in carrito.items():
                producto = get_object_or_404(Producto, id=int(id_str))
                cantidad = item['cantidad']

                if producto.stock < cantidad:
                    raise Exception(f"Stock insuficiente para {producto.nombre}.")

                promociones = Promocion.objects.filter(
                    activa=True, productos=producto,
                    fecha_inicio__lte=hoy, fecha_fin__gte=hoy
                )

                precio_unitario = Decimal(producto.precio)
                subtotal = Decimal('0')

                if promociones.exists():
                    aplicado_2x1 = False
                    for promo in promociones:
                        if promo.tipo == '2X1':
                            pares = cantidad // 2
                            subtotal = precio_unitario * (cantidad - pares)
                            aplicado_2x1 = True
                            break
                        if promo.valor_descuento is not None:
                            valor_desc = Decimal(promo.valor_descuento)
                            if promo.tipo == 'PORCENTAJE':
                                precio_unitario *= (Decimal('1.0') - valor_desc / Decimal('100'))
                            elif promo.tipo == 'VALOR_FIJO':
                                precio_unitario -= valor_desc
                    if not aplicado_2x1:
                        precio_unitario = max(precio_unitario, Decimal('0'))
                        subtotal = precio_unitario * cantidad
                else:
                    subtotal = precio_unitario * cantidad

                total_venta += subtotal

                DetalleVenta.objects.create(
                    venta=venta, producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )

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
