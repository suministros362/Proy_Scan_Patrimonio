from data.excel_repository import ExcelRepository
from data.planilla_generator import PlanillaGenerator
from models.producto import Producto

class PatrimonioService:
    def __init__(self):
        self.repository = ExcelRepository()
        self.generator = PlanillaGenerator()
        self.inventario_general = self.repository.obtener_inventario()
        self.escaneados_sesion: list[Producto] = []
        self.sector_actual = ""  # Nuevo atributo para almacenar el sector actual

        self.colores_disponibles = [
            "#E6F3FF",  # Azul claro
            "#E6FFE6",  # Verde claro
            "#FFF0F5",  # Rosa claro
            "#FFF2CC",  # Amarillo pastel
            "#E8DAEF",  # Violeta claro
            "#E0F7FA",  # Cian claro
            "#FFE0B2",  # Naranja claro
        ]
        self.mapa_colores_sectores = {}  # Diccionario para mapear sectores a colores

    def buscar_producto_por_codigo(self, codigo_escaneado: str) -> Producto | None:
        codigo_limpio = str(codigo_escaneado).strip()
        
        for prod in self.inventario_general:
            # Revisa si coincide con el Nro. Nuevo, de Inventario O de Serie
            if (codigo_limpio == prod.nro_nuevo or 
                codigo_limpio == prod.nro_inventario or 
                codigo_limpio == prod.nro_serie):
                return prod
                
        return None

    def es_duplicado_en_sesion(self, producto: Producto) -> bool:
        """Verifica si el producto ya fue escaneado en la sesión actual por sus identificadores."""
        for p in self.escaneados_sesion:
            # Comprueba si coinciden los identificadores (ignorando campos vacíos)
            if p.nro_nuevo and p.nro_nuevo == producto.nro_nuevo:
                return True
            if p.nro_inventario and p.nro_inventario == producto.nro_inventario:
                return True
            if p.nro_serie and p.nro_serie == producto.nro_serie:
                return True
        return False

    def procesar_codigo(self, codigo_escaneado: str):
        prod = self.buscar_producto_por_codigo(codigo_escaneado)
        
        if not prod:
            return {"encontrado": False, "razon": "no_existe", "producto": None}
            
        # Verificar si ya se escaneó en esta sesión
        if self.es_duplicado_en_sesion(prod):
            return {"encontrado": True, "razon": "duplicado", "producto": prod}
            
        # Si no es duplicado, lo agregamos a la sesión
        self.registrar_escaneo(prod)
        return {"encontrado": True, "razon": "ok", "producto": prod}

    def registrar_escaneo(self, producto: Producto):
        """Agrega el producto al historial de la sesión."""
        self.escaneados_sesion.append(producto)
        producto.sector = self.sector_actual  # Asignar el sector actual al producto escaneado

    def crear_y_registrar_producto(self, datos: dict) -> Producto:
        """Crea un nuevo objeto Producto y lo agrega EXCLUSIVAMENTE a la lista de la sesión activa. NO toca el inventrio maestro ni el Excel."""

        nuevo_prod = Producto(
            nro_inventario=datos.get("nro_inventario", ""),
            nro_nuevo=datos.get("nro_nuevo", ""),
            elemento=datos.get("elemento", ""),
            marca=datos.get("marca", ""),
            modelo=datos.get("modelo", ""),
            nro_serie=datos.get("nro_serie", ""),
            oficina=datos.get("oficina", ""),
            dependencia=datos.get("dependencia", ""),
            observaciones=datos.get("observaciones", "Alta manual en sesión")
        )

    # def crear_y_registrar_producto(self, nro_inventario="", nro_nuevo="", elemento="", 
    #                                marca="", modelo="", nro_serie="", oficina="", dependencia=""):
    #     """Crea un producto nuevo y solo lo agrega a la sesión si se pudo guardar en Excel."""
        
    #     nuevo_prod = Producto(
    #         nro_inventario=nro_inventario,
    #         nro_nuevo=nro_nuevo,
    #         elemento=elemento,
    #         marca=marca,
    #         modelo=modelo,
    #         nro_serie=nro_serie,
    #         oficina=oficina,
    #         dependencia=dependencia
    #     )
        
        # 1. Intentar guardar en disco (Excel Maestro)
        # guardado_ok = self.repository.guardar_nuevo_producto(nuevo_prod)
        
        # 2. Si el guardado falló (ej. Excel bloqueado), abortamos el registro en memoria
        #if not guardado_ok:
        #    return False, None
            
        # 3. Si se guardó con éxito en el Excel, actualizamos la memoria local y la sesión
        #self.inventario_general.append(nuevo_prod)
        self.escaneados_sesion.append(nuevo_prod)
        
        return nuevo_prod

    def exportar_planilla_diaria(self, ruta_archivo: str) -> bool:
        if not self.escaneados_sesion:
            return False
        self.repository.exportar_escaneos(self.escaneados_sesion, ruta_archivo)
        return True

    def limpiar_sesion(self):
        """Limpia la lista de productos escaneados en la sesión actual."""
        self.escaneados_sesion.clear()
        self.sector_actual = ""  # También resetea el sector actual
        self.mapa_colores_sectores.clear()  # Limpiar el mapa de colores de sectores

    def generar_planilla_relevo(self, datos_encabezado: dict, ruta_salida: str) -> bool:
        """Genera la planilla de relevo con los productos escaneados en la sesión."""
        if not self.escaneados_sesion:
            return False
        return self.generator.generar_relevo(datos_encabezado=datos_encabezado, productos=self.escaneados_sesion, ruta_salida=ruta_salida)

    def eliminar_producto_por_indice(self, indice: int) -> bool:
        """Elimina un producto de la sesión por su índice en la lista."""
        if 0 <= indice < len(self.escaneados_sesion):
            self.escaneados_sesion.pop(indice)
            return True
        return False

    def cambiar_sector_actual(self, nuevo_sector: str):
        """Actualizar el sector activo y le asigna un color unico si es nuevo."""
        self.sector_actual = nuevo_sector.strip()

        if self.sector_actual and self.sector_actual not in self.mapa_colores_sectores:
            #Asignamos el siguiente color disponible o rotamos en la lista
            idx_color = len(self.mapa_colores_sectores)%len(self.colores_disponibles)
            self.mapa_colores_sectores[self.sector_actual] = self.colores_disponibles[idx_color]

    def obtener_color_sector(self, sector: str) -> str:
        """Devuelve el solor HEX asignado a un sector (o blanco si no tiene)."""
        return self.mapa_colores_sectores.get(sector)

