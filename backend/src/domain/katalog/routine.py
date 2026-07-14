"""Katalog-Bibliothek — Routine (Domain Model §4.10)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

from domain.katalog.errors import LeereRoutine, UngueltigeAktionsreihenfolge
from domain.katalog.externes_kommando import ExternesKommando, MaterialisiertesExternesKommando
from domain.shared.errors import InvariantViolation


class RoutineAktionsart(str, Enum):
    EXTERNES_KOMMANDO_AUSFUEHREN = "externes_kommando_ausfuehren"


class MaterialisierteRoutineHerkunft(str, Enum):
    BIBLIOTHEK = "bibliothek"
    EINZELKOMMANDO = "einzelkommando"


@dataclass(frozen=True)
class RoutineAktion:
    """Fachliche Aktion innerhalb einer Routine — Gate 7.3d: nur ExternesKommando."""

    aktionsart: RoutineAktionsart
    kommando_id: str
    position: int


@dataclass(frozen=True)
class Routine:
    """Aggregate Root — Bibliotheksmodul Katalog."""

    routine_id: str
    bezeichnung: str
    aktionen: tuple[RoutineAktion, ...]

    @classmethod
    def anlegen(
        cls,
        *,
        bezeichnung: str,
        aktionen: tuple[RoutineAktion, ...],
    ) -> Routine:
        bezeichnung = bezeichnung.strip()
        if not bezeichnung:
            raise InvariantViolation("Bezeichnung der Routine darf nicht leer sein")
        _validiere_aktionen(aktionen)
        return cls(
            routine_id=str(uuid4()),
            bezeichnung=bezeichnung,
            aktionen=aktionen,
        )


@dataclass(frozen=True)
class MaterialisierteKommandoAktion:
    """Materialisierte Kommando-Aktion in einer Routine."""

    position: int
    kommando_id: str
    bezeichnung: str
    kommandocode: str

    @classmethod
    def aus(
        cls,
        *,
        position: int,
        kommando: ExternesKommando,
    ) -> MaterialisierteKommandoAktion:
        return cls(
            position=position,
            kommando_id=kommando.kommando_id,
            bezeichnung=kommando.bezeichnung,
            kommandocode=kommando.kommandocode,
        )


@dataclass(frozen=True)
class MaterialisierteRoutine:
    """Unveränderlicher Automatisierungs-Snapshot in der ProduktdefinitionsVersion."""

    herkunft: MaterialisierteRoutineHerkunft
    bezeichnung: str
    aktionen: tuple[MaterialisierteKommandoAktion, ...]
    routine_id: str | None = None

    @classmethod
    def aus_bibliothek(
        cls,
        *,
        routine: Routine,
        kommandos: dict[str, ExternesKommando],
    ) -> MaterialisierteRoutine:
        return cls(
            herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
            routine_id=routine.routine_id,
            bezeichnung=routine.bezeichnung,
            aktionen=_materialisiere_aktionen(routine.aktionen, kommandos),
        )

    @classmethod
    def aus_einzelkommando(
        cls,
        *,
        kommando: ExternesKommando,
    ) -> MaterialisierteRoutine:
        aktion = MaterialisierteKommandoAktion.aus(position=1, kommando=kommando)
        return cls(
            herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
            routine_id=None,
            bezeichnung=kommando.bezeichnung,
            aktionen=(aktion,),
        )

    def erstes_kommando_snapshot(self) -> MaterialisiertesExternesKommando | None:
        """Erstes Kommando — für Gate-7.3b-Kompatibilität (deprecated Feld)."""
        if not self.aktionen:
            return None
        erste = self.aktionen[0]
        return MaterialisiertesExternesKommando(
            kommando_id=erste.kommando_id,
            bezeichnung=erste.bezeichnung,
            kommandocode=erste.kommandocode,
        )


def _validiere_aktionen(aktionen: tuple[RoutineAktion, ...]) -> None:
    if not aktionen:
        raise LeereRoutine("Routine erfordert mindestens eine Aktion")
    positionen = [a.position for a in aktionen]
    if len(set(positionen)) != len(positionen):
        raise UngueltigeAktionsreihenfolge("Aktionspositionen müssen eindeutig sein")
    erwartet = list(range(1, len(aktionen) + 1))
    if sorted(positionen) != erwartet:
        raise UngueltigeAktionsreihenfolge(
            f"Aktionspositionen müssen fortlaufend ab 1 sein, erwartet {erwartet}"
        )
    for aktion in aktionen:
        if aktion.aktionsart != RoutineAktionsart.EXTERNES_KOMMANDO_AUSFUEHREN:
            raise InvariantViolation(f"Unbekannte Aktionsart: {aktion.aktionsart}")


def _materialisiere_aktionen(
    aktionen: tuple[RoutineAktion, ...],
    kommandos: dict[str, ExternesKommando],
) -> tuple[MaterialisierteKommandoAktion, ...]:
    from domain.katalog.errors import KommandoInRoutineNichtGefunden

    materialisiert: list[MaterialisierteKommandoAktion] = []
    for aktion in sorted(aktionen, key=lambda a: a.position):
        kommando = kommandos.get(aktion.kommando_id)
        if kommando is None:
            raise KommandoInRoutineNichtGefunden(
                f"Kommando {aktion.kommando_id} in Routine nicht gefunden"
            )
        materialisiert.append(
            MaterialisierteKommandoAktion.aus(position=aktion.position, kommando=kommando)
        )
    return tuple(materialisiert)
