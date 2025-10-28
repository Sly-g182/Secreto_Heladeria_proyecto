# marketing/signals.py (Asegúrate de que este archivo existe y está guardado)

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Lista de modelos a los que el grupo 'Marketing' debe tener acceso de SOLO LECTURA
MODELOS_SOLO_LECTURA = [
    ('clientes', 'cliente'),
    ('ventas', 'venta'),
    ('ventas', 'detalleventa'),
    ('productos', 'producto'),
    ('productos', 'categoria'),
]

# ESTA ES LA FUNCIÓN QUE DEBES EXPORTAR
def asignar_permisos_marketing(sender, **kwargs):
    """
    Asigna automáticamente el permiso 'Can view' a los modelos
    de otras aplicaciones para el grupo 'Marketing'.
    """
    # ... (el resto de la lógica de la función)
    
    try:
        grupo_marketing = Group.objects.get(name='Marketing')
    except Group.DoesNotExist:
        # Esto puede ocurrir si el fixture del grupo no se cargó primero
        return

    for app_label, model_name in MODELOS_SOLO_LECTURA:
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            view_permission_codename = f'view_{model_name}'
            permiso_view = Permission.objects.get(
                content_type=content_type,
                codename=view_permission_codename
            )
            
            # Asignar el permiso
            if permiso_view not in grupo_marketing.permissions.all():
                grupo_marketing.permissions.add(permiso_view)
                # print(f"Permiso '{permiso_view.name}' asignado al grupo Marketing.")

        except (ContentType.DoesNotExist, Permission.DoesNotExist):
            # Ignorar si algún modelo o permiso no existe (ej. si una app no está migrada)
            continue