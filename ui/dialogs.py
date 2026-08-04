import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from models.producto import Producto


class AgregarProductoDialog(tb.Toplevel):
    def __init__(self, parent, codigo_escaneado, controller):
        super().__init__(parent)
        self.controller = controller
        self.codigo_escaneado = codigo_escaneado
        self.producto_creado = None

        self.title("Agregar Producto Manual")
        self.geometry("500x800")
        self.resizable(False, False)
        
        # Bloquear la ventana padre mientras esta esté abierta
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        container = tb.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        tb.Label(
            container, 
            text="Producto no encontrado", 
            font=("Helvetica", 12, "bold"), 
            bootstyle="warning"
        ).pack(anchor="w", pady=(0, 5))

        tb.Label(
            container, 
            text="Complete los datos para incluirlo en la sesión actual:", 
            font=("Helvetica", 9), 
            bootstyle="secondary"
        ).pack(anchor="w", pady=(0, 15))

        # Formulario
        grid_frame = tb.Frame(container)
        grid_frame.pack(fill="x", pady=5)

        # Campos
        tb.Label(grid_frame, text="N° Inventario:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_inv = tb.Entry(grid_frame)
        self.entry_inv.insert(0, self.codigo_escaneado)
        self.entry_inv.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="N° Nuevo:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_nuevo = tb.Entry(grid_frame)
        self.entry_nuevo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Elemento / Detalle (*):").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_elemento = tb.Entry(grid_frame)
        self.entry_elemento.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Marca:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_marca = tb.Entry(grid_frame)
        self.entry_marca.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Modelo:").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_modelo = tb.Entry(grid_frame)
        self.entry_modelo.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="N° Serie:").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_serie = tb.Entry(grid_frame)
        self.entry_serie.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Oficina:").grid(row=6, column=0, sticky="w", pady=5)
        self.entry_oficina = tb.Entry(grid_frame)
        self.entry_oficina.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Dependencia:").grid(row=7, column=0, sticky="w", pady=5)
        self.entry_dependencia = tb.Entry(grid_frame)
        self.entry_dependencia.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Observaciones:").grid(row=8, column=0, sticky="w", pady=5)
        self.entry_obs = tb.Entry(grid_frame)
        self.entry_obs.grid(row=8, column=1, sticky="ew", padx=(10, 0), pady=5)

        tb.Label(grid_frame, text="Sector:").grid(row=9, column=0, sticky="w", pady=5)
        self.entry_sector = tb.Entry(grid_frame)
        self.entry_sector.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=5)

        grid_frame.columnconfigure(1, weight=1)

        # Barra de Estado / Carga
        self.lbl_estado = tb.Label(container, text="", font=("Helvetica", 9))
        self.lbl_estado.pack(anchor="w", pady=(10, 0))

        # Botones
        frame_btn = tb.Frame(container)
        frame_btn.pack(fill="x", side="bottom", pady=(15, 0))

        self.btn_guardar = tb.Button(
            frame_btn, 
            text="Agregar a la Sesión", 
            bootstyle="success", 
            command=self.on_guardar
        )
        self.btn_guardar.pack(side="right", padx=5)

        self.btn_cancelar = tb.Button(
            frame_btn, 
            text="Cancelar", 
            bootstyle="secondary-outline", 
            command=self.destroy
        )
        self.btn_cancelar.pack(side="right")

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
         




#--------------------------------------------------------------------------------
#----Segunda versión de ventana emergente para agregar un producto manualmente (más completa)----------------
#--------------------------------------------------------------------------------
# import threading
# import ttkbootstrap as tb
# from ttkbootstrap.constants import *

# class AgregarProductoDialog(tb.Toplevel):
#     def __init__(self, parent, codigo_escaneado, controller):
#         super().__init__(parent)
        
#         self.controller = controller
#         self.codigo_escaneado = codigo_escaneado
#         self.producto_creado = None 
        
#         self.title("Alta Manual de Artículo")
#         self.geometry("480x650")
#         self.resizable(False, False)
        
#         self.grab_set()
#         self.setup_ui()

#     def setup_ui(self):
#         container = tb.Frame(self, padding=20)
#         container.pack(fill="both", expand=True)

#         # Encabezado
#         lbl_info = tb.Label(
#             container, 
#             text=f"Código Escaneado: {self.codigo_escaneado}", 
#             font=("Helvetica", 11, "bold"),
#             bootstyle="primary"
#         )
#         lbl_info.pack(anchor="w", pady=(0, 10))

#         # --- FORMULARIO DE CAMPOS ---
#         frame_form = tb.LabelFrame(container, text=" Datos del Artículo ", padding=15)
#         frame_form.pack(fill="both", expand=True, pady=(0, 10))

