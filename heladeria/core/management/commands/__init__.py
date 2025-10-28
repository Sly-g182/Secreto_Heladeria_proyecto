from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Carga todas las fixtures en el orden correcto'

    def handle(self, *args, **options):
        fixtures_ordenadas = [
            'clientes/fixtures/clientes.json',
            'productos/fixtures/productos.json',
            'marketing/fixtures/promociones.json',
            'ventas/fixtures/ventas.json',
        ]

        for fixture in fixtures_ordenadas:
            self.stdout.write(f'Cargando fixture: {fixture}...')
            call_command('loaddata', fixture)
        
        self.stdout.write(self.style.SUCCESS('Todas las fixtures se cargaron correctamente.'))
