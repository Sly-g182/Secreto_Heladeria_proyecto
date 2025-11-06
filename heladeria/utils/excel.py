import openpyxl
from django.http import HttpResponse
from datetime import datetime


def exportar_a_excel(queryset, campos, encabezados, nombre_archivo="reporte.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Datos"

    ws.append(encabezados)

    for obj in queryset:
        fila = []
        for campo in campos:
            valor = obj
            for attr in campo.split('.'):
                valor = getattr(valor, attr, None)
                if callable(valor):
                    valor = valor()
                if valor is None:
                    break
            if isinstance(valor, datetime):
                valor = valor.strftime("%d/%m/%Y %H:%M")
            fila.append(valor if valor is not None else "N/A")
        ws.append(fila)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
    wb.save(response)
    return response