#         tb.Label(frame_form, text="N° Nuevo:").grid(row=0, column=0, sticky="w", pady=4)
#         self.entry_nro_nuevo = tb.Entry(frame_form)
#         self.entry_nro_nuevo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=4)

#         tb.Label(frame_form, text="N° Serie:").grid(row=1, column=0, sticky="w", pady=4)
#         self.entry_nro_serie = tb.Entry(frame_form)
#         self.entry_nro_serie.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=4)

#         tb.Label(frame_form, text="Elemento:").grid(row=2, column=0, sticky="w", pady=4)
#         self.entry_elemento = tb.Entry(frame_form)
#         self.entry_elemento.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=4)
#         self.entry_elemento.focus()

#         tb.Label(frame_form, text="Marca:").grid(row=3, column=0, sticky="w", pady=4)
#         self.entry_marca = tb.Entry(frame_form)
#         self.entry_marca.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=4)

#         tb.Label(frame_form, text="Modelo:").grid(row=4, column=0, sticky="w", pady=4)
#         self.entry_modelo = tb.Entry(frame_form)
#         self.entry_modelo.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=4)

#         tb.Label(frame_form, text="Oficina:").grid(row=5, column=0, sticky="w", pady=4)
#         self.entry_oficina = tb.Entry(frame_form)
#         self.entry_oficina.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=4)

#         tb.Label(frame_form, text="Dependencia:").grid(row=6, column=0, sticky="w", pady=4)
#         self.entry_dependencia = tb.Entry(frame_form)
#         self.entry_dependencia.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=4)

#         frame_form.columnconfigure(1, weight=1)

#         # --- BARRA DE PROGRESO / CARGA ---
#         self.frame_cargando = tb.Frame(container)
#         self.frame_cargando.pack(fill="x", pady=(0, 10))

#         self.lbl_estado = tb.Label(self.frame_cargando, text="Guardando registro en Excel...", font=("Helvetica", 9, "italic"), bootstyle="secondary")
#         self.progress_bar = tb.Progressbar(self.frame_cargando, mode="indeterminate", bootstyle="info-striped")
        
#         # Ocultamos la barra de estado inicialmente
#         self.lbl_estado.pack_forget()
#         self.progress_bar.pack_forget()

#         # --- BOTONES ---
#         self.frame_botones = tb.Frame(container)
#         self.frame_botones.pack(fill="x", side="bottom")

#         self.btn_guardar = tb.Button(
#             self.frame_botones, 
#             text="Guardar", 
#             bootstyle="success", 
#             command=self.iniciar_guardado
#         )
#         self.btn_guardar.pack(side="right", padx=5)

#         self.btn_cancelar = tb.Button(
#             self.frame_botones, 
#             text="Cancelar", 
#             bootstyle="secondary-outline", 
#             command=self.destroy
#         )
#         self.btn_cancelar.pack(side="right")

#     def iniciar_guardado(self):
#         """Valida y arranca el hilo secundario para no congelar la UI."""
#         nro_nuevo = self.entry_nro_nuevo.get().strip()
#         nro_serie = self.entry_nro_serie.get().strip()
#         elemento = self.entry_elemento.get().strip()
#         marca = self.entry_marca.get().strip()
#         modelo = self.entry_modelo.get().strip()
#         oficina = self.entry_oficina.get().strip()
#         dependencia = self.entry_dependencia.get().strip()

#         campos_ingresados = [nro_nuevo, nro_serie, elemento, marca, modelo, oficina, dependencia]
#         if not any(campos_ingresados):
#             tb.dialogs.Messagebox.show_warning(
#                 "Debes completar al menos un campo para poder registrar el artículo.",
#                 "Formulario Vacío",
#                 parent=self
#             )
#             return

#         # 1. Mostrar barra de carga y animar
#         self.btn_guardar.config(state="disabled")
#         self.btn_cancelar.config(state="disabled")
#         self.lbl_estado.pack(anchor="w", pady=(0, 2))
#         self.progress_bar.pack(fill="x")
#         self.progress_bar.start(10) # Hace que la barrita rebote continuamente

#         # 2. Ejecutar la tarea pesada de guardado en un hilo (Thread) separado
#         datos = (nro_nuevo, elemento, marca, modelo, nro_serie, oficina, dependencia)
#         threading.Thread(target=self._guardar_en_segundo_plano, args=datos, daemon=True).start()

#     def _guardar_en_segundo_plano(self, nro_nuevo, elemento, marca, modelo, nro_serie, oficina, dependencia):
#         """Método que corre en el hilo secundario para guardar el Excel."""
#         exito, producto = self.controller.agregar_producto_manual(
#             nro_inventario=nro_nuevo,
#             nro_nuevo=nro_nuevo,
#             elemento=elemento,
#             marca=marca,
#             modelo=modelo,
#             nro_serie=nro_serie,
#             oficina=oficina,
#             dependencia=dependencia
#         )

