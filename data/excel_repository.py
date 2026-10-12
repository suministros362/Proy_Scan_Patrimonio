"""Acceso al inventario maestro y exportación de productos a Excel."""

import logging
import os
import shutil
import tempfile

import pandas as pd
from tkinter import messagebox

from config import settings
from models.producto import Producto

logger = logging.getLogger(__name__)


def mostrar_error_gui(titulo: str, mensaje: str) -> None:
    """Muestra un error en la interfaz o lo registra en ejecución de pruebas.

    Args:
        titulo: Título del diálogo.
        mensaje: Texto descriptivo del error.

    Returns:
        None.

    Raises:
        None: Los fallos del sistema gráfico se registran y no se propagan.
    """
    if os.environ.get("PYTEST_CURRENT_TEST"):
        logger.error("%s: %s", titulo, mensaje)
        return

    try:
        messagebox.showerror(titulo, mensaje)
    except Exception:
        logger.exception(
            "No se pudo mostrar el diálogo de error en la GUI: %s",
            titulo)


class ExcelRepository:
    """Lee, valida, actualiza y exporta libros del inventario patrimonial.

    Args:
        file_path: Ruta opcional del maestro; por defecto usa la
            configuración central.

    Returns:
        Instancia de `ExcelRepository` asociada a la ruta indicada.

    Raises:
        None.
    """

    def __init__(self, file_path=None):
        """Crea un repositorio asociado a un libro maestro.

        Args:
            file_path: Ruta opcional del libro; usa la configuración central
                si falta.

        Returns:
            None.

        Raises:
            None.
        """
        self.file_path = file_path if file_path is not None else str(
            settings.INVENTORY_PATH)

    def validar_esquema(self) -> tuple[bool, list[str]]:
        """Valida la existencia del maestro y sus columnas requeridas.

        Args:
            None.

        Returns:
            Tupla con validez y diagnósticos; vacía si el esquema es válido.

        Raises:
            None: Los errores de acceso se devuelven como diagnósticos.
        """
        if not os.path.isfile(self.file_path):
            return False, [
                f"No se encontró el archivo de inventario: {
                    self.file_path}"]

        try:
            if os.path.getsize(self.file_path) == 0:
                return False, [
                    f"El archivo de inventario está vacío: {
                        self.file_path}"]
            # Read just the header before loading rows to fail early on a bad
            # contract.
            encabezados = pd.read_excel(
                self.file_path, dtype=str, nrows=0).columns.str.strip()
        except Exception as exc:
            return False, [
                f"No se pudo leer el esquema del inventario '{
                    self.file_path}': {exc}"]

        faltantes = [
            columna
            for columna in settings.INVENTORY_COLUMNS
            if columna not in encabezados
        ]
        if faltantes:
            return False, [
                f"Faltan columnas obligatorias: {
                    ', '.join(faltantes)}"]
        return True, []

    def obtener_inventario(self) -> list[Producto]:
        """Lee el maestro validado y convierte sus filas en productos.

        Args:
            None.

        Returns:
            Productos leídos o lista vacía si el archivo es inválido.

        Raises:
            None: Los fallos se registran y producen una lista vacía.
        """
        esquema_valido, errores = self.validar_esquema()
        if not esquema_valido:
            logger.error("Inventario no válido: %s", "; ".join(errores))
            return []

        try:
            df = pd.read_excel(self.file_path, dtype=str)
        except Exception:
            logger.exception(
                "No se pudo leer el archivo de inventario: %s",
                self.file_path)
            return []

        df.columns = df.columns.str.strip()

        return self._productos_desde_dataframe(df)

    @staticmethod
    def _productos_desde_dataframe(df: pd.DataFrame) -> list[Producto]:
        """Convierte las filas de un DataFrame en entidades de dominio.

        Args:
            df: DataFrame con las columnas configuradas para el inventario.

        Returns:
            Lista de productos con celdas vacías normalizadas a cadenas vacías.

        Raises:
            KeyError: Si falta alguno de los encabezados requeridos.
        """
        productos = []
        for _, row in df.iterrows():
            producto = Producto(
                nro_inventario=ExcelRepository._valor_celda(
                    row, "NRO_INVENTARIO"
                ),
                nro_nuevo=ExcelRepository._valor_celda(row, "NRO_NUEVO"),
                elemento=ExcelRepository._valor_celda(row, "ELEMENTO"),
                marca=ExcelRepository._valor_celda(row, "MARCA"),
                modelo=ExcelRepository._valor_celda(row, "MODELO"),
                nro_serie=ExcelRepository._valor_celda(row, "NRO_SERIE"),
                oficina=ExcelRepository._valor_celda(row, "OFICINA"),
                dependencia=ExcelRepository._valor_celda(row, "DEPENDENCIA"),
            )
            productos.append(producto)

        return productos

    @staticmethod
    def _valor_celda(row, columna: str) -> str:
        """Normaliza una celda de Excel a texto sin espacios periféricos.

        Args:
            row: Fila de pandas con los datos del producto.
            columna: Nombre de la columna que se convertirá.

        Returns:
            Cadena vacía para valores ausentes o texto recortado.

        Raises:
            KeyError: Si la fila no admite el nombre de columna solicitado.
        """
        valor = row.get(columna)
        return "" if pd.isna(valor) else str(valor).strip()

    def actualizar_inventario(self, ruta_nuevo_archivo: str) -> list[Producto]:
        """Valida, instala y devuelve el contenido de un nuevo libro maestro.

        Args:
            ruta_nuevo_archivo: Ruta al `.xlsx` que reemplazará el inventario.

        Returns:
            Productos cargados desde el libro validado.

        Raises:
            ValueError: Si la ruta, el formato o el esquema no son válidos.
            OSError: Si no se puede copiar o reemplazar el libro maestro.
        """
        if not ruta_nuevo_archivo or not str(ruta_nuevo_archivo).strip():
            raise ValueError(
                "Debe seleccionar un archivo Excel de inventario.")
        if os.path.splitext(os.fspath(ruta_nuevo_archivo))[
                1].lower() != ".xlsx":
            raise ValueError(
                "El listado de inventario debe estar en formato .xlsx.")

        archivo_nuevo = ExcelRepository(
            file_path=os.fspath(ruta_nuevo_archivo))
        esquema_valido, errores = archivo_nuevo.validar_esquema()
        if not esquema_valido:
            raise ValueError(
                "El archivo seleccionado no es un inventario válido: " +
                "; ".join(errores))

        try:
            dataframe = pd.read_excel(archivo_nuevo.file_path, dtype=str)
        except Exception as exc:
            raise ValueError(
                f"No se pudo leer el inventario seleccionado: {exc}") from exc

        dataframe.columns = dataframe.columns.str.strip()
        productos = self._productos_desde_dataframe(dataframe)
        directorio_maestro = os.path.dirname(os.path.abspath(self.file_path))
        ruta_temporal = None

        try:
            os.makedirs(directorio_maestro, exist_ok=True)
            descriptor, ruta_temporal = tempfile.mkstemp(
                prefix=".inventario_",
                suffix=os.path.splitext(self.file_path)[1] or ".xlsx",
                dir=directorio_maestro,
            )
            os.close(descriptor)
            shutil.copy2(archivo_nuevo.file_path, ruta_temporal)
            # The temporary copy is in the destination directory so replace
            # stays atomic.
            os.replace(ruta_temporal, self.file_path)
        except OSError as exc:
            raise OSError(
                f"No se pudo reemplazar el inventario maestro '{
                    self.file_path}': {exc}") from exc
        finally:
            if ruta_temporal and os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)

        logger.info(
            "Inventario maestro actualizado: %s productos",
            len(productos))
        return productos

    def guardar_nuevo_producto(self, producto: Producto) -> bool:
        """Agrega un producto al maestro si su esquema es válido.

        Args:
            producto: Producto que se añadirá como una nueva fila.

        Returns:
            `True` si guardó; `False` ante errores de lectura o escritura.

        Raises:
            None: Los errores se registran y se notifican al usuario.
        """
        try:
            archivo_inicializado = os.path.isfile(
                self.file_path) and os.path.getsize(
                self.file_path) > 0
            if archivo_inicializado:
                esquema_valido, errores = self.validar_esquema()
                if not esquema_valido:
                    mensaje = "No se guardó el producto. " + "; ".join(errores)
                    logger.error(mensaje)
                    mostrar_error_gui("Inventario inválido", mensaje)
                    return False
                df = pd.read_excel(self.file_path, dtype=str)
            else:
                df = pd.DataFrame(columns=settings.INVENTORY_COLUMNS)

            nuevo_df = pd.DataFrame([producto.to_dict()])
            df_actualizado = pd.concat([df, nuevo_df], ignore_index=True)
            df_actualizado.to_excel(self.file_path, index=False)
            logger.info(
                "Producto agregado al inventario: %s",
                producto.nro_nuevo or producto.nro_inventario)
            return True
        except PermissionError:
            logger.exception(
                "No se pudo guardar el archivo porque está bloqueado: %s",
                self.file_path)
            mostrar_error_gui(
                "Archivo Bloqueado",
                "No se pudo guardar el registro porque el archivo "
                f"'{self.file_path}' está abierto.\n\n"
                "Por favor, CIERRA EL EXCEL y vuelve a intentar.",
            )
            return False
        except (ValueError, OSError) as exc:
            logger.exception(
                "Error inesperado al guardar el registro en el inventario.")
            mostrar_error_gui(
                "Error inesperado",
                f"Ocurrió un error al guardar: {
                    str(exc)}")
            return False
        except Exception:
            logger.exception(
                "Error no previsto al guardar el registro "
                "en el inventario: %s",
                self.file_path)
            mostrar_error_gui(
                "Error inesperado",
                "Ocurrió un error no previsto al guardar el registro.")
            return False

    def exportar_escaneos(
            self,
            lista_productos: list[Producto],
            ruta_salida: str) -> bool:
        """Escribe los productos de sesión en un nuevo libro Excel.

        Args:
            lista_productos: Productos que se exportarán.
            ruta_salida: Ruta del libro que se creará.

        Returns:
            `True` si exportó correctamente; de lo contrario, `False`.

        Raises:
            None: Los errores se registran y se devuelven como `False`.
        """
        try:
            data = [producto.to_dict() for producto in lista_productos]
            pd.DataFrame(data).to_excel(ruta_salida, index=False)
            logger.info("Escaneos exportados correctamente: %s", ruta_salida)
            return True
        except (PermissionError, ValueError, OSError):
            logger.exception(
                "No se pudieron exportar los escaneos: %s",
                ruta_salida)
            return False
        except Exception:
            logger.exception(
                "Error no previsto al exportar los escaneos: %s",
                ruta_salida)
            return False
