from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from productos.models import Producto, Categoria
from clientes.models import Cliente


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

    # 🔹 Promoción general o específica
    es_general = models.BooleanField(default=False)

    # 🔹 Clientes específicos que obtienen esta promoción
    clientes_beneficiados = models.ManyToManyField(
        Cliente,
        blank=True,
        related_name='promociones_beneficiadas'
    )

    @property
    def es_vigente(self):
        hoy = timezone.localdate()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validaciones de coherencia de fechas y tipo de promoción."""
        # Validaciones específicas de tipo
        if self.tipo == '2X1' and self.valor_descuento:
            raise ValidationError({'valor_descuento': "Las promociones 2x1 no deben tener valor de descuento."})

        if self.tipo in ['PORCENTAJE', 'VALOR_FIJO'] and not self.valor_descuento:
            raise ValidationError({'valor_descuento': "Debes especificar un valor de descuento."})

        # Validaciones de fecha
        hoy = timezone.localdate()

        # Solo validar si las fechas existen
        if self.fecha_inicio and self.fecha_inicio < hoy:
            raise ValidationError({'fecha_inicio': "La fecha de inicio no puede ser anterior a hoy."})

        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': "La fecha de fin no puede ser anterior a la fecha de inicio."})


class Campana(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='campanas'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Campana"
        verbose_name_plural = "Campanas"

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

    @property
    def es_vigente(self):
        """Retorna True si la campaña está activa y dentro de las fechas."""
        hoy = timezone.localdate()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin

    def clean(self):
        """Validaciones de fechas."""
        hoy = timezone.localdate()

        # Solo validar si las fechas están definidas
        if self.fecha_inicio and self.fecha_inicio < hoy:
            raise ValidationError({'fecha_inicio': "La fecha de inicio no puede ser anterior a hoy."})

        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': "La fecha de fin no puede ser anterior a la fecha de inicio."})
