"""Diálogo para editar las observaciones de un producto de la sesión."""

import ttkbootstrap as tb
from models.producto import Producto


class EditarObservacionDialog(tb.Toplevel):
    """Ventana modal para modificar la observación de un bien.

    Args:
        parent: Ventana que abre el diálogo.
        producto: Producto que se editará.

    Returns:
        Instancia de `EditarObservacionDialog` asociada al producto.

    Raises:
        None.
    """

    def __init__(self, parent, producto: Producto):
        """Inicializa el editor para el producto indicado.

        Args:
            parent: Ventana que abre el diálogo.
            producto: Producto cuya observación puede actualizarse.

        Returns:
            None.

        Raises:
            None.
        """
        super().__init__(parent)
        self.title(f"Editar Registro - {producto.nro_inventario}")
        self.geometry("450x250")
        self.resizable(False, False)
        self.grab_set()

        self.producto = producto
        self.guardado = False

        self.setup_ui()

    def setup_ui(self):
        """Crea los campos y acciones de guardar o cancelar.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        container = tb.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        tb.Label(
            container,
            text=f"Elemento: {self.producto.elemento}",
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        tb.Label(
            container,
            text=f"N° Serie: {
                self.producto.nro_serie} | Serie/Inv: {
                self.producto.nro_inventario}",
            font=(
                "Helvetica",
                9),
            bootstyle="secondary").pack(
            anchor="w",
            pady=(
                0,
                15))

        tb.Label(
            container,
            text="Observaciones de la sesión:").pack(
            anchor="w")

        self.entry_obs = tb.Entry(container)
        self.entry_obs.insert(0, self.producto.observaciones)
        self.entry_obs.pack(fill="x", pady=(5, 15))
        self.entry_obs.focus()

        # Botones
        frame_btn = tb.Frame(container)
        frame_btn.pack(fill="x", side="bottom")

        tb.Button(
            frame_btn,
            text="Guardar Cambios",
            bootstyle="success",
            command=self.on_guardar
        ).pack(side="right", padx=5)

        tb.Button(
            frame_btn,
            text="Cancelar",
            bootstyle="secondary-outline",
            command=self.destroy
        ).pack(side="right")

    def on_guardar(self):
        """Copia el texto del campo al producto y cierra la ventana.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.producto.observaciones = self.entry_obs.get().strip()
        self.guardado = True
        self.destroy()
