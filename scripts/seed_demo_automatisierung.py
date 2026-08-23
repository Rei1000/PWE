#!/usr/bin/env python3
"""Gate 6.3c — Demo-Seed über öffentliche HTTP-API (externer Client).

Orchestriert ausschließlich öffentliche Endpunkte. Keine Repository-/Application-/DB-Imports.

Voraussetzung: API läuft mit PWE_DEMO_MODE=true und EXTERNES_KOMMANDO_ADAPTER=simulation
(oder Default simulation), damit DEMO_MESSWERT eine deterministische Antwort liefert.

Nicht idempotent: jeder Lauf erzeugt neue Katalogobjekte und eine neue aktive Version
für die Demo-Produktkodierung (bestehende Daten werden nicht gelöscht).

Gate 8.2: Dieses Script ersetzt keine Katalog-Administration.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

# Demo-Datensatz (engine-generisch) — muss mit Backend-Demo-Sim (DEMO_MESSWERT) übereinstimmen.
DEMO_PRODUKTKODIERUNG = "9000000001"
DEMO_SCHRITT_ID = "demo-schritt-1"
DEMO_VORLAGE_ID = "demo-vorlage-1"
DEMO_KOMMANDO_BEZEICHNUNG = "Demo Messwert"
DEMO_KOMMANDOCODE = "DEMO_MESSWERT"
DEMO_SOLLBESTUECKUNG = ["komponente-a"]
DEMO_SOLLVORGABEN = {"messwert": {"min": 1, "max": 100}}
DEMO_PRUEFOBJEKT = "DEMO-OBJ-1"
DEFAULT_API_BASE = "http://127.0.0.1:8000"


class SeedStepError(Exception):
    def __init__(self, step: str, message: str, *, status: int | None = None, code: str | None = None):
        super().__init__(message)
        self.step = step
        self.status = status
        self.code = code


_COOKIE_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_COOKIE_JAR))
_CSRF_TOKEN: str | None = None


def _request(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    global _CSRF_TOKEN
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if method.upper() not in {"GET", "HEAD", "OPTIONS"} and _CSRF_TOKEN:
        headers["X-CSRF-Token"] = _CSRF_TOKEN
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with _OPENER.open(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            payload: Any = json.loads(raw) if raw else None
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"detail": raw or exc.reason}
        detail = payload.get("detail", str(exc.reason))
        code = payload.get("code")
        raise SeedStepError(
            "http",
            f"HTTP {exc.code}: {detail}",
            status=exc.code,
            code=code if isinstance(code, str) else None,
        ) from exc
    except urllib.error.URLError as exc:
        raise SeedStepError("http", f"Verbindung fehlgeschlagen: {exc.reason}") from exc


def _step(name: str, method: str, url: str, body: dict[str, Any] | None = None) -> Any:
    try:
        status, payload = _request(method, url, body=body)
    except SeedStepError as exc:
        raise SeedStepError(
            name,
            str(exc),
            status=exc.status,
            code=exc.code,
        ) from exc
    if status >= 400:
        raise SeedStepError(name, f"Unerwarteter Status {status}", status=status)
    print(f"{name}: ok (HTTP {status})")
    return payload


def seed_demo(*, api_base: str, start_prueflauf: bool = True) -> dict[str, str]:
    global _CSRF_TOKEN
    base = api_base.rstrip("/")
    login = os.environ.get("PWE_SEED_ADMIN_LOGIN", "admin")
    password = os.environ.get("PWE_SEED_ADMIN_PASSWORD", "admin-change-me")
    login_resp = _step(
        "Login",
        "POST",
        f"{base}/auth/login",
        {"login": login, "passwort": password},
    )
    _CSRF_TOKEN = login_resp.get("csrf_token")

    kommando = _step(
        "Kommando anlegen",
        "POST",
        f"{base}/katalog/bibliothek/kommandos",
        {"bezeichnung": DEMO_KOMMANDO_BEZEICHNUNG, "kommandocode": DEMO_KOMMANDOCODE},
    )
    kommando_id = kommando["kommando_id"]

    entwurf = _step(
        "Entwurf anlegen",
        "POST",
        f"{base}/katalog/entwuerfe",
        {
            "produktkodierung": DEMO_PRODUKTKODIERUNG,
            "prozedur_schritte": [
                {
                    "schritt_id": DEMO_SCHRITT_ID,
                    "vorlage_id": DEMO_VORLAGE_ID,
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "sollvorgaben": DEMO_SOLLVORGABEN,
                }
            ],
            "sollbestueckung": DEMO_SOLLBESTUECKUNG,
        },
    )
    produktdefinition_id = entwurf["produktdefinition_id"]

    _step(
        "Automatisierung zuweisen",
        "PUT",
        f"{base}/katalog/entwuerfe/{produktdefinition_id}/schritte/{DEMO_SCHRITT_ID}/automatisierung",
        {"kommando_id": kommando_id},
    )

    version = _step(
        "Veröffentlichen",
        "POST",
        f"{base}/katalog/entwuerfe/{produktdefinition_id}/veroeffentlichen",
    )
    version_id = version["version_id"]

    result = {
        "produktdefinition_id": produktdefinition_id,
        "kommando_id": kommando_id,
        "version_id": version_id,
        "produktkodierung": DEMO_PRODUKTKODIERUNG,
        "schritt_id": DEMO_SCHRITT_ID,
    }

    if start_prueflauf:
        prueflauf = _step(
            "Prüflauf starten",
            "POST",
            f"{base}/prueflaeufe",
            {
                "produktkodierung": DEMO_PRODUKTKODIERUNG,
                "pruefobjekt_kennung": DEMO_PRUEFOBJEKT,
            },
        )
        prueflauf_id = prueflauf["prueflauf_id"]
        result["prueflauf_id"] = prueflauf_id
        result["frontend_pfad"] = f"/prueflaeufe/{prueflauf_id}"

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PWE Gate 6.3c — Demo-Seed (öffentliche HTTP-API, nicht idempotent)."
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help=f"API-Basis-URL (Default: {DEFAULT_API_BASE})",
    )
    parser.add_argument(
        "--ohne-prueflauf",
        action="store_true",
        help="Nur Katalog seeden, keinen Prüflauf starten",
    )
    args = parser.parse_args(argv)

    print("PWE Demo-Seed (Gate 6.3c)")
    print(f"API: {args.api_base}")
    print("Hinweis: API muss mit PWE_DEMO_MODE=true (Simulation) laufen.")
    print("Nicht idempotent — jeder Lauf erzeugt neue Katalogobjekte.")
    print()

    try:
        result = seed_demo(api_base=args.api_base, start_prueflauf=not args.ohne_prueflauf)
    except SeedStepError as exc:
        print(f"{exc.step}: fehlgeschlagen", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        if exc.code:
            print(f"code: {exc.code}", file=sys.stderr)
        return 1

    print()
    print("Ergebnis:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    if "frontend_pfad" in result:
        print()
        print(f"Frontend: http://localhost:5173{result['frontend_pfad']}")
        print("Nächste Schritte: Komponente 'komponente-a' erfassen, dann Automatisierung ausführen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
