"""Estilos de presentación para filas agrupadas por sector y tema."""


class SectorRowPresenter:
    """Asigna colores estables a sectores y produce tags de fila Treeview.

    Args:
        None.

    Returns:
        Instancia con un mapa de colores inicialmente vacío.

    Raises:
        None.
    """

    LIGHT_PALETTE = (
        ("#E6F3FF", "#D0E7FF"),
        ("#E6FFE6", "#D1FFD1"),
        ("#FFF0F5", "#FFE0EB"),
        ("#FFF2CC", "#FFE599"),
        ("#E8DAEF", "#D7BDE2"),
        ("#E0F7FA", "#B2EBF2"),
        ("#FFE0B2", "#FFCC80"),
    )
    DARK_PALETTE = (
        ("#1A365D", "#2A4365"),
        ("#1C4532", "#22543D"),
        ("#4A154B", "#611F69"),
        ("#5B3A00", "#744A00"),
        ("#4C1D95", "#5B21B6"),
        ("#083344", "#164E63"),
        ("#6C2BD9", "#7C3AED"),
    )
    DARK_THEMES = {"one-dark", "superhero", "cyborg", "solar", "vapor"}

    def __init__(self):
        """Inicializa el mapa de sectores para esta vista.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self._sector_indices = {}

    def clear(self):
        """Reinicia la asignación de colores para una nueva sesión visual.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self._sector_indices.clear()

    def es_modo_oscuro(self, theme_name: str) -> bool:
        """Indica si el nombre del tema corresponde a una paleta oscura.

        Args:
            theme_name: Nombre del tema activo de ttkbootstrap.

        Returns:
            `True` para temas oscuros; de lo contrario, `False`.

        Raises:
            AttributeError: Si `theme_name` no proporciona `lower()`.
        """
        theme_name = theme_name.lower()
        return "dark" in theme_name or theme_name in self.DARK_THEMES

    def estilo_fila(self, sector: str, es_par: bool,
                    es_modo_oscuro: bool) -> tuple[str, str, str]:
        """Obtiene el tag, fondo y texto apropiados para una fila.

        Args:
            sector: Nombre del sector que agrupa el producto.
            es_par: Indica si la fila tiene índice par para alternar tonos.
            es_modo_oscuro: Selecciona la paleta correspondiente al tema.

        Returns:
            Tupla `(tag, color_fondo, color_texto)` para configurar Treeview.

        Raises:
            None.
        """
        # Keep the sector-to-palette mapping stable across refreshes and theme
        # changes.
        sector_index = self._sector_indices.setdefault(
            sector,
            len(self._sector_indices) % len(self.LIGHT_PALETTE),
        )
        palette = self.DARK_PALETTE if es_modo_oscuro else self.LIGHT_PALETTE
        background = palette[sector_index][1 if es_par else 0]
        foreground = "#FFFFFF" if es_modo_oscuro else "#1F2937"
        mode = "dark" if es_modo_oscuro else "light"
        parity = "par" if es_par else "impar"
        tag = f"tag_{sector_index}_{parity}_{mode}"
        return tag, background, foreground
