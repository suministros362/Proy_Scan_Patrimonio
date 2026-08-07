import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ScrolledFrame
from datetime import datetime
import re
from tkinter.filedialog import asksaveasfilename
from tkinter import filedialog

class PlanillaRelevoDialog(tb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Datos para Planilla de Relevo")
        
        # Bloquear la ventana padre mientras esta esté abierta
        self.transient(parent)
        self.grab_set()

        self.datos = None  # Almacenará el diccionario con la entrada del usuario

        self.setup_ui()
        self.ajustar_y_centrar(parent)

    def ajustar_y_centrar(self, parent):
        """Define un alto cómodo para ver todos los campos y se adapta si la pantalla es pequeña."""
        self.update_idletasks()
        
        width = 480
        
        # 1. Definimos un alto ideal donde entran todos los campos cómodamente
        alto_ideal = 620
        
        # 2. Obtenemos el alto de la pantalla del equipo
        screen_height = self.winfo_screenheight()
        
        # 3. Ponemos un tope de seguridad del 85% de la pantalla para evitar que se salgan los botones
        max_height = int(screen_height * 0.85)
        
        # 4. Si la pantalla soporta el alto ideal, usa 620px; si es más chica, se limita a max_height
        final_height = min(alto_ideal, max_height)

        # Calcular coordenadas para centrar respecto a la ventana principal (parent)
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

        self.lbl_estado = tb.Label(footer_frame, text="", font=("Helvetica", 8))
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
        tb.Label(grid_frame, text="Piso:").grid(row=0, column=0, sticky="w", pady=pady_val)
        self.entry_piso = tb.Entry(grid_frame)
        self.entry_piso.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Oficina:").grid(row=1, column=0, sticky="w", pady=pady_val)
        self.entry_oficina = tb.Entry(grid_frame)
        self.entry_oficina.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Área:").grid(row=2, column=0, sticky="w", pady=pady_val)
        self.entry_area = tb.Entry(grid_frame)
        self.entry_area.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Dependencia:").grid(row=3, column=0, sticky="w", pady=pady_val)
        self.entry_dependencia = tb.Entry(grid_frame)
        self.entry_dependencia.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Responsable:").grid(row=4, column=0, sticky="w", pady=pady_val)
        self.entry_responsable = tb.Entry(grid_frame)
        self.entry_responsable.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Subresponsable:").grid(row=5, column=0, sticky="w", pady=pady_val)
        self.entry_subresponsable = tb.Entry(grid_frame)
        self.entry_subresponsable.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Teléfono:").grid(row=6, column=0, sticky="w", pady=pady_val)
        self.entry_telefono = tb.Entry(grid_frame)
        self.entry_telefono.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        grid_frame.columnconfigure(1, weight=1)

# class PlanillaRelevoDialog(tb.Toplevel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("Datos para Planilla de Relevo")
#         self.geometry("400x600")
#         self.resizable(False, False)
#         self.grab_set()

#         self.datos = None  # Almacenará el diccionario con la entrada del usuario

#         self.setup_ui()

#     def setup_ui(self):
#         container = tb.Frame(self, padding=20)
#         container.pack(fill="both", expand=True)

#         tb.Label(
#             container, 
#             text="Complete los datos del Relevamiento:", 
#             font=("Helvetica", 10, "bold")
#         ).pack(anchor="w", pady=(0, 15))

#         frame_fields = tb.Frame(container)
#         frame_fields.pack(fill="x", pady=5)

#         # 1. Piso
#         tb.Label(frame_fields, text="Piso:").grid(row=0, column=0, sticky="w", pady=5)
#         self.entry_piso = tb.Entry(frame_fields)
#         self.entry_piso.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

#         # 2. Oficina
#         tb.Label(frame_fields, text="Oficina:").grid(row=1, column=0, sticky="w", pady=5)
#         self.entry_oficina = tb.Entry(frame_fields)
#         self.entry_oficina.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

#         # 3. Área
#         tb.Label(frame_fields, text="Área:").grid(row=2, column=0, sticky="w", pady=5)
#         self.entry_area = tb.Entry(frame_fields)
#         self.entry_area.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

#         # 4. Dependencia
#         tb.Label(frame_fields, text="Dependencia:").grid(row=3, column=0, sticky="w", pady=5)
#         self.entry_dependencia = tb.Entry(frame_fields)
#         self.entry_dependencia.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

#         #5. Responsable
#         tb.Label(frame_fields, text="Responsable:").grid(row=4, column=0, sticky="w", pady=5)
#         self.entry_responsable = tb.Entry(frame_fields)
#         self.entry_responsable.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)

#         #6. Subresponsable
#         tb.Label(frame_fields, text="Subresponsable:").grid(row=5, column=0, sticky="w", pady=5)
#         self.entry_subresponsable = tb.Entry(frame_fields)
#         self.entry_subresponsable.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=5)

#         #7. Telefono
#         tb.Label(frame_fields, text="Teléfono:").grid(row=6, column=0, sticky="w", pady=5)
#         self.entry_telefono = tb.Entry(frame_fields)
#         self.entry_telefono.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=5)

#         frame_fields.columnconfigure(1, weight=1)

#         # Botones
#         frame_btn = tb.Frame(container)
#         frame_btn.pack(fill="x", side="bottom", pady=(15, 0))

#         btn_generar = tb.Button(
#             frame_btn, 
#             text="Generar Excel", 
#             bootstyle="success", 
#             command=self.on_generar
#         )
#         btn_generar.pack(side="right", padx=5)

#         btn_cancelar = tb.Button(
#             frame_btn, 
#             text="Cancelar", 
#             bootstyle="secondary-outline", 
#             command=self.destroy
#         )
#         btn_cancelar.pack(side="right")

    def _generar_nombre_predeterminado(self, piso: str, oficina: str, area: str) -> str:
        """Arma y limpia el nombre: Piso_Oficina_Area_DD-MM-YYYY.xlsx"""
        piso_str = piso or "Piso"
        oficina_str = oficina or "Oficina"
        area_str = area or "Area"
        fecha_str = datetime.now().strftime("%d-%m-%Y")

        # Limpiar caracteres no permitidos en archivos (\ / : * ? " < > |) y reemplazar espacios por guion bajo
        piso_clean = re.sub(r'[\\/*?:"<>|]', '', piso_str).replace(' ', '_')
        oficina_clean = re.sub(r'[\\/*?:"<>|]', '', oficina_str).replace(' ', '_')
        area_clean = re.sub(r'[\\/*?:"<>|]', '', area_str).replace(' ', '_')

        return f"{piso_clean}_{oficina_clean}_{area_clean}_{fecha_str}.xlsx"

    def on_generar(self):
        piso = self.entry_piso.get().strip()
        oficina = self.entry_oficina.get().strip()
        area = self.entry_area.get().strip()
        dependencia = self.entry_dependencia.get().strip()
        responsable = self.entry_responsable.get().strip()
        subresponsable = self.entry_subresponsable.get().strip()
        telefono = self.entry_telefono.get().strip()
        # Generar nombre de archivo predeterminado
        nombre_sugerido = self._generar_nombre_predeterminado(piso, oficina, area)

        ruta = filedialog.asksaveasfilename(
            title="Guardar Planilla de Relevamiento",
            initialfile=nombre_sugerido,  # 👈 Muestra el nombre automático
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            parent=self
        )

        if ruta:
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