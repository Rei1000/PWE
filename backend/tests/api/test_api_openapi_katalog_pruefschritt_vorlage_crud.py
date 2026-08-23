"""OpenAPI-Contract — PrüfschrittVorlage CRUD (Gate 8.2b1)."""

from api.app import create_app
from api.deps import in_memory_deps

VORLAGE_COLLECTION = "/katalog/bibliothek/vorlagen"
VORLAGE_ITEM = "/katalog/bibliothek/vorlagen/{vorlage_id}"


def _openapi():
    return create_app(in_memory_deps()).openapi()


def test_openapi_vorlage_endpunkte():
    spec = _openapi()
    assert "post" in spec["paths"][VORLAGE_COLLECTION]
    assert "get" in spec["paths"][VORLAGE_COLLECTION]
    assert "get" in spec["paths"][VORLAGE_ITEM]
    assert "put" in spec["paths"][VORLAGE_ITEM]
    assert "delete" in spec["paths"][VORLAGE_ITEM]


def test_openapi_vorlage_write_forbid_extra():
    spec = _openapi()
    post = spec["paths"][VORLAGE_COLLECTION]["post"]
    req_ref = post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    req_name = req_ref.split("/")[-1]
    assert spec["components"]["schemas"][req_name].get("additionalProperties") is False

    put = spec["paths"][VORLAGE_ITEM]["put"]
    put_ref = put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    put_name = put_ref.split("/")[-1]
    assert spec["components"]["schemas"][put_name].get("additionalProperties") is False


def test_openapi_vorlage_listen_ohne_beschreibung():
    spec = _openapi()
    list_schema = spec["components"]["schemas"]["PruefschrittVorlageListenEintragResponse"]
    assert "beschreibung" not in list_schema.get("properties", {})


def test_openapi_vorlage_detail_mit_beschreibung():
    spec = _openapi()
    detail_schema = spec["components"]["schemas"]["PruefschrittVorlageDetailResponse"]
    assert "beschreibung" in detail_schema.get("properties", {})
