from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from clientes.models import Cliente
from productos.models import Producto
from marketing.models import Promocion


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, related_name="ventas")
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre if self.cliente else 'Cliente Eliminado'}"

    def calcular_total(self):
        suma = self.detalles.aggregate(total_suma=Sum('subtotal'))['total_suma'] or Decimal('0.00')
        self.total = suma.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.save()


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} en Venta #{self.venta.id}"

    def save(self, *args, **kwargs):
        nuevo = self._state.adding
        hoy = timezone.now().date()
        cliente = self.venta.cliente

        # Precio base del producto
        precio_base = Decimal(self.producto.precio)

        # Buscar promociones vigentes aplicables (por producto o generales)
        promociones = Promocion.objects.filter(
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        ).filter(
            models.Q(productos=self.producto) | models.Q(productos__isnull=True)
        )

        # Si hay cliente, incluir las que sean generales o asignadas a él
        if cliente:
            promociones = promociones.filter(
                models.Q(es_general=True) | models.Q(clientes_beneficiados=cliente)
            )

        mejor_precio = precio_base

        # Aplicar la mejor promoción posible
        for promo in promociones.distinct():
            precio_desc = precio_base

            if promo.tipo == 'PORCENTAJE' and promo.valor_descuento:
                descuento = (precio_base * (promo.valor_descuento / Decimal('100'))).quantize(Decimal('0.01'))
                precio_desc = precio_base - descuento

            elif promo.tipo == 'VALOR_FIJO' and promo.valor_descuento:
                precio_desc = max(precio_base - promo.valor_descuento, Decimal('0.00'))

            elif promo.tipo == '2X1' and self.cantidad >= 2:
                unidades_pagas = (self.cantidad + 1) // 2
                precio_desc = (precio_base * unidades_pagas / self.cantidad).quantize(Decimal('0.01'))

            if precio_desc < mejor_precio:
                mejor_precio = precio_desc

        # Asignar valores finales
        self.precio_unitario = mejor_precio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.subtotal = (self.precio_unitario * self.cantidad).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)

        # Actualizar stock correctamente
        if nuevo:
            Producto.objects.filter(pk=self.producto_id).update(stock=F('stock') - self.cantidad)
        else:
            antiguo = DetalleVenta.objects.get(pk=self.pk)
            diferencia = self.cantidad - antiguo.cantidad
            if diferencia:
                Producto.objects.filter(pk=self.producto_id).update(stock=F('stock') - diferencia)

        # Recalcular total de la venta
        self.venta.calcular_total()
