# marketing/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date, timedelta
from django.db.models import Sum, Count, Subquery, OuterRef
from django.db import models

from clientes.models import Cliente
from productos.models import Producto
from .models import Promocion
from ventas.models import Venta, DetalleVenta
from .forms import PromocionForm


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
    hoy = date.today()

    resumen = {
        'total_clientes': Cliente.objects.count(),
        'total_ventas': Venta.objects.count(),
        'total_productos': Producto.objects.count(),
        'promociones_activas': Promocion.objects.filter(activa=True, fecha_fin__gte=hoy).count(),
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

    return render(request, 'marketing/dashboard.html', {
        'resumen': resumen,
        'ultimas_ventas': ultimas_ventas,
        'productos_mas_vendidos': productos_mas_vendidos,
        'productos_por_vencer': productos_por_vencer,
        'todas_promociones': todas_promociones,
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

    promociones_activas = Promocion.objects.filter(activa=True, fecha_fin__gte=date.today())
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
            form.save()
            messages.success(request, f"✏️ Promoción '{promocion.nombre}' actualizada.")
            return redirect('marketing:marketing_dashboard')
        messages.error(request, "❌ Error al actualizar promoción.")
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
# 📋 REPORTE DE CLIENTES
# ------------------------------
@login_required
@user_passes_test(is_staff_user, login_url='/')
def reporte_clientes(request):
    if not request.user.is_staff:
        return render(
            request,
            "marketing/reporte_clientes.html",
            {"datos_clientes": [], "no_permitido": True}
        )

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
