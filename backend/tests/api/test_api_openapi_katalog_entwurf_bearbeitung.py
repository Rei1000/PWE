"""OpenAPI-Contract — Entwurfsbearbeitung (Gate 8.2b2)."""

from api.app import create_app
from api.deps import in_memory_deps

ENTWURF_ITEM = "/katalog/entwuerfe/{produktdefinition_id}"
SCHRITT_COLLECTION = "/katalog/entwuerfe/{produktdefinition_id}/schritte"
SCHRITT_ITEM = "/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}"
REIHENFOLGE = "/katalog/entwuerfe/{produktdefinition_id}/schritte/reihenfolge"


def _openapi():
    return create_app(in_memory_deps()).openapi()


def test_openapi_entwurf_endpunkte_vorhanden():
    spec = _openapi()
    assert "get" in spec["paths"][ENTWURF_ITEM]
    assert "post" in spec["paths"][SCHRITT_COLLECTION]
    assert "put" in spec["paths"][SCHRITT_ITEM]
    assert "delete" in spec["paths"][SCHRITT_ITEM]
    assert "put" in spec["paths"][REIHENFOLGE]


def test_openapi_schritt_write_forbid_extra():
    spec = _openapi()
    for path in (SCHRITT_COLLECTION, SCHRITT_ITEM, REIHENFOLGE):
        method = "post" if path == SCHRITT_COLLECTION else "put"
        op = spec["paths"][path][method]
        ref = op["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        name = ref.split("/")[-1]
        assert spec["components"]["schemas"][name].get("additionalProperties") is False


def test_openapi_schritt_aktualisieren_ohne_automatisierung():
    spec = _openapi()
    put = spec["paths"][SCHRITT_ITEM]["put"]
    ref = put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    name = ref.split("/")[-1]
    props = spec["components"]["schemas"][name].get("properties", {})
    assert "kommando_id" not in props
    assert "routine_id" not in props
