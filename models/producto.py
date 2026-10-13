"""Entidad de dominio que representa un bien patrimonial."""


class Producto:
    """Almacena los identificadores y atributos de un bien patrimonial.

    Args:
        nro_inventario: Código patrimonial del inventario.
        nro_nuevo: Código nuevo o alternativo del bien.
        elemento: Descripción del bien.
        marca: Marca del bien.
        modelo: Modelo del bien.
        nro_serie: Número de serie.
        oficina: Oficina donde se encuentra el bien.
        dependencia: Dependencia responsable.
        observaciones: Texto libre asociado al bien.
        sector: Sector de la sesión actual.
        **kwargs: Argumentos adicionales ignorados por compatibilidad.

    Returns:
        Instancia de `Producto` con valores normalizados a texto.

    Raises:
        None.
    """

    def __init__(
            self,
            nro_inventario: str,
            nro_nuevo: str,
            elemento: str,
            marca: str,
            modelo: str,
            nro_serie: str,
            oficina: str,
            dependencia: str,
            observaciones: str = "",
            sector: str = "",
            **kwargs):
        """Inicializa un producto normalizando los valores a texto.

        Args:
            nro_inventario: Código patrimonial del inventario.
            nro_nuevo: Código nuevo o alternativo del bien.
            elemento: Descripción del bien.
            marca: Marca del bien.
            modelo: Modelo del bien.
            nro_serie: Número de serie.
            oficina: Oficina donde se encuentra el bien.
            dependencia: Dependencia responsable.
            observaciones: Texto libre asociado al bien.
            sector: Sector de la sesión actual.
            **kwargs: Argumentos adicionales ignorados por compatibilidad.

        Returns:
            None.

        Raises:
            None.
        """
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
        """Convierte el producto a los encabezados usados en Excel.

        Args:
            None.

        Returns:
            Diccionario con los campos del producto y sus nombres de columna.

        Raises:
            None.
        """
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
