"""Referenzprüfung — Bibliotheksobjekte in offenen Entwürfen und Routinen."""

from __future__ import annotations

from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


def ist_kommando_in_verwendung(
    katalog: KatalogRepository,
    bibliothek: BibliothekRepository,
    kommando_id: str,
) -> bool:
    for entwurf in katalog.list_entwuerfe():
        for schritt in entwurf.prozedur_schritte:
            if schritt.kommando_id == kommando_id:
                return True
    for routine in bibliothek.list_routinen():
        for aktion in routine.aktionen:
            if aktion.kommando_id == kommando_id:
                return True
    return False


def ist_routine_in_verwendung(
    katalog: KatalogRepository,
    routine_id: str,
) -> bool:
    for entwurf in katalog.list_entwuerfe():
        for schritt in entwurf.prozedur_schritte:
            if schritt.routine_id == routine_id:
                return True
    return False


def ist_vorlage_in_verwendung(
    katalog: KatalogRepository,
    vorlage_id: str,
) -> bool:
    for entwurf in katalog.list_entwuerfe():
        for schritt in entwurf.prozedur_schritte:
            if schritt.vorlage_id == vorlage_id:
                return True
    return False
