from config import settings
from data.excel_repository import ExcelRepository
from data.planilla_generator import PlanillaGenerator


def test_rutas_de_recursos_se_construyen_desde_raiz_configurada():
    assert settings.INVENTORY_PATH == (
        settings.RESOURCE_ROOT /
        settings.DATA_DIRECTORY_NAME /
        settings.INVENTORY_FILE_NAME)
    assert settings.RELEVO_TEMPLATE_PATH == (
        settings.RESOURCE_ROOT /
        settings.TEMPLATE_DIRECTORY_NAME /
        settings.RELEVO_TEMPLATE_FILE_NAME)
    assert settings.SEARCH_TEMPLATE_PATH == (
        settings.RESOURCE_ROOT /
        settings.TEMPLATE_DIRECTORY_NAME /
        settings.SEARCH_TEMPLATE_FILE_NAME)


def test_ensure_output_directory_crea_la_carpeta_configurada(
        tmp_path, monkeypatch):
    output_path = tmp_path / "salidas" / "relevos"
    monkeypatch.setattr(settings, "OUTPUT_DIRECTORY", output_path)

    resultado = settings.ensure_output_directory()

    assert resultado == output_path
    assert output_path.is_dir()


def test_columnas_requeridas_del_inventario_son_unicas():
    assert settings.INVENTORY_COLUMNS
    assert len(settings.INVENTORY_COLUMNS) == len(
        set(settings.INVENTORY_COLUMNS))


def test_repository_y_generator_usan_rutas_configuradas():
    repository = ExcelRepository()
    generator = PlanillaGenerator()

    assert repository.file_path == str(settings.INVENTORY_PATH)
    assert generator.ruta_plantilla_relevo == str(
        settings.RELEVO_TEMPLATE_PATH)
    assert generator.ruta_plantilla_busqueda == str(
        settings.SEARCH_TEMPLATE_PATH)
