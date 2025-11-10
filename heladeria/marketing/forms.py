from django import forms
from django.utils import timezone
from .models import Promocion, Campana
from productos.models import Producto, Categoria
from clientes.models import Cliente


class PromocionForm(forms.ModelForm):
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Productos (dejar vacío para aplicar a TODA la tienda)"
    )

    clientes_beneficiados = forms.ModelMultipleChoiceField(
        queryset=Cliente.objects.all().order_by('user__first_name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Clientes beneficiados (dejar vacío si es general)"
    )

    class Meta:
        model = Promocion
        fields = [
            'nombre',
            'descripcion',
            'tipo',
            'valor_descuento',
            'fecha_inicio',
            'fecha_fin',
            'productos',
            'clientes_beneficiados',
            'es_general',
            'activa'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        hoy = timezone.localdate()

        # 🔹 Validar que la fecha de inicio no sea anterior a hoy
        if fecha_inicio and fecha_inicio < hoy:
            self.add_error('fecha_inicio', "La fecha de inicio no puede ser anterior a hoy.")

        # 🔹 Validar que la fecha de fin no sea anterior a la fecha de inicio
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a la fecha de inicio.")

        return cleaned_data


class CampanaForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all().order_by('nombre'),
        widget=forms.Select,
        required=True,
        label="Categoría de Productos"
    )

    class Meta:
        model = Campana
        fields = [
            'nombre',
            'descripcion',
            'categoria',
            'fecha_inicio',
            'fecha_fin',
            'activa'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        hoy = timezone.localdate()

        # 🔹 Validar que la fecha de inicio no sea anterior a hoy
        if fecha_inicio and fecha_inicio < hoy:
            self.add_error('fecha_inicio', "La fecha de inicio no puede ser anterior a hoy.")

        # 🔹 Validar que la fecha de fin no sea anterior a la fecha de inicio
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a la fecha de inicio.")

        return cleaned_data
