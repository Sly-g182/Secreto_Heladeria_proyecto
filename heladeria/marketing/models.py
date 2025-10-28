from django.db import models
from productos.models import Producto

TIPO_PROMOCION = [
    ('PORCENTAJE', 'Porcentaje'),
    ('VALOR_FIJO', 'Valor Fijo'),
    ('2X1', '2x1'),
]

class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_PROMOCION)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    productos = models.ManyToManyField(Producto, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=False)

    @property
    def es_vigente(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin

    def __str__(self):
        return self.nombre
