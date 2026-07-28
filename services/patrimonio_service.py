from data.excel_repository import ExcelRepository
from models.producto import Producto

class PatrimonioService:
    def __init__(self):
        self.repository = ExcelRepository()
        self.inventario_general = self.repository.obtener_inventario()
        self.escaneados_sesion: list[Producto] = []

    def buscar_producto_por_codigo(self, codigo: str) -> Producto | None:
        """Busca en la lista del inventario cargado en memoria."""
        for prod in self.inventario_general:
            if prod.codigo == codigo:
                return prod
        return None

    def registrar_escaneo(self, producto: Producto):
        """Agrega el producto al historial de la sesión."""
        self.escaneados_sesion.append(producto)

    def crear_y_registrar_producto(self, codigo: str, nombre: str, categoria: str) -> Producto:
        """Crea un producto no existente, lo guarda en el Excel maestro y en la sesión."""
        nuevo_prod = Producto(codigo, nombre, categoria)
        
        # 1. Guardar en disco (Excel Maestro)
        self.repository.guardar_nuevo_producto(nuevo_prod)
        
        # 2. Agregar a la memoria local de la app
        self.inventario_general.append(nuevo_prod)
        self.escaneados_sesion.append(nuevo_prod)
        
        return nuevo_prod

    def exportar_planilla_diaria(self, ruta_archivo: str) -> bool:
        if not self.escaneados_sesion:
            return False
        self.repository.exportar_escaneos(self.escaneados_sesion, ruta_archivo)
        return True