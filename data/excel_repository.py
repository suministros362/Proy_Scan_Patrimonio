import pandas as pd
import os
from models.producto import Producto

class ExcelRepository:
    def __init__(self, file_path="inventario.xlsx"):
        self.file_path = file_path

    def obtener_inventario(self) -> list[Producto]:
        """Lee el Excel y retorna una lista de objetos Producto."""
        if not os.path.exists(self.file_path):
            # Crear un Excel inicial de prueba si no existe
            df_inicial = pd.DataFrame([
                {"Codigo_Patrimonial": "PAT-001234", "Nombre_Articulo": "Escritorio Madera", "Categoria": "Mobiliario"},
                {"Codigo_Patrimonial": "PAT-001235", "Nombre_Articulo": "Silla Giratoria", "Categoria": "Mobiliario"}
            ])
            df_inicial.to_excel(self.file_path, index=False)

        df = pd.read_excel(self.file_path, dtype={"Codigo_Patrimonial": str})
        
        productos = []
        for _, row in df.iterrows():
            productos.append(
                Producto(
                    codigo=str(row["Codigo_Patrimonial"]),
                    nombre=str(row["Nombre_Articulo"]),
                    categoria=str(row["Categoria"])
                )
            )
        return productos

    def guardar_nuevo_producto(self, producto: Producto):
        """Agrega un producto nuevo al Excel general de inventario."""
        df = pd.read_excel(self.file_path, dtype={"Codigo_Patrimonial": str})
        nuevo_df = pd.DataFrame([producto.to_dict()])
        df_actualizado = pd.concat([df, nuevo_df], ignore_index=False)
        df_actualizado.to_excel(self.file_path, index=False)

    def exportar_escaneos(self, lista_productos: list[Producto], ruta_salida: str):
        """Exporta la planilla de la sesión escaneada."""
        data = [p.to_dict() for p in lista_productos]
        df = pd.DataFrame(data)
        df.to_excel(ruta_salida, index=False)