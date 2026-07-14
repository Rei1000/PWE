"""OpenAPI-Contract — Automatisierung (Gate 7.3f)."""

from api.app import create_app
from api.deps import in_memory_deps

AUTO_PATH = (
    "/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/automatisierung/ausfuehren"
)
LEGACY_PATH = (
    "/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/kommandos/{kommando_id}/ausfuehren"
)


def _openapi():
    app = create_app(in_memory_deps())
    return app.openapi()


def test_openapi_automatisierung_200_schema():
    spec = _openapi()
    post = spec["paths"][AUTO_PATH]["post"]
    assert post["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("AutomatisierungAusfuehrenResponse")


def test_openapi_automatisierung_fehler_schemas():
    spec = _openapi()
    post = spec["paths"][AUTO_PATH]["post"]
    for status in ("404", "409", "422"):
        schema = post["responses"][status]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("ErrorResponse")


def test_openapi_automatisierung_kein_409_ergebnis():
    spec = _openapi()
    post = spec["paths"][AUTO_PATH]["post"]
    assert "409" in post["responses"]
    ref = post["responses"]["409"]["content"]["application/json"]["schema"]["$ref"]
    assert ref.endswith("ErrorResponse")
    assert "AutomatisierungAusfuehrenResponse" not in str(post["responses"]["409"])


def test_openapi_automatisierung_request_forbid_extra():
    spec = _openapi()
    post = spec["paths"][AUTO_PATH]["post"]
    schema_ref = post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema_name = schema_ref.split("/")[-1]
    request_schema = spec["components"]["schemas"][schema_name]
    assert request_schema.get("additionalProperties") is False


def test_openapi_legacy_endpunkt_deprecated():
    spec = _openapi()
    post = spec["paths"][LEGACY_PATH]["post"]
    assert post["deprecated"] is True
    assert "automatisierung/ausfuehren" in post["description"]


def test_openapi_ergebnis_schema_felder():
    spec = _openapi()
    schema = spec["components"]["schemas"]["AutomatisierungAusfuehrenResponse"]
    required = set(schema["required"])
    assert {
        "ausfuehrung_id",
        "fehlgeschlagen",
        "ausgefuehrte_aktionen",
        "abgebrochen_bei_aktion_position",
        "fehlerart",
        "nachweise",
    } <= required
