from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Promocion, Producto  

class ProductoInline(admin.TabularInline):
    model = Promocion.productos.through
    extra = 1
    verbose_name = "Producto en promoción"
    verbose_name_plural = "Productos en promoción"


def activar_promociones(modeladmin, request, queryset):
    updated = queryset.update(activa=True)
    modeladmin.message_user(request, f"{updated} promoción(es) activada(s).")
activar_promociones.short_description = "Activar promociones seleccionadas"

def desactivar_promociones(modeladmin, request, queryset):
    updated = queryset.update(activa=False)
    modeladmin.message_user(request, f"{updated} promoción(es) desactivada(s).")
desactivar_promociones.short_description = "Desactivar promociones seleccionadas"

def extender_fechas(modeladmin, request, queryset):
    for promo in queryset:
        promo.fecha_fin += timedelta(days=7)
        promo.save()
    modeladmin.message_user(request, "Fechas extendidas 7 días para las promociones seleccionadas.")
extender_fechas.short_description = "Extender fechas 7 días"

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'valor_descuento', 'rango_fechas', 'es_vigente_status', 'num_productos')
    list_filter = ('activa', 'tipo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha_inicio'
    filter_horizontal = ('productos',)
    inlines = [ProductoInline]
    actions = [activar_promociones, desactivar_promociones, extender_fechas]

    def rango_fechas(self, obj):
        return f"{obj.fecha_inicio.strftime('%d/%m/%y')} a {obj.fecha_fin.strftime('%d/%m/%y')}"
    rango_fechas.short_description = "Vigencia"

    def es_vigente_status(self, obj):
        hoy = timezone.now().date()
        if obj.es_vigente:
            return format_html('<span style="color: green; font-weight: bold;">ACTIVA</span>')
        elif obj.fecha_fin < hoy:
            return format_html('<span style="color: red;">FINALIZADA</span>')
        elif not obj.activa:
            return format_html('<span style="color: orange;">INACTIVA (Manual)</span>')
        else:
            return format_html('<span style="color: blue;">PRÓXIMA</span>')
    es_vigente_status.short_description = 'Estado'

    def num_productos(self, obj):
        return obj.productos.count() if obj.productos.exists() else "Global/Todos"
    num_productos.short_description = 'Aplica a'


    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Marketing').exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Marketing').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Marketing').exists()

    def save_model(self, request, obj, form, change):
        if obj.fecha_fin < obj.fecha_inicio:
            raise ValidationError("La fecha fin no puede ser anterior a la fecha inicio.")
        if obj.tipo == 'PORCENTAJE' and (obj.valor_descuento <= 0 or obj.valor_descuento > 100):
            raise ValidationError({'valor_descuento': "El porcentaje debe estar entre 1 y 100."})
        if obj.tipo == 'VALOR_FIJO' and (obj.valor_descuento is None or obj.valor_descuento <= 0):
            raise ValidationError({'valor_descuento': "El valor fijo debe ser mayor a cero."})
        if obj.tipo == '2X1' and obj.valor_descuento not in (0, None):
            raise ValidationError({'valor_descuento': "2x1 no requiere valor de descuento."})
        super().save_model(request, obj, form, change)
