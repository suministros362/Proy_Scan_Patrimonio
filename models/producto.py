class Producto:
    def __init__(self, codigo: str, nombre: str, categoria: str):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria

    def to_dict(self):
        """Útil para exportar a DataFrames o JSON fácilmente."""
        return {
            "Codigo_Patrimonial": self.codigo,
            "Nombre_Articulo": self.nombre,
            "Categoria": self.categoria
        }