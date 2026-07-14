"""OpenAPI-Contract — Katalog-Setup Automatisierung (Gate 6.3a)."""

from api.app import create_app
from api.deps import in_memory_deps

KOMMANDO_PATH = "/katalog/bibliothek/kommandos"
AUTO_PATH = (
    "/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}/automatisierung"
)


def _openapi():
    return create_app(in_memory_deps()).openapi()


def test_openapi_kommando_anlegen_201_schema():
    spec = _openapi()
    post = spec["paths"][KOMMANDO_PATH]["post"]
    assert post["responses"]["201"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("ExternesKommandoAnlegenResponse")


def test_openapi_kommando_request_forbid_extra():
    spec = _openapi()
    post = spec["paths"][KOMMANDO_PATH]["post"]
    schema_ref = post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema_name = schema_ref.split("/")[-1]
    assert spec["components"]["schemas"][schema_name].get("additionalProperties") is False


def test_openapi_kommando_response_ohne_kommandocode():
    spec = _openapi()
    schema = spec["components"]["schemas"]["ExternesKommandoAnlegenResponse"]
    props = set(schema.get("properties", {}))
    assert "kommando_id" in props
    assert "bezeichnung" in props
    assert "kommandocode" not in props


def test_openapi_automatisierung_zuweisen_schemas():
    spec = _openapi()
    put = spec["paths"][AUTO_PATH]["put"]
    req_ref = put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    req_name = req_ref.split("/")[-1]
    req_schema = spec["components"]["schemas"][req_name]
    assert set(req_schema["required"]) == {"kommando_id"}
    assert "routine_id" not in req_schema.get("properties", {})
    assert req_schema.get("additionalProperties") is False
    assert put["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("AutomatisierungZuweisenResponse")
    for status in ("404", "409", "422"):
        ref = put["responses"][status]["content"]["application/json"]["schema"]["$ref"]
        assert ref.endswith("ErrorResponse")
