"""OpenAPI-Contract — Automatisierung (Gate 7.3f / Gate 7.4a API Exit)."""

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


def test_openapi_legacy_endpunkt_entfernt():
    """Gate 7.4a — Legacy-Pfad und Schemas dürfen nicht mehr in OpenAPI erscheinen."""
    spec = _openapi()
    assert LEGACY_PATH not in spec["paths"]
    schemas = spec["components"]["schemas"]
    assert "ExternesKommandoAusfuehrenRequest" not in schemas
    assert "ExternesKommandoAusfuehrenResponse" not in schemas
    for path in spec["paths"]:
        post = spec["paths"][path].get("post")
        if post is None:
            continue
        assert post.get("deprecated") is not True


def test_openapi_zielendpoint_adr0016_unverändert():
    spec = _openapi()
    assert AUTO_PATH in spec["paths"]
    post = spec["paths"][AUTO_PATH]["post"]
    assert post["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("AutomatisierungAusfuehrenResponse")
    for status in ("404", "409", "422"):
        assert (
            post["responses"][status]["content"]["application/json"]["schema"]["$ref"].endswith(
                "ErrorResponse"
            )
        )


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
