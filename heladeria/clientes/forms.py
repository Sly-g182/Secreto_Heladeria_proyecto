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


# heladeria/clientes/forms.py




# heladeria/clientes/forms.py



class EditarPerfilForm(forms.ModelForm):
    """
    Formulario combinado para editar tanto el User como el Cliente asociado.
    """

    # Campos de User
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="Correo Electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )

    # Campos de Cliente
    rut = forms.CharField(
        label="RUT",
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '21742095-4 o 217420954'})
    )

    telefono = forms.CharField(
        label="Teléfono",
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'})
    )

    direccion = forms.CharField(
        label="Dirección",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'rut', 'telefono', 'direccion']

    # -------- VALIDACIONES ----------
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado por otro usuario.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\+569\d{8}$', telefono):
            raise forms.ValidationError("El teléfono debe tener el formato +569XXXXXXXX.")
        return telefono

    def clean_rut(self):
        rut = self.cleaned_data.get('rut').upper().replace(".", "").strip()
        if not re.match(r'^\d{7,8}-?[0-9K]$', rut):
            raise forms.ValidationError("El RUT debe tener el formato 21742095-4 o 217420954.")
        if "-" not in rut:
            rut = rut[:-1] + "-" + rut[-1]
        return rut

    # -------- GUARDADO ----------
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Guardar también los datos del cliente asociado
            cliente, _ = Cliente.objects.get_or_create(user=user)
            cliente.rut = self.cleaned_data.get('rut')
            cliente.telefono = self.cleaned_data.get('telefono')
            cliente.direccion = self.cleaned_data.get('direccion')
            cliente.save()
        return user

    # -------- Inicialización ----------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'cliente'):
            cliente = self.instance.cliente
            self.fields['rut'].initial = cliente.rut
            self.fields['telefono'].initial = cliente.telefono
            self.fields['direccion'].initial = cliente.direccion
