from services.patrimonio_service import PatrimonioService

class PatrimonioController:
    def __init__(self):
        self.service = PatrimonioService()

    def procesar_codigo_escaneado(self, codigo: str):
        return self.service.procesar_codigo(codigo)
    
    # def procesar_codigo_escaneado(self, codigo: str):
    #     """Maneja el evento de escaneo."""
    #     producto = self.service.buscar_producto_por_codigo(codigo)
    #     if producto:
    #         self.service.registrar_escaneo(producto)
    #         return {"encontrado": True, "producto": producto}
    #     else:
    #         return {"encontrado": False, "codigo": codigo}

    def agregar_producto_manual(self, datos_producto: dict):
        return self.service.crear_y_registrar_producto(datos_producto)

    def limpiar_sesion_actual(self):
        self.service.limpiar_sesion()

    def generar_planilla_relevo(self, datos_encabezado: dict, ruta_salida: str):
        return self.service.generar_planilla_relevo(datos_encabezado, ruta_salida)

    def eliminar_producto_sesion(self, indice: int)-> bool:
        return self.service.eliminar_producto_por_indice(indice)