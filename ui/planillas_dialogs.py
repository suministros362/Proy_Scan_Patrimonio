"""Diálogo para capturar metadatos y destino de la planilla de relevo."""

import ttkbootstrap as tb
from ttkbootstrap.widgets import ScrolledFrame
from datetime import datetime
import re
from tkinter import filedialog

from config import settings


class PlanillaRelevoDialog(tb.Toplevel):
    """Formulario modal de datos de cabecera para el reporte de relevo.

    Args:
        parent: Ventana que abre el diálogo.

    Returns:
        Instancia de `PlanillaRelevoDialog` con el formulario preparado.

    Raises:
        None.
    """

    def __init__(self, parent):
        """Inicializa el formulario y lo centra respecto de su ventana padre.

        Args:
            parent: Ventana que abre el diálogo.

        Returns:
            None.

        Raises:
            None.
        """
        super().__init__(parent)
        self.title("Datos para Planilla de Relevo")

        # Bloquear la ventana padre mientras esta esté abierta
        self.transient(parent)
        self.grab_set()

        self.datos = None  # User-provided report metadata.

        self.setup_ui()
        self.ajustar_y_centrar(parent)

    def ajustar_y_centrar(self, parent):
        """Adapta la geometría del formulario al tamaño de pantalla.

        Args:
            parent: Ventana usada como referencia para centrar el diálogo.

        Returns:
            None.

        Raises:
            None.
        """
        self.update_idletasks()

        width = 480

        # 1. Definimos un alto ideal donde entran todos los campos cómodamente
        alto_ideal = 620

        # 2. Obtenemos el alto de la pantalla del equipo
        screen_height = self.winfo_screenheight()

        # 3. Ponemos un tope de seguridad del 85% de la pantalla para evitar
        # que se salgan los botones
        max_height = int(screen_height * 0.85)

        # 4. Si la pantalla soporta el alto ideal, usa 620px; si es más chica,
        # se limita a max_height
        final_height = min(alto_ideal, max_height)

        # Calcular coordenadas para centrar respecto a la ventana principal
        # (parent)
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w // 2) - (width // 2)
        y = parent_y + (parent_h // 2) - (final_height // 2)

        # Evitar que la ventana quede arriba fuera de pantalla
        x = max(0, x)
        y = max(30, y)

        self.geometry(f"{width}x{final_height}+{x}+{y}")

    def setup_ui(self):
        """Construye las etiquetas, entradas y controles de acción.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        # Contenedor Principal
        main_container = tb.Frame(self, padding=15)
        main_container.pack(fill="both", expand=True)

        # 1. Cabecera (Fija arriba)
        header_frame = tb.Frame(main_container)
        header_frame.pack(fill="x", side="top", pady=(0, 10))

        tb.Label(
            header_frame,
            text="Planilla de Relevamiento",
            font=("Helvetica", 11, "bold"),
            bootstyle="primary"
        ).pack(anchor="w")

        tb.Label(
            header_frame,
            text="Complete los datos del área para generar el documento:",
            font=("Helvetica", 8),
            bootstyle="secondary"
        ).pack(anchor="w")

        # 2. Botones y Barra de Estado (Fijos abajo)
        footer_frame = tb.Frame(main_container)
        footer_frame.pack(fill="x", side="bottom", pady=(10, 0))

        self.lbl_estado = tb.Label(
            footer_frame, text="", font=(
                "Helvetica", 8))
        self.lbl_estado.pack(anchor="w", pady=(0, 5))

        frame_btn = tb.Frame(footer_frame)
        frame_btn.pack(fill="x")

        self.btn_generar = tb.Button(
            frame_btn,
            text="Generar Excel",
            bootstyle="success",
            command=self.on_generar
        )
        self.btn_generar.pack(side="right", padx=(5, 0))

        self.btn_cancelar = tb.Button(
            frame_btn,
            text="Cancelar",
            bootstyle="secondary-outline",
            command=self.destroy
        )
        self.btn_cancelar.pack(side="right")

        # 3. Formulario con Scroll (ocupa todo el espacio central)
        scroll_container = ScrolledFrame(main_container, autohide=True)
        scroll_container.pack(fill="both", expand=True, pady=5)

        grid_frame = tb.Frame(scroll_container)
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)

        pady_val = 4

        # Formulario de campos
        tb.Label(
            grid_frame,
            text="Piso:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_piso = tb.Entry(grid_frame)
        self.entry_piso.grid(
            row=0, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        tb.Label(
            grid_frame,
            text="Oficina:").grid(
            row=1,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_oficina = tb.Entry(grid_frame)
        self.entry_oficina.grid(
            row=1, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        tb.Label(
            grid_frame,
            text="Área:").grid(
            row=2,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_area = tb.Entry(grid_frame)
        self.entry_area.grid(
            row=2, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        tb.Label(
            grid_frame,
            text="Dependencia:").grid(
            row=3,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_dependencia = tb.Entry(grid_frame)
        self.entry_dependencia.grid(
            row=3, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        tb.Label(
            grid_frame,
            text="Responsable:").grid(
            row=4,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_responsable = tb.Entry(grid_frame)
        self.entry_responsable.grid(
            row=4, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        tb.Label(
            grid_frame,
            text="Subresponsable:").grid(
            row=5,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_subresponsable = tb.Entry(grid_frame)
        self.entry_subresponsable.grid(
            row=5, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        tb.Label(
            grid_frame,
            text="Teléfono:").grid(
            row=6,
            column=0,
            sticky="w",
            pady=pady_val)
        self.entry_telefono = tb.Entry(grid_frame)
        self.entry_telefono.grid(
            row=6, column=1, sticky="ew", padx=(
                10, 0), pady=pady_val)

        grid_frame.columnconfigure(1, weight=1)

    def _generar_nombre_predeterminado(
            self,
            piso: str,
            oficina: str,
            area: str) -> str:
        """Compone un nombre seguro para el archivo de salida.

        Args:
            piso: Texto del piso o nivel del edificio.
            oficina: Nombre de la oficina.
            area: Nombre del área relevada.

        Returns:
            Nombre de archivo con componentes sanitizados, fecha y extensión.

        Raises:
            None.
        """
        piso_str = piso or "Piso"
        oficina_str = oficina or "Oficina"
        area_str = area or "Area"
        fecha_str = datetime.now().strftime("%d-%m-%Y")

        # Remove characters forbidden by common filesystems before suggesting a
        # name.
        piso_clean = re.sub(r'[\\/*?:"<>|]', '', piso_str).replace(' ', '_')
        oficina_clean = re.sub(
            r'[\\/*?:"<>|]',
            '',
            oficina_str).replace(
            ' ',
            '_')
        area_clean = re.sub(r'[\\/*?:"<>|]', '', area_str).replace(' ', '_')

        return (
            f"{piso_clean}_{oficina_clean}_{area_clean}_{fecha_str}"
            f"{settings.RELEVO_REPORT_EXTENSION}"
        )

    def on_generar(self):
        """Recoge los metadatos, solicita destino y cierra el formulario.

        Args:
            None.

        Returns:
            None.

        Raises:
            None: El diálogo del sistema gestiona la cancelación del destino.
        """
        piso = self.entry_piso.get().strip()
        oficina = self.entry_oficina.get().strip()
        area = self.entry_area.get().strip()
        dependencia = self.entry_dependencia.get().strip()
        responsable = self.entry_responsable.get().strip()
        subresponsable = self.entry_subresponsable.get().strip()
        telefono = self.entry_telefono.get().strip()
        # Generar nombre de archivo predeterminado
        nombre_sugerido = self._generar_nombre_predeterminado(
            piso, oficina, area)

        ruta = filedialog.asksaveasfilename(
            title="Guardar Planilla de Relevamiento",
            initialfile=nombre_sugerido,
            initialdir=str(settings.ensure_output_directory()),
            defaultextension=settings.RELEVO_REPORT_EXTENSION,
            filetypes=[
                ("Archivos de Excel", f"*{settings.RELEVO_REPORT_EXTENSION}"),
                ("Todos los archivos", "*.*"),
            ],
            parent=self
        )

        if ruta:
            # Publish data only after the user has selected an output path.
            self.datos = {
                "piso": piso,
                "oficina": oficina,
                "area": area,
                "dependencia": dependencia,
                "responsable": responsable,
                "subresponsable": subresponsable,
                "telefono": telefono
            }
            self.ruta_salida = ruta

        self.destroy()
