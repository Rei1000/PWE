"""API-Tests — stabiles Fehlerformat {detail, code}."""

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.deps import in_memory_deps


@pytest.fixture
def client():
    app = create_app(in_memory_deps())
    with TestClient(app) as http_client:
        yield http_client


def test_domain_fehler_hat_code(client: TestClient):
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "UNKNOWN",
            "pruefobjekt_kennung": "GER-1",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 404
    body = response.json()
    assert body == {"detail": body["detail"], "code": "version_nicht_gefunden"}
    assert isinstance(body["detail"], str)


def test_validierungsfehler_hat_code(client: TestClient):
    response = client.post("/prueflaeufe", json={"produktkodierung": "123"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation"
    assert body["detail"] == "Validierungsfehler"
