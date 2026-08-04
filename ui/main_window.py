import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog

from ui.observacion_dialogs import EditarObservacionDialog
from ui.dialogs import AgregarProductoDialog
from ui.planillas_dialogs import PlanillaRelevoDialog

class MainWindow(tb.Window):
    def __init__(self, controller):
        self.tema_claro = "bootstrap-light"
        self.tema_oscuro = "one-dark"
        
        super().__init__(
            title="Control de Patrimonio",
            themename=self.tema_claro,
            size=(1200, 750)
        )
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        # --- CABECERA Y SWITCH DE TEMA ---
        frame_top = tb.Frame(self, padding=(20, 10))
        frame_top.pack(fill="x")

        btn_limpiar = tb.Button(
            frame_top, 
            text="🗑️ Nueva Sesión", 
            bootstyle="danger-outline", 
            command=self.on_limpiar_sesion
        )
        btn_limpiar.pack(side="left", padx=5)

        self.switch_tema = tb.Checkbutton(
            frame_top, 
            text="Modo Oscuro", 
            bootstyle="round-toggle", 
            command=self.alternar_tema,
            width=12
        )
        self.switch_tema.pack(side="right")

        # --- FRAME DE ESCANEO ---
        frame_scan = tb.LabelFrame(self, text=" Escaneo de Código ", padding=15, bootstyle="primary")
        frame_scan.pack(fill="x", padx=20, pady=5)

        tb.Label(frame_scan, text="Código Escaneado:").pack(side="left", padx=5)
        
        self.entry_codigo = tb.Entry(frame_scan, font=("Helvetica", 11), width=30)
        self.entry_codigo.pack(side="left", padx=10)
        self.entry_codigo.focus()
        self.entry_codigo.bind("<Return>", self.on_escanear)

        btn_scan = tb.Button(frame_scan, text="Procesar", command=self.on_escanear, bootstyle="primary")
        btn_scan.pack(side="left", padx=5)

        #Botón para definir el sector actual
        btn_sector = tb.Button(frame_scan, text="📍 Definir Sector", command=self.on_cambiar_sector, bootstyle="info-outline")
        btn_sector.pack(side="left", padx=5)

        #Label indicador de sector actual (Opcional pero muy útil para el usuario)
        self.label_sector_activo = tb.Label(frame_scan, text="Sector: ----", bootstyle="primary", font=("Helvetica", 10, "bold"), foreground="orange")
        self.label_sector_activo.pack(side="left", padx=10)

        

        # --- TABLA DE RESULTADOS (8 CAMPOS) ---
        frame_tabla = tb.LabelFrame(self, text=" Bienes Escaneados ", padding=10, bootstyle="info")
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("nro","nro_inv", "nro_nuevo", "elemento", "marca", "modelo", "nro_serie", "oficina", "dependencia", "observaciones", "sector")
        
        self.tabla = tb.Treeview(frame_tabla, columns=columnas, show="headings", bootstyle="info")
        
        # Encabezados
        self.tabla.heading("nro", text="N°")
        self.tabla.heading("nro_inv", text="N° Inventario")
        self.tabla.heading("nro_nuevo", text="N° Nuevo")
        self.tabla.heading("elemento", text="Elemento")
        self.tabla.heading("marca", text="Marca")
        self.tabla.heading("modelo", text="Modelo")
        self.tabla.heading("nro_serie", text="N° Serie")
        self.tabla.heading("oficina", text="Oficina")
        self.tabla.heading("dependencia", text="Dependencia")
        self.tabla.heading("observaciones", text="Observaciones")
        self.tabla.heading("sector", text="Sector")
        # Anchos de columna optimizados
        self.tabla.column("nro", width=50, anchor="center")
        self.tabla.column("nro_inv", width=100, anchor="center")
        self.tabla.column("nro_nuevo", width=100, anchor="center")
        self.tabla.column("elemento", width=180, anchor="w")
        self.tabla.column("marca", width=110, anchor="w")
        self.tabla.column("modelo", width=110, anchor="w")
        self.tabla.column("nro_serie", width=110, anchor="center")
        self.tabla.column("oficina", width=110, anchor="w")
        self.tabla.column("dependencia", width=130, anchor="w")
        self.tabla.column("observaciones", width=200, anchor="w")
        self.tabla.column("sector", width=110, anchor="center")

        # Permitir doble clic en la tabla para editar
        self.tabla.bind("<Double-1>", self.on_modificar_observacion)

        # Scrollbar para la tabla
        scrollbar = tb.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- BOTONES PARA LAS 3 PLANILLAS ---
        frame_bottom = tb.LabelFrame(self, text=" Generación de Planillas ", padding=10)
        frame_bottom.pack(fill="x", padx=20, pady=(0, 15))

        # Botón para modificar la observación del ítem seleccionado en la tabla
        btn_modificar = tb.Button(
            frame_bottom, 
            text="✏️ Agregar/Modificar Observación", 
            bootstyle="warning-outline", 
            command=self.on_modificar_observacion
        )
        btn_modificar.pack(side="left", padx=10)

        # Botón para eliminar el ítem seleccionado en la tabla
        btn_eliminar = tb.Button(
            frame_bottom, 
            text="🗑️ Eliminar Registro", 
            bootstyle="danger-outline", 
            command=self.on_eliminar_registro
        )
        btn_eliminar.pack(side="left", padx=10)

        btn_planilla1 = tb.Button(
            frame_bottom,
            text="Planilla de Relevo", 
            bootstyle="success", 
            command=self.on_generar_relevo
        )
        btn_planilla1.pack(side="left", padx=10)

        btn_planilla2 = tb.Button(
            frame_bottom,
            text="Planilla 2",
            bootstyle="info-outline",
            command=lambda: print("Generar Planilla 2")
        )
        btn_planilla2.pack(side="left", padx=10)

        btn_planilla3 = tb.Button(
            frame_bottom,
            text="Planilla 3",
            bootstyle="warning-outline",
            command=lambda: print("Generar Planilla 3")
        )
        btn_planilla3.pack(side="left", padx=10)

    def on_limpiar_sesion(self):
        """Pide confirmación y limpia la sesión actual y la tabla."""
        if not self.tabla.get_children():
            self.entry_codigo.focus()    
            return

        respuesta = messagebox.askyesno(
            "Confirmar", 
            "¿Deseas reiniciar la sesión actual? Se borrarán los artículos de la lista activa."
        )
        if respuesta:
            self.controller.limpiar_sesion_actual()
            self.label_sector_activo.config(text="Sector Actual: Ninguno", bootstyle="secondary")
            # Limpiar filas del Treeview
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            self.entry_codigo.focus()
        self.entry_codigo.focus()

    def on_modificar_observacion(self, event=None):
        """Abre la ventana emergente para modificar la observación del producto seleccionado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            tb.dialogs.Messagebox.show_warning(
                "Seleccione un elemento de la lista para editar.",
                title="Sin selección",
                parent=self
            )
            return

        item_id = seleccion[0]
        index = self.tabla.index(item_id)

        # Obtenemos el objeto correspondiente desde la lista de la sesión en el controller
        producto = self.controller.service.escaneados_sesion[index]

        # Abrir el diálogo de modificación
        dialogo = EditarObservacionDialog(self, producto)
        self.wait_window(dialogo)

        if dialogo.guardado:
            # Actualizar la fila en la tabla visual
            self.refrescar_tabla()
            # self.tabla.item(item_id, values=(
            #     producto.nro_inventario, producto.nro_nuevo, producto.elemento,
            #     producto.marca, producto.modelo, producto.nro_serie, 
            #     producto.oficina, producto.dependencia, producto.observaciones
            # ))
        self.entry_codigo.focus()    

    def on_generar_relevo(self):
        """Flujo para generar la planilla de relevo."""
        if not self.tabla.get_children():
            messagebox.showwarning("Atención", "No hay elementos escaneados en la sesión actual.")
            self.entry_codigo.focus()
            return

        # 1. Solicitar Piso, Oficina, Área y Dependencia
        dialogo = PlanillaRelevoDialog(self)
        self.wait_window(dialogo)

        if not dialogo.datos:
            self.entry_codigo.focus()
            return  # Canceló el diálogo

        # 2. Elegir dónde guardar el Excel generado
        ruta_salida = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")],
            title="Guardar Planilla de Relevo Como..."
        )

        if not ruta_salida:
            self.entry_codigo.focus()
            return

        # 3. Generar Excel
        exito = self.controller.generar_planilla_relevo(dialogo.datos, ruta_salida)

        if exito:
            tb.dialogs.Messagebox.show_info(
                f"Planilla generada con éxito en:\n{ruta_salida}",
                title="Reporte Creado",
                parent=self
            )
            #messagebox.showinfo("Éxito", f"Planilla generada correctamente en:\n{ruta_salida}")
        else:
            # tb.dialogs.Messagebox.show_error(
            #     "No se pudo generar la planilla. Asegúrate de tener la plantilla 'plantilla_relevo.xlsx' en la raíz del proyecto y que no esté en uso.",
            #     title="Error de Generación",
            #     parent=self
            # )
            messagebox.showerror("Error", "No se pudo generar la planilla. Verifica que la plantilla no esté en uso.")
        self.entry_codigo.focus()    



    def alternar_tema(self):
        if "selected" in self.switch_tema.state():
            self.style.theme_use(self.tema_oscuro)
            self.switch_tema.config(text="Modo Claro")
        else:
            self.style.theme_use(self.tema_claro)
            self.switch_tema.config(text="Modo Oscuro")
        self.entry_codigo.focus()

    def on_escanear(self, event=None):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            return

        self.entry_codigo.delete(0, 'end')

        resultado = self.controller.procesar_codigo_escaneado(codigo)

        if resultado["encontrado"]:
            if resultado["razon"] == "duplicado":
                p = resultado["producto"]
                messagebox.showwarning("Producto Ya Escaneado", f"El artículo '{p.elemento}' ({codigo}) YA fue registrado en esta sesión.")
            else:
                self.refrescar_tabla()    
                # p = resultado["producto"]
                # self.tabla.insert("", "end", values=(
                # p.nro_inventario, p.nro_nuevo, p.elemento, 
                # p.marca, p.modelo, p.nro_serie, p.oficina, p.dependencia
            # ))
        else:
            # 1. Alerta de código no encontrado
            respuesta = messagebox.askyesno(
                "No Encontrado", 
                f"El código {codigo} no existe. \n\n ¿Deseas proceder al alta manual?"
            )
            
            # 2. Abrir la ventana emergente pasando el código no encontrado
            if respuesta:
                dialogo = AgregarProductoDialog(self, codigo, self.controller)
                self.wait_window(dialogo) # Bloquea la ventana principal hasta cerrar el diálogo

                # 3. Si el usuario guardó el producto, lo insertamos en la tabla principal
                if dialogo.producto_creado:
                    self.refrescar_tabla()
                    # p = dialogo.producto_creado
                    # self.tabla.insert("", "end", values=(
                    #     p.nro_inventario, p.nro_nuevo, p.elemento, 
                    #     p.marca, p.modelo, p.nro_serie, p.oficina, p.dependencia
                    # ))
        self.entry_codigo.focus()

    def refrescar_tabla(self):
        """Limpia y vuelve a cargar toda la tabla asignando el N° correlativo correcto."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for idx, p in enumerate(self.controller.service.escaneados_sesion, start=1):
            sector_prod = getattr(p, "sector", "")  or "Sin Sector"# Obtener el sector del producto, si existe
            tag_name = f"tag_{sector_prod}"

            if sector_prod in self.controller.service.mapa_colores_sectores:
                color_fondo = self.controller.service.mapa_colores_sectores[sector_prod]
                self.tabla.tag_configure(tag_name, background=color_fondo)


            self.tabla.insert("", "end", values=(
                idx, p.nro_inventario, p.nro_nuevo, p.elemento, 
                p.marca, p.modelo, p.nro_serie, p.oficina, p.dependencia, p.observaciones, p.sector.upper()
            ), tags=(tag_name,))

    def on_eliminar_registro(self):
        """Elimina la fila seleccionada y recalcula la numeración."""
        seleccion = self.tabla.selection()
        if not seleccion:
            tb.dialogs.Messagebox.show_warning(
                "Seleccione un registro de la lista para eliminar.",
                title="Sin Selección",
                parent=self
            )
            self.entry_codigo.focus()
            return

        confirmar = tb.dialogs.Messagebox.show_question(
            "¿Desea eliminar el elemento seleccionado de esta sesión?",
            title="Confirmar Eliminación",
            parent=self
        )

        if str(confirmar).lower() in ["yes", "ok", "true", "si", "sí"]:
            item_id = seleccion[0]
            index = self.tabla.index(item_id)
            self.controller.eliminar_producto_sesion(index)
            self.refrescar_tabla()
        self.entry_codigo.focus()

    def on_cambiar_sector(self):
        """Abre un diálogo para que el usuario defina el sector actual."""
        sector = tb.dialogs.Querybox.get_string(
            prompt="Ingrese el nombre del sector actual:",
            title="Definir Sector",
            parent=self
        )

        if sector is not None: 
            sector = sector.strip()
            self.controller.service.cambiar_sector_actual(sector)

            if sector:
                self.label_sector_activo.config(text=f"Sector: {sector.upper()}", bootstyle="info")
            else:
                self.label_sector_activo.config(text="Sector: ----", bootstyle="secondary")

            self.refrescar_tabla()  # Actualiza la tabla para reflejar el cambio de sector
        self.entry_codigo.focus()

