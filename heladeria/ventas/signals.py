print("🚀 Señales de ventas cargadas correctamente")




# ventas/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from ventas.models import Venta
from marketing.models import Promocion
from django.utils import timezone

@receiver(post_save, sender=Venta)
def asignar_promocion_automatica(sender, instance, created, **kwargs):
    """
    Asigna promociones automáticas según comportamiento del cliente:
    - 3 compras seguidas recientes
    - Monto de compra alto
    """
    if not created or not instance.cliente:
        return

    cliente = instance.cliente
    hoy = timezone.now().date()

    # ================================
    # 🔹 Criterio 1: 3 compras seguidas (últimas 30 días)
    # ================================
    ultimas_ventas = cliente.ventas.filter(
        fecha_venta__gte=hoy - timezone.timedelta(days=30)
    ).count()

    if ultimas_ventas >= 3:
        promo_fidelidad = Promocion.objects.filter(
            nombre__icontains="Fidelidad",
            activa=True
        ).first()

        if promo_fidelidad and promo_fidelidad.es_vigente:
            promo_fidelidad.clientes_asignados.add(cliente)
            print(f"✅ Promoción '{promo_fidelidad.nombre}' asignada a {cliente.nombre} (3 compras seguidas)")

    # ================================
    # 🔹 Criterio 2: Monto de compra alto
    # ================================
    MONTO_ALTO = 20000  # 💲 puedes ajustar el umbral

    if instance.total >= MONTO_ALTO:
        promo_vip = Promocion.objects.filter(
            nombre__icontains="Compra Alta",
            activa=True
        ).first()

        if promo_vip and promo_vip.es_vigente:
            promo_vip.clientes_asignados.add(cliente)
            print(f"🎉 Promoción '{promo_vip.nombre}' asignada a {cliente.nombre} (monto alto)")
