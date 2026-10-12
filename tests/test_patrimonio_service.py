import logging

import pytest

from models.producto import Producto
from services.patrimonio_service import PatrimonioService


def _crear_producto(**overrides):
    base = {
        "nro_inventario": "INV-001",
        "nro_nuevo": "NUEVO-001",
        "elemento": "Monitor",
        "marca": "Dell",
        "modelo": "P2419H",
        "nro_serie": "SERIE-001",
        "oficina": "Oficina Central",
        "dependencia": "Administración",
        "observaciones": "",
        "sector": "Administración",
    }
    base.update(overrides)
    return Producto(**base)


def test_buscar_producto_por_codigo_cuando_existe():
    service = PatrimonioService()
    service.inventario_general = [_crear_producto()]

    resultado = service.buscar_producto_por_codigo("NUEVO-001")

    assert resultado is not None
    assert resultado.nro_nuevo == "NUEVO-001"


def test_buscar_producto_por_codigo_cuando_no_existe():
    service = PatrimonioService()
    service.inventario_general = [_crear_producto(nro_nuevo="NUEVO-999")]

    resultado = service.buscar_producto_por_codigo("NUEVO-001")

    assert resultado is None


def test_procesar_codigo_retorna_ok_si_existe_y_no_duplicado():
    service = PatrimonioService()
    producto = _crear_producto()
    service.inventario_general = [producto]

    resultado = service.procesar_codigo("NUEVO-001")

    assert resultado["encontrado"] is True
    assert resultado["razon"] == "ok"
    assert resultado["producto"] == producto
    assert service.escaneados_sesion == [producto]


def test_procesar_codigo_retorna_duplicado_si_ya_fue_escaneado():
    service = PatrimonioService()
    producto = _crear_producto()
    service.inventario_general = [producto]
    service.escaneados_sesion = [producto]

    resultado = service.procesar_codigo("NUEVO-001")

    assert resultado["encontrado"] is True
    assert resultado["razon"] == "duplicado"


def test_crear_y_registrar_producto_agrega_a_sesion():
    service = PatrimonioService()
    service.sector_actual = "Contabilidad"

    producto = service.crear_y_registrar_producto({
        "nro_inventario": "INV-100",
        "nro_nuevo": "NUEVO-100",
        "elemento": "Impresora",
        "marca": "Epson",
        "modelo": "L220",
        "nro_serie": "SERIE-100",
        "oficina": "Oficina 2",
        "dependencia": "Contabilidad",
        "observaciones": "Alta manual en sesión",
        "sector": "Contabilidad",
    })

    assert producto.elemento == "Impresora"
    assert len(service.escaneados_sesion) == 1
    assert service.escaneados_sesion[0].sector == "Contabilidad"


def test_crear_y_registrar_producto_rechaza_elemento_vacio():
    service = PatrimonioService()
    datos = {
        "nro_inventario": "INV-101",
        "nro_nuevo": "NUEVO-101",
        "elemento": "",
        "marca": "",
        "modelo": "",
        "nro_serie": "",
        "oficina": "",
        "dependencia": "",
        "observaciones": "",
        "sector": "",
    }

    with pytest.raises(ValueError, match="Elemento.*obligatorio"):
        service.crear_y_registrar_producto(datos)

    assert service.escaneados_sesion == []


def test_validar_producto_manual_rechaza_elemento_vacio():
    service = PatrimonioService()

    assert service.validar_producto_manual(
        {"elemento": "  "}) == "El campo 'Elemento' es obligatorio."


def test_auditoria_registra_inicio_escaneo_alta_manual_y_cierre(caplog):
    producto = _crear_producto()

    with caplog.at_level(logging.INFO):
        service = PatrimonioService()
        service.inventario_general = [producto]
        service.procesar_codigo("NUEVO-001")
        service.crear_y_registrar_producto({"elemento": "Impresora"})
        service.finalizar_sesion()

    assert "event=session_started" in caplog.text
    assert "event=scan_registered" in caplog.text
    assert "scan_count': 1" in caplog.text
    assert "event=manual_product_added" in caplog.text
    assert "manual_add_count': 1" in caplog.text
    assert "event=session_ended" in caplog.text
    assert "NUEVO-001" not in caplog.text


def test_auditoria_registra_resultado_de_generacion_de_reporte(
        caplog, monkeypatch, tmp_path):
    service = PatrimonioService()
    service.escaneados_sesion = [_crear_producto()]
    monkeypatch.setattr(
        service.generator,
        "generar_relevo",
        lambda **kwargs: True)

    with caplog.at_level(logging.INFO):
        resultado = service.generar_planilla_relevo(
            {}, str(tmp_path / "relevo.xlsx"))

    assert resultado is True
    assert "event=report_generated" in caplog.text
    assert "report_type': 'relevo'" in caplog.text
    assert "success': True" in caplog.text
