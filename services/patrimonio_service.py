"""Reglas de negocio, estado de sesión y auditoría patrimonial."""

import logging
import uuid

from data.excel_repository import ExcelRepository
from data.planilla_generator import PlanillaGenerator
from models.producto import Producto

logger = logging.getLogger(__name__)


class PatrimonioService:
    """Coordina inventario, sesión activa, validaciones y reportes.

    Args:
        None: Las dependencias se construyen usando la configuración central.

    Returns:
        Instancia de `PatrimonioService` con una sesión nueva activa.

    Raises:
        None: Los errores de lectura se gestionan en el repositorio.
    """

    def __init__(self):
        """Carga las dependencias y crea una sesión de trabajo.

        Args:
            None.

        Returns:
            None.

        Raises:
            None: El repositorio gestiona errores de lectura inicial.
        """
        self.repository = ExcelRepository()
        self.generator = PlanillaGenerator()
        self.inventario_general = self.repository.obtener_inventario()
        self.escaneados_sesion: list[Producto] = []
        self.sector_actual = ""
        self.session_id = ""
        self._session_active = False
        self._scan_count = 0
        self._manual_add_count = 0
        self._iniciar_sesion()

    def _registrar_auditoria(self, evento: str, **detalles) -> None:
        """Escribe un evento de auditoría asociado a la sesión activa.

        Args:
            evento: Nombre estable del tipo de acción registrada.
            **detalles: Contadores y estado no identificable del evento.

        Returns:
            None.

        Raises:
            None.
        """
        logger.info(
            "AUDIT event=%s session_id=%s details=%s",
            evento,
            self.session_id,
            detalles,
        )

    def _iniciar_sesion(self) -> None:
        """Crea un identificador y reinicia los contadores de auditoría.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.session_id = uuid.uuid4().hex
        self._session_active = True
        self._scan_count = 0
        self._manual_add_count = 0
        self._registrar_auditoria("session_started", scan_count=0)

    def finalizar_sesion(self) -> None:
        """Registra el resumen de la sesión actual una sola vez.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        if not self._session_active:
            return
        self._registrar_auditoria(
            "session_ended",
            scan_count=self._scan_count,
            manual_add_count=self._manual_add_count,
        )
        self._session_active = False

    def buscar_producto_por_codigo(
            self, codigo_escaneado: str) -> Producto | None:
        """Busca un producto por inventario, código nuevo o número de serie.

        Args:
            codigo_escaneado: Identificador introducido por el usuario.

        Returns:
            Producto coincidente o `None` si no existe.

        Raises:
            None.
        """
        codigo_limpio = str(codigo_escaneado).strip()

        if not codigo_limpio:
            logger.warning("Se intentó buscar un producto con código vacío.")
            return None

        for prod in self.inventario_general:
            # Revisa si coincide con el Nro. Nuevo, de Inventario O de Serie
            if (
                codigo_limpio == prod.nro_nuevo
                or codigo_limpio == prod.nro_inventario
                or codigo_limpio == prod.nro_serie
            ):
                logger.info("Producto encontrado en el inventario.")
                return prod

        logger.warning("No se encontró producto en el inventario.")
        return None

    def es_duplicado_en_sesion(self, producto: Producto) -> bool:
        """Comprueba si coincide algún identificador no vacío de la sesión.

        Args:
            producto: Producto que se desea comparar con los ya registrados.

        Returns:
            `True` si coincide un identificador; de lo contrario, `False`.

        Raises:
            None.
        """
        for p in self.escaneados_sesion:
            # Comprueba si coinciden los identificadores (ignorando campos
            # vacíos)
            if p.nro_nuevo and p.nro_nuevo == producto.nro_nuevo:
                return True
            if (
                p.nro_inventario
                and p.nro_inventario == producto.nro_inventario
            ):
                return True
            if p.nro_serie and p.nro_serie == producto.nro_serie:
                return True
        return False

    def procesar_codigo(self, codigo_escaneado: str):
        """Busca un código y registra el producto si no es duplicado.

        Args:
            codigo_escaneado: Código recibido del lector o campo de escaneo.

        Returns:
            Diccionario con `encontrado`, `razon` y el `producto` asociado.

        Raises:
            None.
        """
        logger.info("Procesando código escaneado.")
        prod = self.buscar_producto_por_codigo(codigo_escaneado)

        if not prod:
            logger.warning("Código no encontrado en inventario.")
            self._registrar_auditoria(
                "scan_not_found", scan_count=self._scan_count)
            return {
                "encontrado": False,
                "razon": "no_existe",
                "producto": None}

        # Verificar si ya se escaneó en esta sesión
        if self.es_duplicado_en_sesion(prod):
            logger.warning("Código duplicado detectado en sesión.")
            self._registrar_auditoria(
                "scan_duplicate", scan_count=self._scan_count)
            return {"encontrado": True, "razon": "duplicado", "producto": prod}

        # Si no es duplicado, lo agregamos a la sesión
        self.registrar_escaneo(prod)
        logger.info("Escaneo registrado correctamente en la sesión.")
        return {"encontrado": True, "razon": "ok", "producto": prod}

    def procsar_codigo(self, codigo_escaneado: str):
        """Delega en `procesar_codigo` para mantener compatibilidad anterior.

        Args:
            codigo_escaneado: Código que se procesará.

        Returns:
            El mismo resultado que `procesar_codigo`.

        Raises:
            None.
        """
        logger.warning(
            "Se usó un alias de compatibilidad con typo en el "
            "método del servicio."
        )
        return self.procesar_codigo(codigo_escaneado)

    def registrar_escaneo(self, producto: Producto):
        """Añade un producto a la sesión y actualiza su sector y contador.

        Args:
            producto: Producto encontrado en el inventario.

        Returns:
            None.

        Raises:
            None.
        """
        self.escaneados_sesion.append(producto)
        # Asignar el sector actual al producto escaneado
        producto.sector = self.sector_actual
        # Count only accepted inventory scans; duplicates and unknown codes are
        # excluded.
        self._scan_count += 1
        self._registrar_auditoria(
            "scan_registered",
            scan_count=self._scan_count)

    def crear_y_registrar_producto(self, datos: dict) -> Producto:
        """Valida, crea y agrega un producto manual a la sesión activa.

        Args:
            datos: Campos del producto con claves internas del modelo.

        Returns:
            Producto recién creado y agregado a la sesión.

        Raises:
            ValueError: Si falta la descripción obligatoria del elemento.
        """
        error_validacion = self.validar_producto_manual(datos)
        if error_validacion:
            raise ValueError(error_validacion)

        sector_ingresado = str(
            datos.get("sector") or "").strip() or self.sector_actual

        nuevo_prod = Producto(
            nro_inventario=datos.get("nro_inventario", ""),
            nro_nuevo=datos.get("nro_nuevo", ""),
            elemento=datos.get("elemento", ""),
            marca=datos.get("marca", ""),
            modelo=datos.get("modelo", ""),
            nro_serie=datos.get("nro_serie", ""),
            oficina=datos.get("oficina", ""),
            dependencia=datos.get("dependencia", ""),
            observaciones=datos.get("observaciones", "Alta manual en sesión"),
            sector=sector_ingresado
        )

        self.escaneados_sesion.append(nuevo_prod)
        self._manual_add_count += 1
        self._registrar_auditoria(
            "manual_product_added",
            manual_add_count=self._manual_add_count,
            session_item_count=len(self.escaneados_sesion),
        )
        return nuevo_prod

    def validar_producto_manual(self, datos: dict) -> str | None:
        """Valida los campos requeridos para un alta manual.

        Args:
            datos: Valores capturados en el formulario de alta.

        Returns:
            Mensaje de error o `None` cuando los datos son válidos.

        Raises:
            None.
        """
        if not str(datos.get("elemento") or "").strip():
            return "El campo 'Elemento' es obligatorio."
        return None

    def obtener_productos_sesion(self) -> list[Producto]:
        """Devuelve una copia superficial de los productos de la sesión.

        Args:
            None.

        Returns:
            Lista nueva que contiene los productos registrados.

        Raises:
            None.
        """
        return list(self.escaneados_sesion)

    def obtener_producto_sesion(self, indice: int) -> Producto | None:
        """Obtiene un producto por su posición actual en la sesión.

        Args:
            indice: Índice base cero del producto.

        Returns:
            Producto en esa posición o `None` si el índice no es válido.

        Raises:
            None.
        """
        if 0 <= indice < len(self.escaneados_sesion):
            return self.escaneados_sesion[indice]
        return None

    def hay_productos_en_sesion(self) -> bool:
        """Indica si existe al menos un producto en la sesión activa.

        Args:
            None.

        Returns:
            `True` si la sesión contiene productos; si no, `False`.

        Raises:
            None.
        """
        return bool(self.escaneados_sesion)

    def actualizar_inventario(self, ruta_nuevo_archivo: str) -> int:
        """Reemplaza el maestro y recarga el inventario en memoria.

        Args:
            ruta_nuevo_archivo: Ruta del libro `.xlsx` que se va a instalar.

        Returns:
            Cantidad de productos cargados desde el nuevo inventario.

        Raises:
            ValueError: Si la ruta, formato o esquema son inválidos.
            OSError: Si el repositorio no puede completar el reemplazo seguro.
        """
        try:
            productos = self.repository.actualizar_inventario(
                ruta_nuevo_archivo)
        except Exception as exc:
            logger.exception("Falló la actualización del inventario maestro.")
            self._registrar_auditoria(
                "inventory_updated",
                success=False,
                error_type=type(exc).__name__,
            )
            raise

        # Publish the new in-memory list only after the repository replaces the
        # file.
        self.inventario_general = productos
        self._registrar_auditoria(
            "inventory_updated",
            success=True,
            inventory_count=len(productos),
        )
        return len(productos)

    def exportar_planilla_diaria(self, ruta_archivo: str) -> bool:
        """Exporta los elementos de la sesión a un libro Excel diario.

        Args:
            ruta_archivo: Destino del archivo que generará el repositorio.

        Returns:
            `True` si exportó; `False` si no hay datos o falla el guardado.

        Raises:
            None: El repositorio devuelve los fallos como resultado booleano.
        """
        if not self.escaneados_sesion:
            self._registrar_auditoria(
                "report_generated",
                report_type="daily_export",
                success=False,
                item_count=0)
            return False
        success = self.repository.exportar_escaneos(
            self.escaneados_sesion, ruta_archivo)
        self._registrar_auditoria(
            "report_generated",
            report_type="daily_export",
            success=success,
            item_count=len(self.escaneados_sesion),
        )
        return success

    def limpiar_sesion(self):
        """Finaliza y reinicia la sesión sin modificar el inventario maestro.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.finalizar_sesion()
        self.escaneados_sesion.clear()
        self.sector_actual = ""
        self._iniciar_sesion()

    def generar_planilla_relevo(
            self,
            datos_encabezado: dict,
            ruta_salida: str) -> bool:
        """Genera la planilla de relevo para los productos de la sesión.

        Args:
            datos_encabezado: Datos del área y responsables para el reporte.
            ruta_salida: Ruta destino elegida por el usuario.

        Returns:
            `True` si se generó; `False` si no hay datos o falla el generador.

        Raises:
            None: Los errores del generador se devuelven como `False`.
        """
        if not self.escaneados_sesion:
            self._registrar_auditoria(
                "report_generated",
                report_type="relevo",
                success=False,
                item_count=0)
            return False
        success = self.generator.generar_relevo(
            datos_encabezado=datos_encabezado,
            productos=self.escaneados_sesion,
            ruta_salida=ruta_salida,
        )
        self._registrar_auditoria(
            "report_generated",
            report_type="relevo",
            success=success,
            item_count=len(self.escaneados_sesion),
        )
        return success

    def busqueda_masiva(self, resultados: list, ruta_salida: str) -> bool:
        """Genera una planilla de búsqueda masiva a partir de resultados.

        Args:
            resultados: Productos que se incluirán en la búsqueda.
            ruta_salida: Ruta destino elegida por el usuario.

        Returns:
            `True` si se generó; `False` si no hay resultados o falla.

        Raises:
            None: Los errores del generador se devuelven como `False`.
        """
        if not resultados:
            self._registrar_auditoria(
                "report_generated",
                report_type="search",
                success=False,
                item_count=0)
            return False
        success = self.generator.generar_busqueda(
            resultados=resultados, ruta_salida=ruta_salida)
        self._registrar_auditoria(
            "report_generated",
            report_type="search",
            success=success,
            item_count=len(resultados),
        )
        return success

    def generar_planilla_busqueda(self, ruta_salida: str) -> bool:
        """Genera la búsqueda masiva usando los productos de la sesión activa.

        Args:
            ruta_salida: Ruta destino elegida por el usuario.

        Returns:
            Resultado booleano de la generación del reporte.

        Raises:
            None: Los fallos del generador se representan con `False`.
        """
        return self.busqueda_masiva(self.escaneados_sesion, ruta_salida)

    def eliminar_producto_por_indice(self, indice: int) -> bool:
        """Elimina un producto de la sesión por su índice base cero.

        Args:
            indice: Posición del producto en la lista de sesión.

        Returns:
            `True` si se eliminó; `False` si el índice no es válido.

        Raises:
            None.
        """
        if 0 <= indice < len(self.escaneados_sesion):
            self.escaneados_sesion.pop(indice)
            return True
        return False

    def cambiar_sector_actual(self, nuevo_sector: str):
        """Establece el sector que se asignará a los próximos escaneos.

        Args:
            nuevo_sector: Nombre del sector, recortado de espacios periféricos.

        Returns:
            None.

        Raises:
            None.
        """
        self.sector_actual = nuevo_sector.strip()
