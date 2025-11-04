from django.db import models
from django.db.models import F, Sum
from clientes.models import Cliente
from productos.models import Producto
from django.utils import timezone
from marketing.models import Promocion

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, related_name="ventas")
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre if self.cliente else 'Cliente Eliminado'}"

    def calcular_total(self):
        suma = self.detalles.aggregate(total_suma=Sum('subtotal'))['total_suma']
        self.total = suma if suma is not None else 0.00
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

        # Precio base
        precio = self.producto.precio

        # ✅ Buscar si hay promociones vigentes aplicables al producto
        hoy = timezone.now().date()
        cliente = self.venta.cliente

        promociones = Promocion.objects.filter(
            productos=self.producto,
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )

        # Filtrar por promociones generales o asignadas al cliente
        if cliente:
            promociones = promociones.filter(
                models.Q(es_general=True) | models.Q(clientes_beneficiados=cliente)
            )

        # ✅ Aplicar la mejor promoción disponible (la de mayor beneficio)
        mejor_precio = precio
        if promociones.exists():
            for promo in promociones:
                precio_promocional = precio
                if promo.tipo == 'PORCENTAJE' and promo.valor_descuento:
                    descuento = precio * (promo.valor_descuento / 100)
                    precio_promocional = precio - descuento
                elif promo.tipo == 'VALOR_FIJO' and promo.valor_descuento:
                    precio_promocional = max(precio - promo.valor_descuento, 0)
                elif promo.tipo == '2X1' and self.cantidad >= 2:
                    # 2x1: pagas la mitad de los productos (redondeo hacia arriba)
                    precio_promocional = precio * (self.cantidad - self.cantidad // 2) / self.cantidad

                if precio_promocional < mejor_precio:
                    mejor_precio = precio_promocional

        self.precio_unitario = mejor_precio
        self.subtotal = self.precio_unitario * self.cantidad

        super().save(*args, **kwargs)

        # 🔁 Control de stock
        if nuevo:
            Producto.objects.filter(pk=self.producto_id).update(stock=F('stock') - self.cantidad)
        else:
            antiguo = DetalleVenta.objects.get(pk=self.pk)
            diferencia = self.cantidad - antiguo.cantidad
            Producto.objects.filter(pk=self.producto_id).update(stock=F('stock') - diferencia)

        # 🔄 Recalcular total de la venta
        self.venta.calcular_total()
