import logging

from data.planilla_generator import PlanillaGenerator


def test_generar_relevo_reporta_plantilla_ausente(tmp_path, caplog):
    plantilla = tmp_path / "faltante.xlsx"
    generator = PlanillaGenerator(ruta_plantilla_relevo=str(plantilla))

    with caplog.at_level(logging.ERROR):
        resultado = generator.generar_relevo(
            {}, [], str(tmp_path / "salida.xlsx"))

    assert resultado is False
    assert str(plantilla) in caplog.text
    assert "No se encontró la plantilla de relevo" in caplog.text


def test_generar_busqueda_reporta_plantilla_ausente(tmp_path, caplog):
    plantilla = tmp_path / "faltante.xls"
    generator = PlanillaGenerator(ruta_plantilla_busqueda=str(plantilla))

    with caplog.at_level(logging.ERROR):
        resultado = generator.generar_busqueda(
            [], str(tmp_path / "salida.xls"))

    assert resultado is False
    assert str(plantilla) in caplog.text
    assert "No se encontró la plantilla de búsqueda" in caplog.text