#----------------------------------------------------------------------------------
#-----Primer servicio de la app, encargado de la lógica de negocio y de la comunicación con el repositorio de datos.
#----------------------------------------------------------------------------------
# from data.excel_repository import ExcelRepository
# from models.producto import Producto

# class PatrimonioService:
#     def __init__(self):
#         self.repository = ExcelRepository()
#         self.inventario_general = self.repository.obtener_inventario()
#         self.escaneados_sesion: list[Producto] = []

#     def buscar_producto_por_codigo(self, codigo_escaneado: str) -> Producto | None:
#         codigo_limpio = str(codigo_escaneado).strip()
        
#         for prod in self.inventario_general:
#             # Revisa si coincide con el Nro. Nuevo, de Inventario O de Serie
#             if (codigo_limpio == prod.nro_nuevo or 
#                 codigo_limpio == prod.nro_inventario or 
#                 codigo_limpio == prod.nro_serie):
#                 return prod
                
#         return None

#     def registrar_escaneo(self, producto: Producto):
#         """Agrega el producto al historial de la sesión."""
#         self.escaneados_sesion.append(producto)

#     def crear_y_registrar_producto(self, codigo: str, nombre: str, categoria: str) -> Producto:
#         """Crea un producto no existente, lo guarda en el Excel maestro y en la sesión."""
#         nuevo_prod = Producto(codigo, nombre, categoria)
        
#         # 1. Guardar en disco (Excel Maestro)
#         self.repository.guardar_nuevo_producto(nuevo_prod)
        
#         # 2. Agregar a la memoria local de la app
#         self.inventario_general.append(nuevo_prod)
#         self.escaneados_sesion.append(nuevo_prod)
        
#         return nuevo_prod

#     def exportar_planilla_diaria(self, ruta_archivo: str) -> bool:
#         if not self.escaneados_sesion:
#             return False
#         self.repository.exportar_escaneos(self.escaneados_sesion, ruta_archivo)
#         return True