#-----------------------------------------------------------------------------------------
#------------------Primera Version de la ventana principal con ttkbootstrap---------------
#-----------------------------------------------------------------------------------------
# import ttkbootstrap as tb
# from tkinter import messagebox
# from ui.dialogs import AgregarProductoDialog

# class MainWindow(tb.Window):
#     def __init__(self, controller):
#         #Definimos los dos temas a alternar
#         self.tema_claro = "flatly"    # Tema claro moderno
#         self.tema_oscuro = "vapor-dark"   # Tema oscuro moderno
#         super().__init__(
#             title="Control Patrimonial",
#             themename=self.tema_claro,
#             size=(750, 750)
#         )
#         self.controller = controller # Inyectamos el controlador
#         self.setup_ui()

#     def setup_ui(self):
#         # --- CABECERA Y CAMBIO DE TEMA ---
#         frame_top = tb.Frame(self, padding=(20, 10))
#         frame_top.pack(fill="x")

#         # Interruptor (Switch) para alternar tema
#         # Al hacer clic, ejecuta el método self.alternar_tema
#         self.switch_tema = tb.Checkbutton(
#             frame_top, 
#             text="Modo Oscuro", 
#             bootstyle="round-toggle", 
#             command=self.alternar_tema,
#             width=12
#         )
#         self.switch_tema.pack(side="right")
#         # --- FRAME ESCANEO ---
#         frame_scan = tb.LabelFrame(self, text=" Escaneo ", padding=15, bootstyle="primary")
#         frame_scan.pack(fill="x", padx=20, pady=10)

