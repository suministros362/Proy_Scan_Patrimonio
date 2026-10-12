"""Adaptador entre las acciones de la interfaz y el servicio patrimonial."""

import logging

from services.patrimonio_service import PatrimonioService

logger = logging.getLogger(__name__)


class PatrimonioController:
    """Expone operaciones de negocio a las ventanas y diálogos.

    Args:
        None: El controlador crea su servicio de patrimonio.

    Returns:
        Instancia de `PatrimonioController` con el servicio inicializado.

    Raises:
        None: Los errores de carga inicial se gestionan en el repositorio.
    """

    def __init__(self):
        """Construye el servicio que atenderá las acciones de la interfaz.

        Args:
            None.

        Returns:
            None.

        Raises:
            None: Los errores de carga inicial se gestionan en el repositorio.
        """
        self.service = PatrimonioService()

    def procesar_codigo_escaneado(self, codigo: str):
        """Envía un código escaneado al servicio.

        Args:
            codigo: Identificador leído desde la interfaz.

        Returns:
            Resultado del procesamiento con estado, razón y producto.

        Raises:
            None.
        """
        logger.info("Procesando código escaneado desde el controlador.")
        return self.service.procesar_codigo(codigo)

    def procsar_codigo_escaneado(self, codigo: str):
        """Mantiene compatibilidad y delega en `procesar_codigo_escaneado`.

        Args:
            codigo: Identificador leído desde la interfaz.

        Returns:
            Resultado del procesamiento del código.

        Raises:
            None.
        """
        logger.warning(
            "Se usó un alias de compatibilidad con typo en el nombre "
            "del método."
        )
        return self.procesar_codigo_escaneado(codigo)

    def agregar_producto_manual(self, datos_producto: dict):
        """Crea un producto manual mediante el servicio.

        Args:
            datos_producto: Campos recogidos por el diálogo de alta.

        Returns:
            Producto agregado a la sesión activa.

        Raises:
            ValueError: Si los datos incumplen las reglas de negocio.
        """
        return self.service.crear_y_registrar_producto(datos_producto)

    def validar_producto_manual(self, datos_producto: dict) -> str | None:
        """Comprueba los datos del formulario sin modificar el estado.

        Args:
            datos_producto: Campos capturados por el diálogo.

        Returns:
            Mensaje de error o `None` cuando la validación es correcta.

        Raises:
            None.
        """
        return self.service.validar_producto_manual(datos_producto)

    def obtener_productos_sesion(self):
        """Obtiene una copia de los productos escaneados en la sesión.

        Args:
            None.

        Returns:
            Lista de productos de la sesión activa.

        Raises:
            None.
        """
        return self.service.obtener_productos_sesion()

    def obtener_producto_sesion(self, indice: int):
        """Obtiene un producto por índice.

        Args:
            indice: Índice base cero del producto.

        Returns:
            Producto o `None` si el índice no es válido.

        Raises:
            None.
        """
        return self.service.obtener_producto_sesion(indice)

    def hay_productos_en_sesion(self) -> bool:
        """Indica si la sesión contiene bienes.

        Args:
            None.

        Returns:
            `True` cuando hay productos; si no, `False`.

        Raises:
            None.
        """
        return self.service.hay_productos_en_sesion()

    def limpiar_sesion_actual(self):
        """Finaliza y crea una nueva sesión de trabajo.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.service.limpiar_sesion()

    def finalizar_sesion(self):
        """Registra el cierre de la sesión actual en la auditoría.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.service.finalizar_sesion()

    def actualizar_inventario(self, ruta_nuevo_archivo: str) -> int:
        """Actualiza el libro maestro y el inventario en memoria.

        Args:
            ruta_nuevo_archivo: Ruta del nuevo libro `.xlsx`.

        Returns:
            Número de productos cargados.

        Raises:
            ValueError: Si el nuevo archivo no cumple el formato o esquema.
            OSError: Si falla el reemplazo seguro del maestro.
        """
        return self.service.actualizar_inventario(ruta_nuevo_archivo)

    def generar_planilla_relevo(
            self,
            datos_encabezado: dict,
            ruta_salida: str):
        """Delega la generación del reporte de relevo.

        Args:
            datos_encabezado: Datos de cabecera del relevamiento.
            ruta_salida: Ruta destino seleccionada.

        Returns:
            `True` si el reporte se creó; de lo contrario, `False`.

        Raises:
            None: El servicio representa errores del generador con `False`.
        """
        return self.service.generar_planilla_relevo(
            datos_encabezado, ruta_salida)

    def generar_planilla_busqueda(self, ruta_salida: str) -> bool:
        """Delega la generación de la planilla de búsqueda.

        Args:
            ruta_salida: Ruta destino seleccionada.

        Returns:
            `True` si el reporte se creó; de lo contrario, `False`.

        Raises:
            None: El servicio representa errores del generador con `False`.
        """
        return self.service.generar_planilla_busqueda(ruta_salida)

    def eliminar_producto_sesion(self, indice: int) -> bool:
        """Elimina un registro de la sesión.

        Args:
            indice: Índice base cero del producto que se eliminará.

        Returns:
            `True` si se eliminó; `False` si el índice no existe.

        Raises:
            None.
        """
        return self.service.eliminar_producto_por_indice(indice)

    def exportar_busqueda_excel(
            self,
            resultados: list,
            ruta_salida: str) -> bool:
        """Exporta una lista explícita de resultados a una planilla.

        Args:
            resultados: Productos que se incluirán en el reporte.
            ruta_salida: Ruta destino seleccionada.

        Returns:
            `True` si se exportó el reporte; de lo contrario, `False`.

        Raises:
            None: El servicio representa errores del generador con `False`.
        """
        return self.service.busqueda_masiva(resultados, ruta_salida)

    def cambiar_sector_actual(self, sector: str):
        """Actualiza el sector que se asignará a escaneos posteriores.

        Args:
            sector: Nombre del sector activo.

        Returns:
            None.

        Raises:
            None.
        """
        self.service.cambiar_sector_actual(sector)
