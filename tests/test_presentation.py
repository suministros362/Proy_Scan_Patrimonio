from ui.presentation import SectorRowPresenter


def test_estilo_fila_conserva_paleta_clara_y_paridad():
    presenter = SectorRowPresenter()

    tag_impar, fondo_impar, texto = presenter.estilo_fila(
        "Administración", False, False)
    tag_par, fondo_par, _ = presenter.estilo_fila(
        "Administración", True, False)

    assert fondo_impar == "#E6F3FF"
    assert fondo_par == "#D0E7FF"
    assert texto == "#1F2937"
    assert tag_impar != tag_par


def test_estilo_fila_conserva_paleta_oscura():
    presenter = SectorRowPresenter()

    _, fondo, texto = presenter.estilo_fila("Administración", False, True)

    assert fondo == "#1A365D"
    assert texto == "#FFFFFF"


def test_presentador_detecta_tema_oscuro():
    presenter = SectorRowPresenter()

    assert presenter.es_modo_oscuro("one-dark") is True
    assert presenter.es_modo_oscuro("bootstrap-light") is False


def test_limpiar_reinicia_asignacion_de_colores():
    presenter = SectorRowPresenter()
    presenter.estilo_fila("Contabilidad", False, False)

    presenter.clear()
    _, fondo, _ = presenter.estilo_fila("Administración", False, False)

    assert fondo == "#E6F3FF"
