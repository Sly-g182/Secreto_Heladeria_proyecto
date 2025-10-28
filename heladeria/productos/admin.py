from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()  
        return ('nombre', 'descripcion')  

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Marketing').exists() and not request.user.is_superuser:
            return False
        return True


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'stock_alert', 'fecha_vencimiento_format', 'es_por_vencer')
    list_filter = ('categoria', 'stock')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha_vencimiento'
    ordering = ('categoria__nombre', 'nombre')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()  
        
        return ('nombre', 'categoria', 'precio', 'stock', 'fecha_vencimiento')

    def stock_alert(self, obj):
        if obj.stock <= 5:
            return format_html('<span style="color: red; font-weight: bold;">{} (Bajo)</span>', obj.stock)
        return obj.stock
    stock_alert.short_description = 'Stock'

    def fecha_vencimiento_format(self, obj):
        return obj.fecha_vencimiento.strftime('%d/%m/%Y') if obj.fecha_vencimiento else "-"
    fecha_vencimiento_format.short_description = "Vencimiento"

    def es_por_vencer(self, obj):
        if obj.esta_por_vencer:
            return format_html('<span style="color: red; font-weight: bold;">¡PRONTO!</span>')
        return format_html('<span style="color: green;">OK</span>')
    es_por_vencer.short_description = 'Alerta Vencimiento'

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Marketing').exists() and not request.user.is_superuser:
            return False
        return True
