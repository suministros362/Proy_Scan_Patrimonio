import ttkbootstrap as tb
from ttkbootstrap.constants import *

class AgregarProductoDialog(tb.Toplevel):
    def __init__(self, parent, codigo_escaneado, controller):
        super().__init__(parent)
        
        self.controller = controller
        self.codigo_escaneado = codigo_escaneado
        self.producto_creado = None  # Guardará el producto resultante si se confirma
        
        # Configuración de la ventana emergente
        self.title("Agregar Artículo Nuevo")
        self.geometry("450x450")
        self.resizable(False, False)
        
        # Bloquea la interacción con la ventana principal mientras esta esté abierta
        self.grab_set()

        # Dibujamos los componentes visuales de este diálogo
        self.setup_ui()

    def setup_ui(self):
        # Frame contenedor con padding
        frame = tb.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # 1. Muestra el Código Escaneado (Solo lectura)
        lbl_codigo = tb.Label(
            frame, 
            text=f"Código Patrimonial: {self.codigo_escaneado}", 
            font=("Helvetica", 11, "bold"),
            bootstyle="primary"
        )
        lbl_codigo.pack(anchor="w", pady=(0, 15))

        # 2. Campo: Nombre / Descripción
        tb.Label(frame, text="Descripción del Artículo:").pack(anchor="w")
        self.entry_nombre = tb.Entry(frame)
        self.entry_nombre.pack(fill="x", pady=(0, 10))
        self.entry_nombre.focus() # Pone el foco directamente aquí

        # 3. Campo: Categoría (Desplegable)
        tb.Label(frame, text="Categoría:").pack(anchor="w")
        self.combo_categoria = tb.Combobox(
            frame, 
            values=["Mobiliario", "Informática", "Electrónica", "Otros"],
            state="readonly"
        )
        self.combo_categoria.set("Mobiliario")
        self.combo_categoria.pack(fill="x", pady=(0, 20))

        # 4. Botones de Acción
        frame_botones = tb.Frame(frame)
        frame_botones.pack(fill="x", side="bottom")

        btn_guardar = tb.Button(
            frame_botones, 
            text="Guardar", 
            bootstyle="success", 
            command=self.on_guardar
        )
        btn_guardar.pack(side="right", padx=5)

        btn_cancelar = tb.Button(
            frame_botones, 
            text="Cancelar", 
            bootstyle="secondary-outline", 
            command=self.destroy
        )
        btn_cancelar.pack(side="right")

    def on_guardar(self):
        nombre = self.entry_nombre.get().strip()
        categoria = self.combo_categoria.get()

        if not nombre:
            tb.dialogs.Messagebox.show_error("Debe ingresar un nombre o descripción", "Error", parent=self)
            return

        # Llama al controlador para registrarlo en el sistema
        self.producto_creado = self.controller.agregar_producto_manual(
            codigo=self.codigo_escaneado,
            nombre=nombre,
            categoria=categoria
        )
        
        # Cierra la ventana emergente
        self.destroy()