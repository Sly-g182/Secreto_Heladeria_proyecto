from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=15, blank=True, null=True)

    # 🔗 Relación muchos-a-muchos hacia Promocion
    promociones = models.ManyToManyField(
        'marketing.Promocion',
        blank=True,
        related_name='clientes_asociados'  # ✅ Nombre único, sin conflictos
    )

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
        """
        Retorna las promociones activas que aplican a este cliente:
        - Promociones asignadas directamente al cliente.
        - Promociones generales (válidas para todos los clientes).
        """
        from django.utils import timezone
        from marketing.models import Promocion
        hoy = timezone.now().date()

        # Promociones personalizadas (asignadas al cliente)
        personalizadas = self.promociones.filter(
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )

        # Promociones generales (válidas para todos)
        generales = Promocion.objects.filter(
            es_general=True,
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )

        # Unimos ambas y eliminamos duplicados
        return (personalizadas | generales).distinct()
