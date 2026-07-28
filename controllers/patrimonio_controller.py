from services.patrimonio_service import PatrimonioService

class PatrimonioController:
    def __init__(self):
        self.service = PatrimonioService()

    def procesar_codigo_escaneado(self, codigo: str):
        """Maneja el evento de escaneo."""
        producto = self.service.buscar_producto_por_codigo(codigo)
        if producto:
            self.service.registrar_escaneo(producto)
            return {"encontrado": True, "producto": producto}
        else:
            return {"encontrado": False, "codigo": codigo}

    def agregar_producto_manual(self, codigo: str, nombre: str, categoria: str):
        return self.service.crear_y_registrar_producto(codigo, nombre, categoria)

    def exportar_planilla(self, ruta: str) -> bool:
        return self.service.exportar_planilla_diaria(ruta)