from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Cliente


class ClienteUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Nombre")
    last_name = forms.CharField(max_length=150, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    rut = forms.CharField(max_length=12, required=True, label="RUT")
    telefono = forms.CharField(max_length=12, required=True, label="Teléfono")
    direccion = forms.CharField(max_length=200, required=False, label="Dirección")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'rut', 'telefono', 'direccion'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\+569\d{8}$', telefono):
            raise ValidationError("El teléfono debe tener el formato +569XXXXXXXX.")
        return telefono

    def clean_rut(self):
        rut = self.cleaned_data.get('rut').upper().replace(".", "").strip()
        if not re.match(r'^\d{7,8}-?[0-9K]$', rut):
            raise ValidationError("El RUT debe tener el formato 21742095-4 o 217420954.")
        if "-" not in rut:
            rut = rut[:-1] + "-" + rut[-1]
        return rut

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
                direccion=self.cleaned_data.get('direccion')
            )
        return user


class EditarPerfilForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario", max_length=150, required=False)
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)
    email = forms.EmailField(label="Correo Electrónico", required=False)
    rut = forms.CharField(label="RUT", max_length=12, required=False)
    telefono = forms.CharField(label="Teléfono", max_length=12, required=False)
    direccion = forms.CharField(label="Dirección", max_length=200, required=False)

    # ✅ Usamos FileInput (sin el ClearableFileInput que mostraba “Actualmente: imagen.jpg Limpiar”)
    imagen = forms.ImageField(
        label="Imagen de perfil",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

        cliente = getattr(self.user, 'cliente', None)
        if cliente:
            self.fields['rut'].initial = cliente.rut
            self.fields['telefono'].initial = cliente.telefono
            self.fields['direccion'].initial = cliente.direccion

        self.fields['username'].initial = self.user.username
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.user.id
        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not re.match(r'^\+569\d{8}$', telefono):
            raise forms.ValidationError("El teléfono debe tener el formato +569XXXXXXXX.")
        return telefono

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if not imagen:
            return None  # No se subió nueva imagen, mantener la actual
        content_type = getattr(imagen, 'content_type', '')
        if not content_type.startswith('image/'):
            raise forms.ValidationError("El archivo debe ser una imagen válida (jpg, png, etc.).")
        if imagen.size > 2 * 1024 * 1024:
            raise forms.ValidationError("La imagen no puede superar los 2 MB.")
        return imagen

    def save(self, commit=True):
        user = self.user
        user.username = self.cleaned_data.get('username', user.username)
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.email = self.cleaned_data.get('email', user.email)
        if commit:
            user.save()

        cliente, _ = Cliente.objects.get_or_create(user=user)
        cliente.rut = self.cleaned_data.get('rut') or cliente.rut
        cliente.telefono = self.cleaned_data.get('telefono') or cliente.telefono
        cliente.direccion = self.cleaned_data.get('direccion') or cliente.direccion
        if self.cleaned_data.get('imagen'):
            cliente.imagen = self.cleaned_data['imagen']
        if commit:
            cliente.save()

        return user


class CambiarPasswordForm(forms.Form):
    nueva_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu nueva contraseña'}),
        error_messages={'required': 'Este campo es obligatorio.'},
    )
    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la nueva contraseña'}),
        error_messages={'required': 'Este campo es obligatorio.'},
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get("nueva_password")
        confirmar = cleaned_data.get("confirmar_password")

        if not nueva or not confirmar:
            raise forms.ValidationError("Debes completar ambos campos.")
        if nueva != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        if len(nueva) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", nueva):
            raise forms.ValidationError("Debe contener al menos una letra mayúscula.")
        if not re.search(r"\d", nueva):
            raise forms.ValidationError("Debe incluir al menos un número.")

        return cleaned_data
