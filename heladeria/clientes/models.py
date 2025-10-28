# clientes/models.py
from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=15, blank=True, null=True)

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
