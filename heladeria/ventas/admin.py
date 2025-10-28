from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser
        
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser



@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'fecha_venta', 'total_formateado')
    search_fields = ('cliente__user__username', 'id')
    inlines = [DetalleVentaInline]

    fieldsets = (
        (None, {
            'fields': ('cliente', 'fecha_venta', 'total')
        }),
    )

    def cliente_nombre(self, obj):
        return obj.cliente.user.username if obj.cliente else "N/A"
    cliente_nombre.short_description = 'Cliente'

    def total_formateado(self, obj):
        return f"${obj.total:,.2f}"
    total_formateado.short_description = 'Total Venta'


    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Marketing').exists() and not request.user.is_superuser:
            return ('cliente', 'fecha_venta', 'total')
        return ('total', 'fecha_venta')

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Marketing').exists() and not request.user.is_superuser:
            return True 
        return super().has_change_permission(request, obj)
        
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.user.groups.filter(name='Marketing').exists() and not request.user.is_superuser:
            extra_context = extra_context or {}
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)
