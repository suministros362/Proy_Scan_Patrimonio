"""Punto de entrada de la aplicación de escritorio Relevo Patrimonio."""

import logging

from config import settings
from controllers.patrimonio_controller import PatrimonioController
from ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(
            settings.ensure_output_directory() /
            "relevo_patrimonio.log",
            encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def main():
    """Inicializa la aplicación y finaliza la auditoría al cerrar la ventana.

    Args:
        None.

    Returns:
        None.

    Raises:
        Exception: Propaga errores de inicialización o ejecución después del
            cierre.
    """
    logging.info("Iniciando aplicación Relevo Patrimonio.")
    # The finally block records session closure even if the event loop fails.
    controller = PatrimonioController()

    app = MainWindow(controller)

    try:
        app.mainloop()
    finally:
        controller.finalizar_sesion()


if __name__ == "__main__":
    main()
