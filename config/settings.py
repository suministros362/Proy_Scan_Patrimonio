"""Constantes y utilidades de configuración de rutas de la aplicación."""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

RESOURCE_ROOT = Path(
    getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1])
)

# Resource names are centralized here so development and packaged paths
# stay aligned.
DATA_DIRECTORY_NAME = "archivos"
TEMPLATE_DIRECTORY_NAME = "plantillas"
INVENTORY_FILE_NAME = "inventario.xlsx"
RELEVO_TEMPLATE_FILE_NAME = "plantilla_relevo.xlsx"
SEARCH_TEMPLATE_FILE_NAME = "plantilla_busqueda.xls"

INVENTORY_COLUMNS = (
    "NRO_INVENTARIO",
    "NRO_NUEVO",
    "ELEMENTO",
    "MARCA",
    "MODELO",
    "NRO_SERIE",
    "OFICINA",
    "DEPENDENCIA",
)

INVENTORY_PATH = RESOURCE_ROOT / DATA_DIRECTORY_NAME / INVENTORY_FILE_NAME
RELEVO_TEMPLATE_PATH = RESOURCE_ROOT / \
    TEMPLATE_DIRECTORY_NAME / RELEVO_TEMPLATE_FILE_NAME
SEARCH_TEMPLATE_PATH = RESOURCE_ROOT / \
    TEMPLATE_DIRECTORY_NAME / SEARCH_TEMPLATE_FILE_NAME
OUTPUT_DIRECTORY = Path.home() / "Documents" / "Relevo Patrimonio"
SEARCH_REPORT_PREFIX = "busqueda_masiva"
RELEVO_REPORT_EXTENSION = ".xlsx"
SEARCH_REPORT_EXTENSION = ".xls"


def ensure_output_directory() -> Path:
    """Crea o recupera una carpeta válida para reportes y logs.

    Args:
        None.

    Returns:
        Ruta de salida configurada o el directorio personal como alternativa.

    Raises:
        None: Los errores de creación se registran y usan la carpeta personal.
    """
    try:
        OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        return OUTPUT_DIRECTORY
    except OSError:
        logger.exception(
            "No se pudo preparar la carpeta de salida: %s",
            OUTPUT_DIRECTORY)
        return Path.home()