#         # 3. Retornar los resultados a la interfaz
#         if exito:
#             self.producto_creado = producto
#             self.destroy() # Cierra la ventana emergente automáticamente
#         else:
#             # Si hubo un error (ej. Excel bloqueado), restaurar la interfaz en la ventana
#             self.progress_bar.stop()
#             self.progress_bar.pack_forget()
#             self.lbl_estado.pack_forget()
#             self.btn_guardar.config(state="normal")
#             self.btn_cancelar.config(state="normal")

#-------------------------------------------------------------------------------
#-----Segunda versión de ventana emergente para agregar un producto manualmente (más completa)----------------
#-------------------------------------------------------------------------------

# import ttkbootstrap as tb
# from ttkbootstrap.constants import *

# class AgregarProductoDialog(tb.Toplevel):
#     def __init__(self, parent, codigo_escaneado, controller):
#         super().__init__(parent)
        
#         self.controller = controller
#         self.codigo_escaneado = codigo_escaneado
#         self.producto_creado = None  # Guardará el producto si se completa con éxito
        
#         self.title("Alta Manual de Artículo")
#         self.geometry("480x700")
#         self.resizable(False, False)
        
#         # Vuelve la ventana modal (bloquea la ventana de atrás)
#         self.grab_set()

#         self.setup_ui()

#     def setup_ui(self):
#         container = tb.Frame(self, padding=20)
#         container.pack(fill="both", expand=True)

#         # Encabezado informativo
#         lbl_info = tb.Label(
#             container, 
#             text=f"Código Escaneado: {self.codigo_escaneado}", 
#             font=("Helvetica", 11, "bold"),
#             bootstyle="primary"
#         )
#         lbl_info.pack(anchor="w", pady=(0, 15))

#         # --- FORMULARIO DE CAMPOS OPCIONALES ---
#         frame_form = tb.LabelFrame(container, text=" Datos del Artículo ", padding=15)
#         frame_form.pack(fill="both", expand=True, pady=(0, 15))

#         # 1. NRO_NUEVO
#         tb.Label(frame_form, text="N° Nuevo:").grid(row=0, column=0, sticky="w", pady=4)
#         self.entry_nro_nuevo = tb.Entry(frame_form)
#         self.entry_nro_nuevo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=4)

#         # 2. NRO_SERIE
#         tb.Label(frame_form, text="N° Serie:").grid(row=1, column=0, sticky="w", pady=4)
#         self.entry_nro_serie = tb.Entry(frame_form)
#         self.entry_nro_serie.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=4)

#         # 3. ELEMENTO
#         tb.Label(frame_form, text="Elemento:").grid(row=2, column=0, sticky="w", pady=4)
#         self.entry_elemento = tb.Entry(frame_form)
#         self.entry_elemento.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=4)
#         self.entry_elemento.focus() # Foco inicial en elemento por comodidad

#         # 4. MARCA
#         tb.Label(frame_form, text="Marca:").grid(row=3, column=0, sticky="w", pady=4)
#         self.entry_marca = tb.Entry(frame_form)
#         self.entry_marca.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=4)

#         # 5. MODELO
#         tb.Label(frame_form, text="Modelo:").grid(row=4, column=0, sticky="w", pady=4)
#         self.entry_modelo = tb.Entry(frame_form)
#         self.entry_modelo.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=4)

#         # 6. OFICINA (Opcional)
#         tb.Label(frame_form, text="Oficina:").grid(row=5, column=0, sticky="w", pady=4)
#         self.entry_oficina = tb.Entry(frame_form)
#         self.entry_oficina.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=4)

#         # 7. DEPENDENCIA (Opcional)
#         tb.Label(frame_form, text="Dependencia:").grid(row=6, column=0, sticky="w", pady=4)
#         self.entry_dependencia = tb.Entry(frame_form)
#         self.entry_dependencia.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=4)

#         frame_form.columnconfigure(1, weight=1)

#         # --- BOTONES ---
#         frame_botones = tb.Frame(container)
#         frame_botones.pack(fill="x", side="bottom")

#         btn_guardar = tb.Button(
#             frame_botones, 
#             text="Guardar", 
#             bootstyle="success", 
#             command=self.on_guardar
#         )
#         btn_guardar.pack(side="right", padx=5)

#         btn_cancelar = tb.Button(
#             frame_botones, 
#             text="Cancelar", 
#             bootstyle="secondary-outline", 
#             command=self.destroy
#         )
#         btn_cancelar.pack(side="right")

