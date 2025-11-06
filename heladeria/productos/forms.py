from django import forms
from clientes.models import Cliente  
from productos.models import Producto
from marketing.models import Promocion

class AgregarAlCarritoForm(forms.Form):
    """
    Formulario simple para añadir un producto al carrito.
    """
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm text-center',
            'min': 1,
            'max': 99,
        })
    )

    producto_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    promocion_aplicada_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
