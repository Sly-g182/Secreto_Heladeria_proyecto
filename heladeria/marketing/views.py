from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import timedelta
from django.db.models import Sum, Count, Subquery, OuterRef, Prefetch
from django.utils import timezone

from clientes.models import Cliente
from productos.models import Producto, Categoria
from .models import Promocion, Campana
from ventas.models import Venta, DetalleVenta
from .forms import PromocionForm, CampanaForm


# ------------------------------
# 🔐 Verificación de usuario staff
# ------------------------------
def is_staff_user(user):
    return user.is_staff


# ------------------------------
# 📊 DASHBOARD PRINCIPAL DE MARKETING
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def marketing_dashboard(request):
    hoy = timezone.now().date()

    promociones_vigentes = Promocion.objects.filter(
        activa=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    campanas_vigentes = Campana.objects.filter(
        activa=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    resumen = {
        'total_clientes': Cliente.objects.count(),
        'total_ventas': Venta.objects.count(),
        'total_productos': Producto.objects.count(),
        'promociones_activas': promociones_vigentes.count(),
        'campanas_activas': campanas_vigentes.count(),
        'ventas_total_monto': Venta.objects.aggregate(total=Sum('total'))['total'] or 0,
    }

    ultimas_ventas = (
        Venta.objects
        .select_related('cliente__user')
        .prefetch_related('detalles__producto')
        .order_by('-fecha_venta')[:5]
    )

    productos_mas_vendidos = (
        DetalleVenta.objects
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    productos_por_vencer = (
        Producto.objects
        .filter(
            stock__gt=0,
            fecha_vencimiento__lte=hoy + timedelta(days=30),
            fecha_vencimiento__gte=hoy
        )
        .order_by('fecha_vencimiento')
    )

    todas_promociones = Promocion.objects.all().order_by('-fecha_inicio')
    todas_campanas = Campana.objects.all().order_by('-fecha_inicio')

    return render(request, 'marketing/dashboard.html', {
        'resumen': resumen,
        'ultimas_ventas': ultimas_ventas,
        'productos_mas_vendidos': productos_mas_vendidos,
        'productos_por_vencer': productos_por_vencer,
        'todas_promociones': todas_promociones,
        'todas_campanas': todas_campanas,
    })


# ------------------------------
# 🟢 CREAR PROMOCIÓN
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def crear_promocion(request):
    if request.method == 'POST':
        form = PromocionForm(request.POST)
        if form.is_valid():
            promocion = form.save()
            messages.success(request, f"✅ Promoción '{promocion.nombre}' creada exitosamente.")
            return redirect('marketing:marketing_dashboard')
        messages.error(request, "❌ Error al crear promoción.")
    else:
        form = PromocionForm()

    hoy = timezone.now().date()
    promociones_activas = Promocion.objects.filter(
        activa=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    return render(request, 'marketing/crear_promocion.html', {
        'form': form,
        'modo': 'Crear',
        'productos': Producto.objects.all(),
        'promociones_activas': promociones_activas,
    })


# ------------------------------
# ✏️ EDITAR PROMOCIÓN
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def editar_promocion(request, pk):
    promocion = get_object_or_404(Promocion, pk=pk)

    if request.method == 'POST':
        form = PromocionForm(request.POST, instance=promocion)
        if form.is_valid():
            promocion = form.save(commit=False)
            promocion.activa = 'activa' in request.POST
            promocion.save()
            form.save_m2m()
            messages.success(request, f"✏️ Promoción '{promocion.nombre}' actualizada correctamente.")
            return redirect('marketing:marketing_dashboard')
        messages.error(request, "❌ Error al actualizar la promoción.")
    else:
        form = PromocionForm(instance=promocion)

    return render(request, 'marketing/crear_promocion.html', {
        'form': form,
        'promocion': promocion,
        'modo': 'Editar',
        'productos': Producto.objects.all()
    })


# ------------------------------
# 🗑️ ELIMINAR PROMOCIÓN
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def eliminar_promocion(request, pk):
    promocion = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        nombre = promocion.nombre
        promocion.delete()
        messages.success(request, f"🗑️ La promoción '{nombre}' fue eliminada correctamente.")
        return redirect('marketing:marketing_dashboard')
    return render(request, 'marketing/eliminar_promocion.html', {'promocion': promocion})


# ------------------------------
# 🟢 CREAR CAMPANA
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def crear_campana(request):
    if request.method == 'POST':
        form = CampanaForm(request.POST)
        if form.is_valid():
            campana = form.save()
            messages.success(request, f"✅ Campaña '{campana.nombre}' creada exitosamente.")
            return redirect('marketing:marketing_dashboard')
        messages.error(request, "❌ Error al crear campaña.")
    else:
        form = CampanaForm()

    hoy = timezone.now().date()
    campanas_activas = Campana.objects.filter(
        activa=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    return render(request, 'marketing/crear_campana.html', {
        'form': form,
        'modo': 'Crear',
        'campanas_activas': campanas_activas,
    })


# ------------------------------
# ✏️ EDITAR CAMPANA
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def editar_campana(request, pk):
    campana = get_object_or_404(Campana, pk=pk)

    if request.method == 'POST':
        form = CampanaForm(request.POST, instance=campana)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Campaña '{campana.nombre}' actualizada.")
            return redirect('marketing:marketing_dashboard')
        messages.error(request, "❌ Error al actualizar campaña.")
    else:
        form = CampanaForm(instance=campana)

    return render(request, 'marketing/crear_campana.html', {
        'form': form,
        'campana': campana,
        'modo': 'Editar',
    })


# ------------------------------
# 🗑️ ELIMINAR CAMPANA
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def eliminar_campana(request, pk):
    campana = get_object_or_404(Campana, pk=pk)
    if request.method == 'POST':
        nombre = campana.nombre
        campana.delete()
        messages.success(request, f"🗑️ La campaña '{nombre}' fue eliminada correctamente.")
        return redirect('marketing:marketing_dashboard')
    return render(request, 'marketing/eliminar_campana.html', {'campana': campana})


# ------------------------------
# 📋 REPORTE DE CLIENTES
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def reporte_clientes(request):
    ultima_compra_subquery = Venta.objects.filter(
        cliente=OuterRef('pk')
    ).order_by('-fecha_venta').values('fecha_venta')[:1]

    datos_clientes = (
        Cliente.objects
        .annotate(
            ultima_compra=Subquery(ultima_compra_subquery),
            total_ordenes=Count('ventas'),
            monto_total_gastado=Sum('ventas__total')
        )
        .select_related('user')
        .order_by('-ultima_compra')
    )

    return render(request, "clientes/reporte_clientes.html", {
        "datos_clientes": datos_clientes
    })


# ------------------------------
# 📢 CAMPANAS DISPONIBLES (para vista pública)
# ------------------------------
def campanas_disponibles(request):
    hoy = timezone.now().date()
    categoria_id = request.GET.get("categoria")

    # Todas las categorías (para filtros o menús)
    categorias = Categoria.objects.all()

    # Campañas vigentes (activas y dentro del rango de fechas)
    campanas = Campana.objects.filter(
        activa=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    ).select_related('categoria')

    # Filtrar por categoría (si el cliente elige una)
    if categoria_id:
        campanas = campanas.filter(categoria_id=categoria_id)

    # Asociar los productos disponibles a cada campaña
    campanas_con_productos = []
    for campana in campanas:
        productos = Producto.objects.filter(
            categoria=campana.categoria,
            stock__gt=0
        ).order_by('nombre')
        if productos.exists():
            campanas_con_productos.append((campana, productos))

    return render(request, "marketing/campanas.html", {
        "campanas_con_productos": campanas_con_productos,
        "categorias": categorias,
        "categoria_id": categoria_id,
    })




