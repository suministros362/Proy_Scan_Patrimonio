import ttkbootstrap as tb
from tkinter import messagebox
from ui.dialogs import AgregarProductoDialog

class MainWindow(tb.Window):
    def __init__(self, controller):
        #Definimos los dos temas a alternar
        self.tema_claro = "flatly"    # Tema claro moderno
        self.tema_oscuro = "vapor-dark"   # Tema oscuro moderno
        super().__init__(
            title="Control Patrimonial",
            themename=self.tema_claro,
            size=(750, 750)
        )
        self.controller = controller # Inyectamos el controlador
        self.setup_ui()

    def setup_ui(self):
        # --- CABECERA Y CAMBIO DE TEMA ---
        frame_top = tb.Frame(self, padding=(20, 10))
        frame_top.pack(fill="x")

        # Interruptor (Switch) para alternar tema
        # Al hacer clic, ejecuta el método self.alternar_tema
        self.switch_tema = tb.Checkbutton(
            frame_top, 
            text="Modo Oscuro", 
            bootstyle="round-toggle", 
            command=self.alternar_tema,
            width=12
        )
        self.switch_tema.pack(side="right")
        # --- FRAME ESCANEO ---
        frame_scan = tb.LabelFrame(self, text=" Escaneo ", padding=15, bootstyle="primary")
        frame_scan.pack(fill="x", padx=20, pady=10)

        self.entry_codigo = tb.Entry(frame_scan, font=("Helvetica", 11), width=25)
        self.entry_codigo.pack(side="left", padx=10)
        self.entry_codigo.focus()
        self.entry_codigo.bind("<Return>", self.on_escanear)

        btn_scan = tb.Button(frame_scan, text="Procesar", command=self.on_escanear, bootstyle="primary")
        btn_scan.pack(side="left", padx=5)

        # --- TABLA DE ESCANEADOS ---
        frame_tabla = tb.LabelFrame(self, text=" Escaneados en la Sesión ", padding=15, bootstyle="info")
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        self.tabla = tb.Treeview(frame_tabla, columns=("codigo", "nombre", "categoria"), show="headings", bootstyle="info")
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Artículo")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.pack(fill="both", expand=True)

        # --- BOTÓN EXPORTAR ---
        btn_exportar = tb.Button(self, text="Generar Excel", command=self.on_exportar, bootstyle="success")
        btn_exportar.pack(side="right", padx=20, pady=10)

    def alternar_tema(self):
        """Método que cambia el tema de la ventana en tiempo real."""
        # Verificamos si el switch está activado
        if "selected" in self.switch_tema.state():
            # Cambiar a Modo Oscuro
            self.style.theme_use(self.tema_oscuro)
            toggle_text = "Modo Claro"
            self.switch_tema.config(text=toggle_text)
        else:
            # Cambiar a Modo Claro
            self.style.theme_use(self.tema_claro)
            toggle_text = "Modo Oscuro"
            self.switch_tema.config(text=toggle_text)
        self.entry_codigo.focus()

    def on_escanear(self, event=None):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            return

        self.entry_codigo.delete(0, 'end')

        # Se solicita la acción al controlador
        resultado = self.controller.procesar_codigo_escaneado(codigo)

        if resultado["encontrado"]:
            prod = resultado["producto"]
            self.tabla.insert("", "end", values=(prod.codigo, prod.nombre, prod.categoria))
        else:
            messagebox.showwarning("No Encontrado", f"El código {codigo} no existe. Procede al alta manual.")
            # 🚀 Abrir la ventana emergente pasándole el código que no existía
            dialogo = AgregarProductoDialog(self, codigo, self.controller)
            self.wait_window(dialogo) # Espera a que el usuario cierre la ventana emergente

            # Si el usuario guardó el producto, actualizamos la tabla principal
            if dialogo.producto_creado:
                prod = dialogo.producto_creado
                self.tabla.insert("", "end", values=(prod.codigo, prod.nombre, prod.categoria))

    def on_exportar(self):
        exito = self.controller.exportar_planilla("Reporte_Patrimonio.xlsx")
        if exito:
            messagebox.showinfo("Éxito", "Planilla exportada con éxito.")
        else:
            messagebox.showwarning("Atención", "No hay items para exportar.")