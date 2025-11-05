from django import forms
from .models import Promocion
from productos.models import Producto
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
            'clientes_beneficiados',  # ✅ nuevo campo
            'es_general',              # ✅ marcar promoción general
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
        valor_descuento = cleaned_data.get('valor_descuento')
        tipo = cleaned_data.get('tipo')
        es_general = cleaned_data.get('es_general')
        clientes_beneficiados = cleaned_data.get('clientes_beneficiados')

        # Validación de fechas
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a la fecha de inicio.")

        # Validación de descuento según tipo
        if tipo in ['PORCENTAJE', 'VALOR_FIJO'] and valor_descuento is None:
            self.add_error('valor_descuento', "El valor de descuento es obligatorio para este tipo de promoción.")
        
        if tipo == 'PORCENTAJE' and (valor_descuento is not None and (valor_descuento < 1 or valor_descuento > 100)):
            self.add_error('valor_descuento', "El porcentaje debe estar entre 1 y 100.")

        # Validación de consistencia entre general y personalizada
        if es_general and clientes_beneficiados.exists():
            self.add_error('es_general', "No puedes marcar como general y seleccionar clientes al mismo tiempo.")

        return cleaned_data
