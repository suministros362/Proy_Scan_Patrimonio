from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment
import os

class PlanillaGenerator:
    def __init__(self, ruta_plantilla_relevo=os.path.join("plantillas", "plantilla_relevo.xlsx")):
        self.ruta_plantilla_relevo = ruta_plantilla_relevo

    def generar_relevo(self, datos_encabezado: dict, productos: list, ruta_salida: str) -> bool:
        """Llena la plantilla de relevo con los datos del formulario y los productos de la sesión."""
        try:
            wb = openpyxl.load_workbook(self.ruta_plantilla_relevo)
            ws = wb.active

            # 1. Insertar Encabezados y Fecha Actual
            # 📌 Cambia las celdas ("B2", "B3", etc.) por las reales de tu Excel
            ws["H5"] = datetime.now().strftime("%d/%m/%Y")
            ws["C8"] = datos_encabezado.get("piso", "")
            ws["C9"] = datos_encabezado.get("oficina", "")
            ws["C10"] = datos_encabezado.get("area", "")
            ws["C11"] = datos_encabezado.get("dependencia", "")

            # Configuración de alineación con ajuste de texto
            alineacion_centrado = Alignment(horizontal="center", vertical="center", wrap_text=True)
            alineacion_texto = Alignment(horizontal="left", vertical="center", wrap_text=True)

            ws["H5"].alignment = alineacion_centrado
            ws["C8"].alignment = alineacion_centrado
            ws["C9"].alignment = alineacion_centrado    
            ws["C10"].alignment = alineacion_centrado
            ws["C11"].alignment = alineacion_centrado

            # 2. Insertar Listado de Bienes
            fila_inicio = 14  # 📌 Ajusta la fila inicial de tu tabla

            for idx, prod in enumerate(productos, start=1):
                fila = fila_inicio + idx - 1

                ws[f"A{fila}"] = idx
                ws[f"B{fila}"] = prod.nro_inventario
                ws[f"C{fila}"] = prod.nro_nuevo
                ws[f"D{fila}"] = prod.elemento
                ws[f"E{fila}"] = prod.marca
                ws[f"F{fila}"] = prod.modelo
                ws[f"G{fila}"] = prod.nro_serie
                ws[f"H{fila}"] = prod.observaciones  # Agregando la columna de observaciones

                # Aplicar alineación
                ws[f"A{fila}"].alignment = alineacion_centrado
                ws[f"B{fila}"].alignment = alineacion_centrado
                ws[f"C{fila}"].alignment = alineacion_centrado
                ws[f"D{fila}"].alignment = alineacion_texto
                ws[f"E{fila}"].alignment = alineacion_texto
                ws[f"F{fila}"].alignment = alineacion_texto
                ws[f"G{fila}"].alignment = alineacion_centrado
                ws[f"H{fila}"].alignment = alineacion_texto  # Alineación para observaciones

            # 3. Guardar en el destino elegido
            wb.save(ruta_salida)
            return True

        except Exception as e:
            print(f"Error al generar la planilla de relevo: {e}")
            return False