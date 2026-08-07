import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ScrolledFrame


class AgregarProductoDialog(tb.Toplevel):
    def __init__(self, parent, codigo_escaneado, controller):
        super().__init__(parent)
        self.controller = controller
        self.codigo_escaneado = codigo_escaneado
        self.producto_creado = None

        self.title("Agregar Producto Manual")
        
        # Bloquear la ventana padre mientras esta esté abierta
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.ajustar_y_centrar(parent)

    def ajustar_y_centrar(self, parent):
        """Define un alto cómodo para ver todos los campos y se adapta si la pantalla es pequeña."""
        self.update_idletasks()
        
        width = 500
        
        # 1. Definimos un alto ideal donde entran todos los campos cómodamente
        alto_ideal = 720
        
        # 2. Obtenemos el alto de la pantalla del equipo
        screen_height = self.winfo_screenheight()
        
        # 3. Ponemos un tope de seguridad del 85% de la pantalla para evitar que se salgan los botones
        max_height = int(screen_height * 0.85)
        
        # 4. Si la pantalla soporta el alto ideal, usa 720px; si es más chica, se limita a max_height
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
            text="Producto no encontrado", 
            font=("Helvetica", 11, "bold"), 
            bootstyle="warning"
        ).pack(anchor="w")

        tb.Label(
            header_frame, 
            text="Complete los datos para incluirlo en la sesión actual:", 
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

        self.btn_guardar = tb.Button(
            frame_btn, 
            text="Agregar a la Sesión", 
            bootstyle="success", 
            command=self.on_guardar
        )
        self.btn_guardar.pack(side="right", padx=(5, 0))

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

        pady_val = 3

        # Formulario de campos
        tb.Label(grid_frame, text="N° Inventario:").grid(row=0, column=0, sticky="w", pady=pady_val)
        self.entry_inv = tb.Entry(grid_frame)
        self.entry_inv.insert(0, self.codigo_escaneado)
        self.entry_inv.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="N° Nuevo:").grid(row=1, column=0, sticky="w", pady=pady_val)
        self.entry_nuevo = tb.Entry(grid_frame)
        self.entry_nuevo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Elemento / Detalle (*):").grid(row=2, column=0, sticky="w", pady=pady_val)
        self.entry_elemento = tb.Entry(grid_frame)
        self.entry_elemento.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Marca:").grid(row=3, column=0, sticky="w", pady=pady_val)
        self.entry_marca = tb.Entry(grid_frame)
        self.entry_marca.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Modelo:").grid(row=4, column=0, sticky="w", pady=pady_val)
        self.entry_modelo = tb.Entry(grid_frame)
        self.entry_modelo.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="N° Serie:").grid(row=5, column=0, sticky="w", pady=pady_val)
        self.entry_serie = tb.Entry(grid_frame)
        self.entry_serie.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Oficina:").grid(row=6, column=0, sticky="w", pady=pady_val)
        self.entry_oficina = tb.Entry(grid_frame)
        self.entry_oficina.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Dependencia:").grid(row=7, column=0, sticky="w", pady=pady_val)
        self.entry_dependencia = tb.Entry(grid_frame)
        self.entry_dependencia.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Observaciones:").grid(row=8, column=0, sticky="w", pady=pady_val)
        self.entry_obs = tb.Entry(grid_frame)
        self.entry_obs.grid(row=8, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        tb.Label(grid_frame, text="Sector:").grid(row=9, column=0, sticky="w", pady=pady_val)
        self.entry_sector = tb.Entry(grid_frame)
        self.entry_sector.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=pady_val)

        grid_frame.columnconfigure(1, weight=1)

    def on_guardar(self):
        elemento = self.entry_elemento.get().strip()

        if not elemento:
            tb.dialogs.Messagebox.show_warning(
                "El campo 'Elemento' es obligatorio.", 
                title="Campo Requerido", 
                parent=self
            )
            return
        
        
        # Deshabilitar controles mientras se procesa
        self.btn_guardar.configure(state="disabled")
        self.btn_cancelar.configure(state="disabled")
        self.lbl_estado.configure(text="Agregando producto a la sesión...", bootstyle="info")

        # Preparar datos
        datos = {
            "nro_inventario": self.entry_inv.get().strip(),
            "nro_nuevo": self.entry_nuevo.get().strip(),
            "elemento": elemento,
            "marca": self.entry_marca.get().strip(),
            "modelo": self.entry_modelo.get().strip(),
            "nro_serie": self.entry_serie.get().strip(),
            "oficina": self.entry_oficina.get().strip(),
            "dependencia": self.entry_dependencia.get().strip(),
            "observaciones": self.entry_obs.get().strip(),
            "sector": self.entry_sector.get().strip()
        }

        # Ejecutar agregación en segundo plano
        hilo = threading.Thread(target=self._guardar_en_segundo_plano, args=(datos,), daemon=True)
        hilo.start()
        


    def _guardar_en_segundo_plano(self, datos):
        try:
            # Llama al controlador pasándole el diccionario entero
            producto = self.controller.agregar_producto_manual(datos)
            
            # Notificar éxito a la UI principal en el hilo adecuado
            self.after(0, lambda: self._finalizar_guardado(producto))
        except Exception as e:
            self.after(0, lambda: self._mostrar_error(str(e)))

    def _finalizar_guardado(self, producto):
        self.producto_creado = producto
        self.destroy()
    

    def _mostrar_error(self, mensaje_error):
        self.btn_guardar.configure(state="normal")
        self.btn_cancelar.configure(state="normal")
        self.lbl_estado.configure(text="", bootstyle="default")
        
        tb.dialogs.Messagebox.show_error(
            f"Error al agregar el producto:\n{mensaje_error}", 
            title="Error", 
            parent=self
        )