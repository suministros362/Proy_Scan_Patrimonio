import os

import pandas as pd
import pytest
import logging

from data.excel_repository import ExcelRepository
from services.patrimonio_service import PatrimonioService


INVENTORY_COLUMNS = [
    "NRO_INVENTARIO",
    "NRO_NUEVO",
    "ELEMENTO",
    "MARCA",
    "MODELO",
    "NRO_SERIE",
    "OFICINA",
    "DEPENDENCIA",
]


def _crear_excel(ruta, filas, columnas=None):
    dataframe = pd.DataFrame(filas, columns=columnas or INVENTORY_COLUMNS)
    dataframe.to_excel(ruta, index=False)


def _fila(codigo, elemento):
    return {
        "NRO_INVENTARIO": f"INV-{codigo}",
        "NRO_NUEVO": codigo,
        "ELEMENTO": elemento,
        "MARCA": "Marca",
        "MODELO": "Modelo",
        "NRO_SERIE": f"SERIE-{codigo}",
        "OFICINA": "Oficina",
        "DEPENDENCIA": "Administración",
    }


def test_actualizar_inventario_reemplaza_maestro_con_archivo_valido(tmp_path):
    ruta_maestro = tmp_path / "inventario.xlsx"
    ruta_nueva = tmp_path / "nuevo_inventario.xlsx"
    _crear_excel(ruta_maestro, [_fila("ANTIGUO", "Silla")])
    _crear_excel(ruta_nueva, [_fila("NUEVO", "Monitor")])
    repository = ExcelRepository(file_path=str(ruta_maestro))

    productos = repository.actualizar_inventario(str(ruta_nueva))

    assert len(productos) == 1
    assert productos[0].nro_nuevo == "NUEVO"
    assert repository.obtener_inventario()[0].elemento == "Monitor"


def test_actualizar_inventario_invalido_no_modifica_maestro(tmp_path):
    ruta_maestro = tmp_path / "inventario.xlsx"
    ruta_nueva = tmp_path / "inventario_invalido.xlsx"
    _crear_excel(ruta_maestro, [_fila("ORIGINAL", "Silla")])
    _crear_excel(ruta_nueva,
                 [{"NRO_INVENTARIO": "INV-2",
                   "ELEMENTO": "Mesa"}],
                 ["NRO_INVENTARIO",
                     "ELEMENTO"])
    contenido_original = ruta_maestro.read_bytes()
    repository = ExcelRepository(file_path=str(ruta_maestro))

    with pytest.raises(ValueError, match="columnas obligatorias"):
        repository.actualizar_inventario(str(ruta_nueva))

    assert ruta_maestro.read_bytes() == contenido_original


def test_actualizar_inventario_faltante_da_error_descriptivo(tmp_path):
    repository = ExcelRepository(file_path=str(tmp_path / "inventario.xlsx"))

    with pytest.raises(
        ValueError,
        match="No se encontró el archivo de inventario",
    ):
        repository.actualizar_inventario(str(tmp_path / "no_existe.xlsx"))


def test_actualizar_inventario_rechaza_otro_formato(tmp_path):
    repository = ExcelRepository(file_path=str(tmp_path / "inventario.xlsx"))

    with pytest.raises(ValueError, match="formato .xlsx"):
        repository.actualizar_inventario(str(tmp_path / "inventario.xls"))


def test_actualizar_inventario_falla_sin_alterar_maestro_si_replace_falla(
        tmp_path,
        monkeypatch):
    ruta_maestro = tmp_path / "inventario.xlsx"
    ruta_nueva = tmp_path / "nuevo_inventario.xlsx"
    _crear_excel(ruta_maestro, [_fila("ORIGINAL", "Silla")])
    _crear_excel(ruta_nueva, [_fila("NUEVO", "Monitor")])
    contenido_original = ruta_maestro.read_bytes()
    repository = ExcelRepository(file_path=str(ruta_maestro))

    def fallar_replace(*args, **kwargs):
        raise PermissionError("archivo bloqueado")

    monkeypatch.setattr(os, "replace", fallar_replace)

    with pytest.raises(
        OSError,
        match="No se pudo reemplazar el inventario maestro",
    ):
        repository.actualizar_inventario(str(ruta_nueva))

    assert ruta_maestro.read_bytes() == contenido_original
    assert list(tmp_path.glob(".inventario_*.xlsx")) == []


def test_servicio_recarga_inventario_en_memoria_y_audita(
        tmp_path, monkeypatch, caplog):
    ruta_maestro = tmp_path / "inventario.xlsx"
    ruta_nueva = tmp_path / "nuevo_inventario.xlsx"
    _crear_excel(ruta_maestro, [_fila("ANTIGUO", "Silla")])
    _crear_excel(ruta_nueva, [_fila("NUEVO", "Monitor")])
    repository = ExcelRepository(file_path=str(ruta_maestro))
    monkeypatch.setattr(
        "services.patrimonio_service.ExcelRepository",
        lambda: repository)
    monkeypatch.setattr(
        "services.patrimonio_service.PlanillaGenerator",
        object)

    with caplog.at_level(logging.INFO):
        service = PatrimonioService()
        cantidad = service.actualizar_inventario(str(ruta_nueva))

    assert cantidad == 1
    assert [producto.nro_nuevo for producto in service.inventario_general] == [
        "NUEVO"]
    assert "event=inventory_updated" in caplog.text
    assert "success': True" in caplog.text