#         self.entry_codigo = tb.Entry(frame_scan, font=("Helvetica", 11), width=25)
#         self.entry_codigo.pack(side="left", padx=10)
#         self.entry_codigo.focus()
#         self.entry_codigo.bind("<Return>", self.on_escanear)

#         btn_scan = tb.Button(frame_scan, text="Procesar", command=self.on_escanear, bootstyle="primary")
#         btn_scan.pack(side="left", padx=5)

#         # --- TABLA DE ESCANEADOS ---
#         frame_tabla = tb.LabelFrame(self, text=" Escaneados en la Sesión ", padding=15, bootstyle="info")
#         frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

#         self.tabla = tb.Treeview(frame_tabla, columns=("codigo", "nombre", "categoria"), show="headings", bootstyle="info")
#         self.tabla.heading("codigo", text="Código")
#         self.tabla.heading("nombre", text="Artículo")
#         self.tabla.heading("categoria", text="Categoría")
#         self.tabla.pack(fill="both", expand=True)

#         # --- BOTÓN EXPORTAR ---
#         btn_exportar = tb.Button(self, text="Generar Excel", command=self.on_exportar, bootstyle="success")
#         btn_exportar.pack(side="right", padx=20, pady=10)

#     def alternar_tema(self):
#         """Método que cambia el tema de la ventana en tiempo real."""
#         # Verificamos si el switch está activado
#         if "selected" in self.switch_tema.state():
#             # Cambiar a Modo Oscuro
#             self.style.theme_use(self.tema_oscuro)
#             toggle_text = "Modo Claro"
#             self.switch_tema.config(text=toggle_text)
#         else:
#             # Cambiar a Modo Claro
#             self.style.theme_use(self.tema_claro)
#             toggle_text = "Modo Oscuro"
#             self.switch_tema.config(text=toggle_text)
#         self.entry_codigo.focus()

