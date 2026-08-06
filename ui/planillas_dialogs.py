import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
import re
from tkinter.filedialog import asksaveasfilename
from tkinter import filedialog

class PlanillaRelevoDialog(tb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Datos para Planilla de Relevo")
        self.geometry("400x700")
        self.resizable(False, False)
        self.grab_set()

        self.datos = None  # Almacenará el diccionario con la entrada del usuario

        self.setup_ui()

    def setup_ui(self):
        container = tb.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        tb.Label(
            container, 
            text="Complete los datos del Relevamiento:", 
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w", pady=(0, 15))

        frame_fields = tb.Frame(container)
        frame_fields.pack(fill="x", pady=5)

        # 1. Piso
        tb.Label(frame_fields, text="Piso:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_piso = tb.Entry(frame_fields)
        self.entry_piso.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # 2. Oficina
        tb.Label(frame_fields, text="Oficina:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_oficina = tb.Entry(frame_fields)
        self.entry_oficina.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        # 3. Área
        tb.Label(frame_fields, text="Área:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_area = tb.Entry(frame_fields)
        self.entry_area.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        # 4. Dependencia
        tb.Label(frame_fields, text="Dependencia:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_dependencia = tb.Entry(frame_fields)
        self.entry_dependencia.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

        #5. Responsable
        tb.Label(frame_fields, text="Responsable:").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_responsable = tb.Entry(frame_fields)
        self.entry_responsable.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)

        #6. Subresponsable
        tb.Label(frame_fields, text="Subresponsable:").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_subresponsable = tb.Entry(frame_fields)
        self.entry_subresponsable.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=5)

        frame_fields.columnconfigure(1, weight=1)

        # Botones
        frame_btn = tb.Frame(container)
        frame_btn.pack(fill="x", side="bottom", pady=(15, 0))

        btn_generar = tb.Button(
            frame_btn, 
            text="Generar Excel", 
            bootstyle="success", 
            command=self.on_generar
        )
        btn_generar.pack(side="right", padx=5)

        btn_cancelar = tb.Button(
            frame_btn, 
            text="Cancelar", 
            bootstyle="secondary-outline", 
            command=self.destroy
        )
        btn_cancelar.pack(side="right")

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
                "subresponsable": subresponsable
            }
            self.ruta_salida = ruta

        self.destroy()