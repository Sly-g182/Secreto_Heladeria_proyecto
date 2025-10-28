from django.db import models
from django.db.models import F, Sum
from clientes.models import Cliente
from productos.models import Producto

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

        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio

        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

        if nuevo:
            Producto.objects.filter(pk=self.producto_id).update(stock=F('stock') - self.cantidad)
        else:
            antiguo = DetalleVenta.objects.get(pk=self.pk)
            diferencia = self.cantidad - antiguo.cantidad
            Producto.objects.filter(pk=self.producto_id).update(stock=F('stock') - diferencia)

        self.venta.calcular_total()
