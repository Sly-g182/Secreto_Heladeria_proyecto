from django.db import models
from django.utils import timezone
from datetime import timedelta

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")

    def __str__(self):
        return self.nombre

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.stock < 0:
            raise ValidationError({'stock': "El stock de un producto no puede ser negativo."})
        if self.precio <= 0:
            raise ValidationError({'precio': "El precio debe ser mayor a cero."})
        super().clean()

    @property
    def esta_por_vencer(self):
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - timezone.now().date()) <= timedelta(days=7)
        return False
