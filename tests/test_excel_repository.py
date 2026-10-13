import os
from tempfile import NamedTemporaryFile

import pandas as pd

from data.excel_repository import ExcelRepository
from models.producto import Producto


def test_obtener_inventario_cuando_el_archivo_no_existe():
    repo = ExcelRepository(file_path="archivo_inexistente.xlsx")

    resultado = repo.obtener_inventario()

    assert resultado == []
    valido, errores = repo.validar_esquema()
    assert valido is False
    assert "No se encontró el archivo de inventario" in errores[0]


def test_obtener_inventario_con_archivo_valido():
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        temp_path = temp.name

    try:
        df = pd.DataFrame([
            {
                "NRO_INVENTARIO": "INV-01",
                "NRO_NUEVO": "NUEVO-01",
                "ELEMENTO": "Silla",
                "MARCA": "Marca X",
                "MODELO": "M1",
                "NRO_SERIE": "SERIE-01",
                "OFICINA": "Oficina 1",
                "DEPENDENCIA": "Administración",
            }
        ])
        df.to_excel(temp_path, index=False)

        repo = ExcelRepository(file_path=temp_path)
        productos = repo.obtener_inventario()

        assert len(productos) == 1
        assert productos[0].nro_inventario == "INV-01"
        assert productos[0].elemento == "Silla"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_obtener_inventario_con_columnas_faltantes():
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        temp_path = temp.name

    try:
        df = pd.DataFrame([
            {"NRO_INVENTARIO": "INV-01", "NRO_NUEVO": "NUEVO-01"}
        ])
        df.to_excel(temp_path, index=False)

        repo = ExcelRepository(file_path=temp_path)
        assert repo.obtener_inventario() == []
        valido, errores = repo.validar_esquema()
        assert valido is False
        assert "Faltan columnas obligatorias" in errores[0]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_guardar_nuevo_producto_con_archivo_valido():
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        temp_path = temp.name

    try:
        producto = Producto(
            nro_inventario="INV-100",
            nro_nuevo="NUEVO-100",
            elemento="Teclado",
            marca="HP",
            modelo="K500",
            nro_serie="SERIE-100",
            oficina="Oficina 2",
            dependencia="Contabilidad",
        )

        repo = ExcelRepository(file_path=temp_path)
        resultado = repo.guardar_nuevo_producto(producto)

        assert resultado is True
        inventario = repo.obtener_inventario()
        assert any(p.nro_nuevo == "NUEVO-100" for p in inventario)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_guardar_nuevo_producto_no_rompe_si_archivo_no_existe():
    temp_path = os.path.join(os.getcwd(), "test_archivo_inventario.xlsx")
    try:
        repo = ExcelRepository(file_path=temp_path)
        producto = Producto(
            nro_inventario="INV-200",
            nro_nuevo="NUEVO-200",
            elemento="Mouse",
            marca="Logitech",
            modelo="M90",
            nro_serie="SERIE-200",
            oficina="Oficina 3",
            dependencia="Tesorería",
        )

        resultado = repo.guardar_nuevo_producto(producto)

        assert resultado is True
        assert os.path.exists(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_guardar_nuevo_producto_no_sobrescribe_archivo_corrupto(tmp_path):
    file_path = tmp_path / "inventario.xlsx"
    contenido_original = b"archivo corrupto"
    file_path.write_bytes(contenido_original)
    producto = Producto(
        nro_inventario="INV-300",
        nro_nuevo="NUEVO-300",
        elemento="Monitor",
        marca="Dell",
        modelo="P1",
        nro_serie="SERIE-300",
        oficina="Oficina 4",
        dependencia="Administración",
    )

    repo = ExcelRepository(file_path=str(file_path))
    resultado = repo.guardar_nuevo_producto(producto)

    assert resultado is False
    assert file_path.read_bytes() == contenido_original


def test_guardar_nuevo_producto_rechaza_esquema_incompleto(tmp_path):
    file_path = tmp_path / "inventario.xlsx"
    pd.DataFrame([{"NRO_INVENTARIO": "INV-01"}]
                 ).to_excel(file_path, index=False)
    contenido_original = file_path.read_bytes()
    producto = Producto(
        nro_inventario="INV-301",
        nro_nuevo="NUEVO-301",
        elemento="Monitor",
        marca="Dell",
        modelo="P1",
        nro_serie="SERIE-301",
        oficina="Oficina 4",
        dependencia="Administración",
    )

    repo = ExcelRepository(file_path=str(file_path))

    assert repo.guardar_nuevo_producto(producto) is False
    assert file_path.read_bytes() == contenido_original


def test_exportar_escaneos_retorna_false_si_falla_el_guardado(
        tmp_path, monkeypatch):
    producto = Producto(
        nro_inventario="INV-400",
        nro_nuevo="NUEVO-400",
        elemento="Monitor",
        marca="Dell",
        modelo="P1",
        nro_serie="SERIE-400",
        oficina="Oficina 5",
        dependencia="Administración",
    )

    def fallar_guardado(*args, **kwargs):
        raise OSError("disco no disponible")

    monkeypatch.setattr(pd.DataFrame, "to_excel", fallar_guardado)
    repo = ExcelRepository(file_path=str(tmp_path / "salida.xlsx"))

    assert repo.exportar_escaneos(
        [producto], str(
            tmp_path / "salida.xlsx")) is False
