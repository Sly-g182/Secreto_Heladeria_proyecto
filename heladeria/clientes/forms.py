from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import Cliente


class ClienteUserCreationForm(UserCreationForm):
    # Campos del usuario
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={'placeholder': ''})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Apellido",
        widget=forms.TextInput(attrs={'placeholder': ''})
    )
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'})
    )

    # Campos del cliente
    rut = forms.CharField(
        max_length=12,
        required=True,
        label="RUT",
        widget=forms.TextInput(attrs={'placeholder': '21742095-4 o 217420954'})
    )
    telefono = forms.CharField(
        max_length=12,
        required=True,
        label="Teléfono",
        widget=forms.TextInput(attrs={'placeholder': '+56912345678'})
    )
    direccion = forms.CharField(
        max_length=200,
        required=False,
        label="Dirección",
        widget=forms.TextInput(attrs={'placeholder': ''})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'first_name',
            'last_name',
            'email',
            'rut',
            'telefono',
            'direccion',
        )

    # --- VALIDACIONES PERSONALIZADAS ---

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Formato chileno estricto: +569 seguido de 8 dígitos
        if not re.match(r'^\+569\d{8}$', telefono):
            raise ValidationError("El teléfono debe tener el formato +569XXXXXXXX (8 dígitos después del +569).")
        return telefono

    def clean_rut(self):
        rut = self.cleaned_data.get('rut').upper().replace(".", "").strip()

        # Acepta solo estos dos formatos: 21742095-4 o 217420954
        if not re.match(r'^\d{7,8}-?[0-9K]$', rut):
            raise ValidationError("El RUT debe tener el formato 21742089-5 o 217420895 (sin puntos).")

        # Si no tiene guion, lo agregamos antes del dígito verificador
        if "-" not in rut:
            rut = rut[:-1] + "-" + rut[-1]

        cuerpo, dv = rut.split("-")

        # Validación del dígito verificador (algoritmo oficial)
        suma = 0
        multiplo = 2
        for c in reversed(cuerpo):
            suma += int(c) * multiplo
            multiplo = 2 if multiplo == 7 else multiplo + 1
        resto = 11 - (suma % 11)
        dv_esperado = 'K' if resto == 10 else '0' if resto == 11 else str(resto)

        if dv != dv_esperado:
            raise ValidationError("El RUT ingresado no es válido.")

        # ✅ Formatear a 21.742.095-4 antes de guardar
        cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
        rut_formateado = f"{cuerpo_formateado}-{dv}"

        return rut_formateado

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            Cliente.objects.create(
                user=user,
                rut=self.cleaned_data.get('rut'),
                telefono=self.cleaned_data.get('telefono'),
                direccion=self.cleaned_data.get('direccion'),
            )
        return user
