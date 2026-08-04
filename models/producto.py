class Producto:
    def __init__(self, nro_inventario: str, nro_nuevo: str, elemento: str, 
                 marca: str, modelo: str, nro_serie: str, oficina: str, dependencia: str, observaciones: str = "", sector: str = "", **kwargs):
        
        self.nro_inventario = str(nro_inventario) if nro_inventario else ""
        self.nro_nuevo = str(nro_nuevo) if nro_nuevo else ""
        self.elemento = str(elemento) if elemento else ""
        self.marca = str(marca) if marca else ""
        self.modelo = str(modelo) if modelo else ""
        self.nro_serie = str(nro_serie) if nro_serie else ""
        self.oficina = str(oficina) if oficina else ""
        self.dependencia = str(dependencia) if dependencia else ""
        self.observaciones = str(observaciones) if observaciones else ""
        self.sector = str(sector) if sector else ""

    def to_dict(self):
        """Retorna solo los 8 campos clave necesarios."""
        return {
            "NRO_INVENTARIO": self.nro_inventario,
            "NRO_NUEVO": self.nro_nuevo,
            "ELEMENTO": self.elemento,
            "MARCA": self.marca,
            "MODELO": self.modelo,
            "NRO_SERIE": self.nro_serie,
            "OFICINA": self.oficina,
            "DEPENDENCIA": self.dependencia,
            "OBSERVACIONES": self.observaciones,
            "SECTOR": self.sector
        }