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

        # Paleta para MODO CLARO (colores pastel con variantes clara y ligeramente más oscura)
        self.colores_modo_claro = [
            ("#E6F3FF", "#D0E7FF"),  # Azul pastel
            ("#E6FFE6", "#D1FFD1"),  # Verde pastel
            ("#FFF0F5", "#FFE0EB"),  # Rosa pastel
            ("#FFF2CC", "#FFE599"),  # Amarillo pastel
            ("#E8DAEF", "#D7BDE2"),  # Violeta pastel
            ("#E0F7FA", "#B2EBF2"),  # Cian pastel
            ("#FFE0B2", "#FFCC80"),  # Naranja pastel
        ]

        # Paleta para MODO OSCURO (colores profundos/saturados para no encandilar y permitir lectura blanca)
        self.colores_modo_oscuro = [
            ("#1A365D", "#2A4365"),  # Azul oscuro
            ("#1C4532", "#22543D"),  # Verde oscuro
            ("#4A154B", "#611F69"),  # Violeta oscuro
            ("#5B3A00", "#744A00"),  # Café/Amarillo oscuro
            ("#4C1D95", "#5B21B6"),  # Púrpura oscuro
            ("#083344", "#164E63"),  # Cian oscuro
            ("#6C2BD9", "#7C3AED"),  # Naranja/Marrón oscuro
        ]

        # Guardamos ambas listas en el mapa de colores
        self.mapa_colores_sectores = {}

        # self.colores_disponibles = [
        #     ("#E6F3FF", "#D0E7FF"),  # Azul pastel
        #     ("#E6FFE6", "#D1FFD1"),  # Verde pastel
        #     ("#FFF0F5", "#FFE0EB"),  # Rosa pastel
        #     ("#FFF2CC", "#FFE599"),  # Amarillo pastel
        #     ("#E8DAEF", "#D7BDE2"),  # Violeta pastel
        #     ("#E0F7FA", "#B2EBF2"),  # Cian pastel
        #     ("#FFE0B2", "#FFCC80"),  # Naranja pastel
        # ]
        # self.mapa_colores_sectores = {}  # Diccionario para mapear sectores a colores

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

        sector_ingresado = datos.get("sector", "").strip() or self.sector_actual

        if sector_ingresado:
            # self.cambiar_sector_actual(sector_ingresado)  # Actualiza el sector actual y asigna color si es nuevo
            self.asignar_color_a_sector(sector_ingresado)  # Asigna color al sector si es nuevo

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

    def busqueda_masiva(self, resultados: list, ruta_salida: str) -> bool:
        """Genera la planilla de búsqueda masiva con los resultados proporcionados."""
        if not resultados:
            return False
        return self.generator.generar_busqueda(resultados=resultados, ruta_salida=ruta_salida)

    def eliminar_producto_por_indice(self, indice: int) -> bool:
        """Elimina un producto de la sesión por su índice en la lista."""
        if 0 <= indice < len(self.escaneados_sesion):
            self.escaneados_sesion.pop(indice)
            return True
        return False

    def cambiar_sector_actual(self, nuevo_sector: str):
        """Actualizar el sector activo y le asigna un color único si es nuevo."""
        self.sector_actual = nuevo_sector.strip()

        if self.sector_actual and self.sector_actual not in self.mapa_colores_sectores:
            # Asignamos el siguiente índice de color rotando en la lista
            idx_color = len(self.mapa_colores_sectores) % len(self.colores_modo_claro)
            
            # 🔴 Antes: self.mapa_colores_sectores[sector] = idx_color
            # 🟢 Ahora: guardamos la posición con self.sector_actual
            self.mapa_colores_sectores[self.sector_actual] = idx_color
    # def cambiar_sector_actual(self, nuevo_sector: str):
    #     """Actualizar el sector activo y le asigna un color unico si es nuevo."""
    #     self.sector_actual = nuevo_sector.strip()

    #     if self.sector_actual and self.sector_actual not in self.mapa_colores_sectores:
    #         #Asignamos el siguiente color disponible o rotamos en la lista
    #         idx_color = len(self.mapa_colores_sectores) % len(self.colores_modo_claro)
    #         self.mapa_colores_sectores[sector] = idx_color


    def asignar_color_a_sector(self, sector: str):
        """Asigna un índice de color a un sector si no lo tiene aún."""
        if sector not in self.mapa_colores_sectores:
            idx = len(self.mapa_colores_sectores) % len(self.colores_modo_claro)
            self.mapa_colores_sectores[sector] = idx

    def obtener_color_sector(self, sector: str, es_par: bool = False, es_modo_oscuro: bool = False) -> tuple[str, str]:
        """
        Devuelve una tupla (color_fondo, color_texto) asignada al sector.
        Garantiza contraste óptimo según la paridad y el modo (claro/oscuro).
        """
        if sector in self.mapa_colores_sectores:
            idx = self.mapa_colores_sectores[sector]
            
            if es_modo_oscuro:
                colores = self.colores_modo_oscuro[idx % len(self.colores_modo_oscuro)]
                bg = colores[1] if es_par else colores[0]
                fg = "#FFFFFF"  # Texto blanco siempre en modo oscuro
            else:
                colores = self.colores_modo_claro[idx % len(self.colores_modo_claro)]
                bg = colores[1] if es_par else colores[0]
                fg = "#1F2937"  # Texto oscuro en modo claro

            return bg, fg

        # Colores por defecto si el sector no tiene color asignado
        if es_modo_oscuro:
            bg = "#2B2B2B" if es_par else "#1E1E1E"
            fg = "#FFFFFF"
        else:
            bg = "#EBEAEA" if es_par else "#FFFFFF"
            fg = "#000000"

        return bg, fg

    # def obtener_color_sector(self, sector: str, es_par: bool = False) -> str:
    #     """Devuelve el color HEX asignado a un sector (o blanco si no tiene)."""
    #     if sector in self.mapa_colores_sectores:
    #         color_impar, color_par = self.mapa_colores_sectores[sector]
    #         # Retorna el color correspondiente según la paridad del índice del sector
    #         return color_par if es_par else color_impar
    #     #
    #     return "#EBEAEA" if es_par else None # Color blanco por defecto si no tiene asignado

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