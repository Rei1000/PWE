"""Tests — scripts/seed_demo_automatisierung.py (HTTP-Client, Gate 6.3c)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[3] / "scripts" / "seed_demo_automatisierung.py"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("seed_demo_automatisierung", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_hat_keine_backend_imports():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "from domain" not in source
    assert "from application" not in source
    assert "from adapters" not in source
    assert "from ports" not in source
    assert "sqlalchemy" not in source.lower()
    assert "create_engine" not in source


def test_seed_erfolgreiche_sequenz():
    mod = _load_script()
    responses = [
        (201, {"kommando_id": "k1", "bezeichnung": "Demo Messwert"}),
        (201, {"produktdefinition_id": "pd1", "produktkodierung": "9000000001"}),
        (200, {"produktdefinition_id": "pd1", "schritt_id": "demo-schritt-1", "kommando_id": "k1"}),
        (201, {"version_id": "v1", "produktdefinition_id": "pd1", "produktkodierung": "9000000001"}),
        (
            201,
            {
                "prueflauf_id": "p1",
                "version_id": "v1",
                "produktkodierung": "9000000001",
                "pruefobjekt_kennung": "DEMO-OBJ-1",
                "pruefer_id": "demo-pruefer",
                "status": "gestartet",
            },
        ),
    ]
    call_count = {"n": 0}

    def fake_request(method, url, *, body=None):
        idx = call_count["n"]
        call_count["n"] += 1
        return responses[idx]

    with patch.object(mod, "_request", side_effect=fake_request):
        result = mod.seed_demo(api_base="http://example.test", start_prueflauf=True)

    assert call_count["n"] == 5
    assert result["kommando_id"] == "k1"
    assert result["prueflauf_id"] == "p1"
    assert result["frontend_pfad"] == "/prueflaeufe/p1"


def test_seed_stoppt_nach_fehlgeschlagenem_schritt():
    mod = _load_script()
    call_count = {"n": 0}

    def fake_request(method, url, *, body=None):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return 201, {"kommando_id": "k1", "bezeichnung": "Demo Messwert"}
        raise mod.SeedStepError(
            "http",
            "HTTP 409: Konflikt",
            status=409,
            code="automatisierung_doppelt_zugewiesen",
        )

    with patch.object(mod, "_request", side_effect=fake_request):
        with pytest.raises(mod.SeedStepError) as exc_info:
            mod.seed_demo(api_base="http://example.test")

    assert call_count["n"] == 2
    assert exc_info.value.step == "Entwurf anlegen"
    assert "409" in str(exc_info.value)


def test_main_exit_code_bei_fehler(capsys):
    mod = _load_script()

    def failing_seed(**kwargs):
        raise mod.SeedStepError("Veröffentlichen", "HTTP 500: boom", status=500, code="x")

    with patch.object(mod, "seed_demo", side_effect=failing_seed):
        code = mod.main(["--api-base", "http://example.test"])
    assert code == 1
    err = capsys.readouterr().err
    assert "Veröffentlichen: fehlgeschlagen" in err