#     def on_escanear(self, event=None):
#         codigo = self.entry_codigo.get().strip()
#         if not codigo:
#             return

#         self.entry_codigo.delete(0, 'end')

#         # Se solicita la acción al controlador
#         resultado = self.controller.procesar_codigo_escaneado(codigo)

#         if resultado["encontrado"]:
#             prod = resultado["producto"]
#             self.tabla.insert("", "end", values=(prod.codigo, prod.nombre, prod.categoria))
#         else:
#             messagebox.showwarning("No Encontrado", f"El código {codigo} no existe. Procede al alta manual.")
#             # 🚀 Abrir la ventana emergente pasándole el código que no existía
#             dialogo = AgregarProductoDialog(self, codigo, self.controller)
#             self.wait_window(dialogo) # Espera a que el usuario cierre la ventana emergente

#             # Si el usuario guardó el producto, actualizamos la tabla principal
#             if dialogo.producto_creado:
#                 prod = dialogo.producto_creado
#                 self.tabla.insert("", "end", values=(prod.codigo, prod.nombre, prod.categoria))

#     def on_exportar(self):
#         exito = self.controller.exportar_planilla("Reporte_Patrimonio.xlsx")
#         if exito:
#             messagebox.showinfo("Éxito", "Planilla exportada con éxito.")
#         else:
#             messagebox.showwarning("Atención", "No hay items para exportar.")