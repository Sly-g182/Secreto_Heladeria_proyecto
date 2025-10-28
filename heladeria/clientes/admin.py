from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'direccion', 'num_ventas')
    search_fields = ('user__username', 'rut')
    readonly_fields = ('user', 'rut', 'telefono', 'direccion')

    def num_ventas(self, obj):
        return obj.ventas.count()
    num_ventas.short_description = 'N° Ventas'

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Marketing').exists() and not request.user.is_superuser:
            return False
        return True

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
