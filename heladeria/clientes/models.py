from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=15, blank=True, null=True)
    imagen = models.ImageField(upload_to='avatars/', blank=True, null=True)
    promociones = models.ManyToManyField('marketing.Promocion', blank=True, related_name='clientes_asociados')

    @property
    def correo(self):
        return self.user.email

    @property
    def nombre(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username

    def __str__(self):
        return self.nombre

    def promociones_vigentes(self):
        from django.utils import timezone
        from marketing.models import Promocion
        hoy = timezone.now().date()
        personalizadas = self.promociones.filter(
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )
        generales = Promocion.objects.filter(
            es_general=True,
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )
        return (personalizadas | generales).distinct()
