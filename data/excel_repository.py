import pandas as pd
import os
from models.producto import Producto
from tkinter import messagebox

class ExcelRepository:
    def __init__(self, file_path=os.path.join("archivos", "inventario.xlsx")):
        self.file_path = file_path

    def obtener_inventario(self) -> list[Producto]:
        """Lee el Excel y convierte cada fila en un objeto Producto con los 8 campos clave."""
        if not os.path.exists(self.file_path):
            print(f"Advertencia: No se encontró el archivo {self.file_path}")
            return []

        # Cargar el Excel leyendo todos los campos como string para evitar perder ceros a la izquierda
        df = pd.read_excel(self.file_path, dtype=str)
        
        # Limpiar espacios en blanco en los nombres de las columnas
        df.columns = df.columns.str.strip()

        productos = []
        for _, row in df.iterrows():
            # Manejar valores vacíos (NaN) convirtiéndolos en cadenas vacías ""
            producto = Producto(
                nro_inventario="" if pd.isna(row.get("NRO_INVENTARIO")) else str(row.get("NRO_INVENTARIO")).strip(),
                nro_nuevo="" if pd.isna(row.get("NRO_NUEVO")) else str(row.get("NRO_NUEVO")).strip(),
                elemento="" if pd.isna(row.get("ELEMENTO")) else str(row.get("ELEMENTO")).strip(),
                marca="" if pd.isna(row.get("MARCA")) else str(row.get("MARCA")).strip(),
                modelo="" if pd.isna(row.get("MODELO")) else str(row.get("MODELO")).strip(),
                nro_serie="" if pd.isna(row.get("NRO_SERIE")) else str(row.get("NRO_SERIE")).strip(),
                oficina="" if pd.isna(row.get("OFICINA")) else str(row.get("OFICINA")).strip(),
                dependencia="" if pd.isna(row.get("DEPENDENCIA")) else str(row.get("DEPENDENCIA")).strip()
            )
            productos.append(producto)
            
        return productos

    def guardar_nuevo_producto(self, producto: Producto) -> bool:
        """Agrega el producto creado manualmente al Excel maestro."""
        try:
            if os.path.exists(self.file_path):
                df = pd.read_excel(self.file_path, dtype=str)
            else:
                df = pd.DataFrame()

            nuevo_df = pd.DataFrame([producto.to_dict()])
            df_actualizado = pd.concat([df, nuevo_df], ignore_index=True)
            
            # Intenta guardar el archivo en disco
            df_actualizado.to_excel(self.file_path, index=False)
            return True

        except PermissionError:
            # Capturamos el error si el Excel está abierto
            messagebox.showerror(
                "Archivo Bloqueado",
                f"No se pudo guardar el registro porque el archivo '{self.file_path}' está abierto.\n\n"
                "Por favor, CIERRA EL EXCEL y vuelve a intentar."
            )
            return False
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error al guardar: {str(e)}")
            return False

    def exportar_escaneos(self, lista_productos: list[Producto], ruta_salida: str):
        """Exporta los productos escaneados en la sesión a un nuevo archivo Excel."""
        data = [p.to_dict() for p in lista_productos]
        df = pd.DataFrame(data)
        df.to_excel(ruta_salida, index=False)

#-------------------------------------------------------------------------------------------------------------------------
#-----------Primer modelo de repositorio para manejar el Excel de inventario general y la planilla de escaneos diarios.---
#-------------------------------------------------------------------------------------------------------------------------
# import pandas as pd
# import os
# from models.producto import Producto

# class ExcelRepository:
#     def __init__(self, file_path="inventario.xlsx"):
#         self.file_path = file_path

#     def obtener_inventario(self) -> list[Producto]:
#         """Lee el Excel y retorna una lista de objetos Producto."""
#         if not os.path.exists(self.file_path):
#             # Crear un Excel inicial de prueba si no existe
#             df_inicial = pd.DataFrame([
#                 {"Codigo_Patrimonial": "PAT-001234", "Nombre_Articulo": "Escritorio Madera", "Categoria": "Mobiliario"},
#                 {"Codigo_Patrimonial": "PAT-001235", "Nombre_Articulo": "Silla Giratoria", "Categoria": "Mobiliario"}
#             ])
#             df_inicial.to_excel(self.file_path, index=False)

#         df = pd.read_excel(self.file_path, dtype={"Codigo_Patrimonial": str})
        
#         productos = []
#         for _, row in df.iterrows():
#             productos.append(
#                 Producto(
#                     codigo=str(row["Codigo_Patrimonial"]),
#                     nombre=str(row["Nombre_Articulo"]),
#                     categoria=str(row["Categoria"])
#                 )
#             )
#         return productos

#     def guardar_nuevo_producto(self, producto: Producto):
#         """Agrega un producto nuevo al Excel general de inventario."""
#         df = pd.read_excel(self.file_path, dtype={"Codigo_Patrimonial": str})
#         nuevo_df = pd.DataFrame([producto.to_dict()])
#         df_actualizado = pd.concat([df, nuevo_df], ignore_index=False)
#         df_actualizado.to_excel(self.file_path, index=False)

#     def exportar_escaneos(self, lista_productos: list[Producto], ruta_salida: str):
#         """Exporta la planilla de la sesión escaneada."""
#         data = [p.to_dict() for p in lista_productos]
#         df = pd.DataFrame(data)
#         df.to_excel(ruta_salida, index=False)