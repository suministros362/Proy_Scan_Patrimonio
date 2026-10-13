"""Generación de planillas Excel a partir de plantillas institucionales."""

from datetime import datetime
import logging
import openpyxl
from openpyxl.styles import Alignment
import os

import xlrd
from xlutils.copy import copy

from config import settings

logger = logging.getLogger(__name__)


class PlanillaGenerator:
    """Rellena plantillas `.xlsx` y `.xls` con datos de relevamiento.

    Args:
        ruta_plantilla_relevo: Ruta opcional de la plantilla de relevo.
        ruta_plantilla_busqueda: Ruta opcional de la plantilla de búsqueda.

    Returns:
        Instancia de `PlanillaGenerator` con rutas resueltas.

    Raises:
        None.
    """

    def __init__(
            self,
            ruta_plantilla_relevo=None,
            ruta_plantilla_busqueda=None):
        """Configura las rutas de plantillas predeterminadas o personalizadas.

        Args:
            ruta_plantilla_relevo: Ruta opcional a la plantilla de relevo.
            ruta_plantilla_busqueda: Ruta opcional a la plantilla `.xls`.

        Returns:
            None.

        Raises:
            None.
        """
        self.ruta_plantilla_relevo = (
            ruta_plantilla_relevo or str(settings.RELEVO_TEMPLATE_PATH)
        )
        self.ruta_plantilla_busqueda = (
            ruta_plantilla_busqueda or str(settings.SEARCH_TEMPLATE_PATH)
        )

    def generar_relevo(
            self,
            datos_encabezado: dict,
            productos: list,
            ruta_salida: str) -> bool:
        """Genera un libro de relevo con metadatos y filas de bienes.

        Args:
            datos_encabezado: Valores del área y responsables para la cabecera.
            productos: Productos que se escribirán desde la fila configurada.
            ruta_salida: Ruta del archivo `.xlsx` que se creará.

        Returns:
            `True` si se guardó; `False` si falta la plantilla o falla.

        Raises:
            None: Los fallos se registran y se indican mediante `False`.
        """
        if not os.path.isfile(self.ruta_plantilla_relevo):
            logger.error(
                "No se encontró la plantilla de relevo requerida: %s",
                self.ruta_plantilla_relevo)
            return False

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
            ws["F8"] = datos_encabezado.get("responsable", "")
            ws["F9"] = datos_encabezado.get("subresponsable", "")
            ws["F10"] = datos_encabezado.get("telefono", "")

            # Configuración de alineación con ajuste de texto
            alineacion_centrado = Alignment(
                horizontal="center", vertical="center", wrap_text=True)
            alineacion_texto = Alignment(
                horizontal="left", vertical="center", wrap_text=True)

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
                # Agregando la columna de observaciones
                ws[f"H{fila}"] = prod.observaciones
                # Agregando la columna de sector
                ws[f"I{fila}"] = prod.sector.upper()

                # Aplicar alineación
                ws[f"A{fila}"].alignment = alineacion_centrado
                ws[f"B{fila}"].alignment = alineacion_centrado
                ws[f"C{fila}"].alignment = alineacion_centrado
                ws[f"D{fila}"].alignment = alineacion_texto
                ws[f"E{fila}"].alignment = alineacion_texto
                ws[f"F{fila}"].alignment = alineacion_texto
                ws[f"G{fila}"].alignment = alineacion_centrado
                # Alineación para observaciones
                ws[f"H{fila}"].alignment = alineacion_texto
                # Alineación para sector
                ws[f"I{fila}"].alignment = alineacion_texto

            # 3. Guardar en el destino elegido
            wb.save(ruta_salida)
            return True

        except Exception:
            logger.exception(
                "No se pudo generar la planilla de relevo: %s",
                ruta_salida)
            return False

    def generar_busqueda(self, resultados: list, ruta_salida: str) -> bool:
        """Genera la búsqueda masiva en formato Excel 97-2003.

        Los códigos se escriben en la columna A y luego en la B, a continuación
        de los elementos escritos en A.

        Args:
            resultados: Objetos que proporcionan el atributo `nro_nuevo`.
            ruta_salida: Ruta del archivo `.xls` que se creará.

        Returns:
            `True` si guardó; `False` si falta la plantilla o falla el proceso.

        Raises:
            None: Los fallos se registran y se indican mediante `False`.
        """
        if not os.path.isfile(self.ruta_plantilla_busqueda):
            logger.error(
                "No se encontró la plantilla de búsqueda requerida: %s",
                self.ruta_plantilla_busqueda)
            return False

        try:
            # 1. Cargar el libro .xls existente (formatting_info=True conserva
            # fuentes y estilos)
            rb = xlrd.open_workbook(
                self.ruta_plantilla_busqueda,
                formatting_info=True)

            # 2. Crear una copia modificable usando xlutils
            wb = copy(rb)
            ws = wb.get_sheet(0)  # Primera hoja

            # -------------------------------------------------------------
            # xlrd/xlwt use zero-based row and column indexes.
            # -------------------------------------------------------------

            # 4. Volcado de datos (Ejemplo: Fila 8 en Excel es índice 7)
            fila_inicio_A = 3  # ⚠️ Fila 8 de Excel (base 0)
            cantidad_elementos = len(resultados)

            # A) Pegar códigos en Columna A (Columna 0)
            for i, item in enumerate(resultados):
                fila_actual_A = fila_inicio_A + i
                codigo = getattr(item, "nro_nuevo", "")
                ws.write(fila_actual_A, 0, codigo)  # Columna 0 = Columna A

            # B) Pegar los MISMOS códigos en Columna B (Columna 1), a
            # continuación de A
            fila_inicio_B = fila_inicio_A + cantidad_elementos

            for i, item in enumerate(resultados):
                fila_actual_B = fila_inicio_B + i
                codigo = getattr(item, "nro_nuevo", "")
                ws.write(fila_actual_B, 1, codigo)  # Columna 1 = Columna B

            # 5. Guardar manteniendo el formato .xls
            # Asegurarse de que la extensión sea .xls
            extension = settings.SEARCH_REPORT_EXTENSION
            if not ruta_salida.lower().endswith(extension):
                ruta_salida = os.path.splitext(
                    ruta_salida)[0] + extension

            wb.save(ruta_salida)
            return True

        except Exception:
            logger.exception(
                "No se pudo generar la planilla de búsqueda: %s",
                ruta_salida)
            return False