#     def on_guardar(self):
#         # Tomamos los valores limpios que el usuario escribió manualmente
#         nro_nuevo = self.entry_nro_nuevo.get().strip()
#         nro_serie = self.entry_nro_serie.get().strip()
#         elemento = self.entry_elemento.get().strip()
#         marca = self.entry_marca.get().strip()
#         modelo = self.entry_modelo.get().strip()
#         oficina = self.entry_oficina.get().strip()
#         dependencia = self.entry_dependencia.get().strip()

#         # Validación: Al menos un campo debe tener texto
#         campos_ingresados = [nro_nuevo, nro_serie, elemento, marca, modelo, oficina, dependencia]
#         if not any(campos_ingresados):
#             tb.dialogs.Messagebox.show_warning(
#                 "Debes completar al menos un campo para poder registrar el artículo.",
#                 "Formulario Vacío",
#                 parent=self
#             )
#             return

#         # 🚀 Enviamos la información 100% manual (nro_inventario irá vacío a menos que lo agregues al formulario)
#         exito, producto = self.controller.agregar_producto_manual(
#             nro_inventario="",
#             nro_nuevo=nro_nuevo,
#             elemento=elemento,
#             marca=marca,
#             modelo=modelo,
#             nro_serie=nro_serie,
#             oficina=oficina,
#             dependencia=dependencia
#         )
        
#         # 🚀 SOLO si se guardó correctamente en el Excel maestro, asignamos y cerramos
#         if exito:
#             self.producto_creado = producto
#             self.destroy()
#         # Si falló (ej. Excel abierto), NO cerramos la ventana para que el usuario no pierda lo que tipeó
#-------------------------------------------------------------------------------
#-----Primer intento de ventana emergente para agregar un producto manualmente----------------
#-------------------------------------------------------------------------------

# import ttkbootstrap as tb
# from ttkbootstrap.constants import *

# class AgregarProductoDialog(tb.Toplevel):
#     def __init__(self, parent, codigo_escaneado, controller):
#         super().__init__(parent)
        
#         self.controller = controller
#         self.codigo_escaneado = codigo_escaneado
#         self.producto_creado = None  # Guardará el producto resultante si se confirma
        
#         # Configuración de la ventana emergente
#         self.title("Agregar Artículo Nuevo")
#         self.geometry("450x450")
#         self.resizable(False, False)
        
#         # Bloquea la interacción con la ventana principal mientras esta esté abierta
#         self.grab_set()

#         # Dibujamos los componentes visuales de este diálogo
#         self.setup_ui()

#     def setup_ui(self):
#         # Frame contenedor con padding
#         frame = tb.Frame(self, padding=20)
#         frame.pack(fill="both", expand=True)

#         # 1. Muestra el Código Escaneado (Solo lectura)
#         lbl_codigo = tb.Label(
#             frame, 
#             text=f"Código Patrimonial: {self.codigo_escaneado}", 
#             font=("Helvetica", 11, "bold"),
#             bootstyle="primary"
#         )
#         lbl_codigo.pack(anchor="w", pady=(0, 15))

#         # 2. Campo: Nombre / Descripción
#         tb.Label(frame, text="Descripción del Artículo:").pack(anchor="w")
#         self.entry_nombre = tb.Entry(frame)
#         self.entry_nombre.pack(fill="x", pady=(0, 10))
#         self.entry_nombre.focus() # Pone el foco directamente aquí

#         # 3. Campo: Categoría (Desplegable)
#         tb.Label(frame, text="Categoría:").pack(anchor="w")
#         self.combo_categoria = tb.Combobox(
#             frame, 
#             values=["Mobiliario", "Informática", "Electrónica", "Otros"],
#             state="readonly"
#         )
#         self.combo_categoria.set("Mobiliario")
#         self.combo_categoria.pack(fill="x", pady=(0, 20))

#         # 4. Botones de Acción
#         frame_botones = tb.Frame(frame)
#         frame_botones.pack(fill="x", side="bottom")

#         btn_guardar = tb.Button(
#             frame_botones, 
#             text="Guardar", 
#             bootstyle="success", 
#             command=self.on_guardar
#         )
#         btn_guardar.pack(side="right", padx=5)

#         btn_cancelar = tb.Button(
#             frame_botones, 
#             text="Cancelar", 
#             bootstyle="secondary-outline", 
#             command=self.destroy
#         )
#         btn_cancelar.pack(side="right")

#     def on_guardar(self):
#         nombre = self.entry_nombre.get().strip()
#         categoria = self.combo_categoria.get()

#         if not nombre:
#             tb.dialogs.Messagebox.show_error("Debe ingresar un nombre o descripción", "Error", parent=self)
#             return

#         # Llama al controlador para registrarlo en el sistema
#         self.producto_creado = self.controller.agregar_producto_manual(
#             codigo=self.codigo_escaneado,
#             nombre=nombre,
#             categoria=categoria
#         )
        
#         # Cierra la ventana emergente
#         self.destroy()