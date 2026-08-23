"""HTTP-Fehlerabbildung — stabile Codes und öffentliche Meldungen."""

from __future__ import annotations

import re

from domain.shared.errors import DomainError, InvariantViolation


def domain_error_code(exc: DomainError) -> str:
    if isinstance(exc, InvariantViolation):
        return "invariant_verletzt"
    name = type(exc).__name__
    if name == "DomainError":
        return "domain"
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def http_status_for_domain_error(exc: DomainError) -> int:
    if isinstance(exc, InvariantViolation):
        return 409
    name = type(exc).__name__
    if name in {"UngueltigeAnmeldedaten", "NichtAuthentifiziert", "SessionAbgelaufen", "LoginNichtErlaubt"}:
        return 401
    if name in {
        "QualifikationUnzureichend",
        "NichtBerechtigt",
        "PrueflaufNichtEigentuemer",
    }:
        return 403
    if name == "UngueltigerDateityp":
        return 415
    if name == "DateiZuGross":
        return 413
    if name == "DateiSpeicherungFehlgeschlagen":
        return 503
    if name == "EinweisungBereitsGueltig":
        return 409
    if name.endswith("NichtGefunden") or name == "NachweisKeinFoto":
        return 404
    return 409


def oeffentliche_fehlermeldung(exc: DomainError) -> str:
    if isinstance(exc, InvariantViolation):
        return "Die Aktion ist im aktuellen Zustand nicht zulässig."
    name = type(exc).__name__
    if name in {"UngueltigeAnmeldedaten", "LoginNichtErlaubt"}:
        return "Anmeldung fehlgeschlagen."
    if name in {"NichtAuthentifiziert", "SessionAbgelaufen"}:
        return "Nicht angemeldet."
    if name == "QualifikationUnzureichend":
        return "Qualifikation unzureichend."
    if name in {"NichtBerechtigt", "PrueflaufNichtEigentuemer"}:
        return "Keine Berechtigung für diese Aktion."
    if name == "EinweisungBereitsGueltig":
        return "Es existiert bereits eine gültige Einweisung."
    if name == "PrueflaufNichtGefunden":
        return "Der angeforderte Prüflauf wurde nicht gefunden."
    if name == "VersionNichtGefunden":
        return "Die referenzierte Produktdefinitionsversion wurde nicht gefunden."
    if name == "VersionNichtAufloesbar":
        return "Die Produktdefinitionsversion des Prüflaufs ist nicht verfügbar."
    if name == "KommandoInVerwendung":
        return "Das externe Kommando wird noch referenziert und kann nicht gelöscht werden."
    if name == "RoutineInVerwendung":
        return "Die Routine wird noch referenziert und kann nicht gelöscht werden."
    if name == "VorlageInVerwendung":
        return "Die PrüfschrittVorlage wird noch referenziert und kann nicht gelöscht werden."
    if name == "FotoNurPerMultipart":
        return "Foto-Nachweise werden ausschließlich über den Multipart-Endpunkt erfasst."
    if name == "UngueltigerDateityp":
        return "Der Dateityp wird nicht unterstützt."
    if name == "DateiZuGross":
        return "Die Datei ist zu groß."
    if name == "DateiSpeicherungFehlgeschlagen":
        return "Die Datei konnte nicht gespeichert werden."
    if name == "NachweisKeinFoto":
        return "Der Nachweis ist kein Foto-Nachweis."
    if name.endswith("NichtGefunden"):
        return "Die angeforderte Ressource wurde nicht gefunden."
    return "Die Anfrage konnte aus fachlichen Gründen nicht verarbeitet werden."


def fehler_response(*, detail: str, code: str) -> dict[str, str]:
    return {"detail": detail, "code": code}
