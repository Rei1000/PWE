"""OpenAPI-Contract — Bibliothek CRUD (Gate 8.2a)."""

from api.app import create_app
from api.deps import in_memory_deps

KOMMANDO_COLLECTION = "/katalog/bibliothek/kommandos"
KOMMANDO_ITEM = "/katalog/bibliothek/kommandos/{kommando_id}"
ROUTINE_COLLECTION = "/katalog/bibliothek/routinen"
ROUTINE_ITEM = "/katalog/bibliothek/routinen/{routine_id}"


def _openapi():
    return create_app(in_memory_deps()).openapi()


def test_openapi_kommando_liste_und_detail():
    spec = _openapi()
    assert "get" in spec["paths"][KOMMANDO_COLLECTION]
    assert "get" in spec["paths"][KOMMANDO_ITEM]
    assert "put" in spec["paths"][KOMMANDO_ITEM]
    assert "delete" in spec["paths"][KOMMANDO_ITEM]

    list_schema = spec["components"]["schemas"]["ExternesKommandoListenEintragResponse"]
    assert "kommandocode" not in list_schema.get("properties", {})

    detail_schema = spec["components"]["schemas"]["ExternesKommandoDetailResponse"]
    assert "kommandocode" in detail_schema.get("properties", {})


def test_openapi_routine_endpunkte():
    spec = _openapi()
    post = spec["paths"][ROUTINE_COLLECTION]["post"]
    req_ref = post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    req_name = req_ref.split("/")[-1]
    assert spec["components"]["schemas"][req_name].get("additionalProperties") is False

    put = spec["paths"][ROUTINE_ITEM]["put"]
    put_ref = put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    put_name = put_ref.split("/")[-1]
    assert spec["components"]["schemas"][put_name].get("additionalProperties") is False


def test_openapi_kommando_update_forbid_extra():
    spec = _openapi()
    put = spec["paths"][KOMMANDO_ITEM]["put"]
    ref = put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    name = ref.split("/")[-1]
    assert spec["components"]["schemas"][name].get("additionalProperties") is False


def test_openapi_automatisierung_erweitert_optional():
    spec = _openapi()
    path = "/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}/automatisierung"
    put = spec["paths"][path]["put"]
    ref = put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    name = ref.split("/")[-1]
    schema = spec["components"]["schemas"][name]
    props = schema.get("properties", {})
    assert "kommando_id" in props
    assert "routine_id" in props
    assert schema.get("additionalProperties") is False
from tests.support.auth import login_as_admin
