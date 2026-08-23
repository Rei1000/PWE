"""HTTP-DTOs — nur Transport, keine Domain-Logik."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PrueflaufStartenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    produktkodierung: str
    pruefobjekt_kennung: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str
    passwort: str


class LoginResponse(BaseModel):
    benutzer_id: str
    login: str
    anzeigename: str
    rollen: list[str]
    csrf_token: str


class MeResponse(BaseModel):
    benutzer_id: str
    login: str
    anzeigename: str
    status: str
    rollen: list[str]
    passwortwechsel_erforderlich: bool = False


class PasswortAendernRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    altes_passwort: str
    neues_passwort: str


class BenutzerAnlegenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str
    anzeigename: str
    passwort: str
    rollen: list[str]


class BenutzerRollenSetzenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rollen: list[str]


class PasswortResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    neues_passwort: str


class BenutzerResponse(BaseModel):
    benutzer_id: str
    login: str
    anzeigename: str
    status: str
    rollen: list[str]
    passwortwechsel_erforderlich: bool


class BenutzerListeResponse(BaseModel):
    benutzer: list[BenutzerResponse]


class AuditEintragResponse(BaseModel):
    audit_id: str
    akteur_benutzer_id: str
    ziel_benutzer_id: str | None = None
    aktion: str
    zeitpunkt: datetime
    referenz_id: str | None = None
    details: dict[str, Any]


class AuditListeResponse(BaseModel):
    eintraege: list[AuditEintragResponse]


class PrueflaufResponse(BaseModel):
    prueflauf_id: str
    version_id: str
    produktkodierung: str
    pruefobjekt_kennung: str
    pruefer_id: str
    status: str


class KomponenteErfassenRequest(BaseModel):
    komponenten_typ: str
    seriennummer: str


class NachweisArtEnum(str, Enum):
    """Transport-Enum — Werte sind der öffentliche API-Contract (lowercase snake_case)."""

    MESSWERT = "messwert"
    FOTO = "foto"
    KOMMENTAR = "kommentar"
    MANUELLE_EINGABE = "manuelle_eingabe"
    ROHANTWORT = "rohantwort"
    EXTRAHIERTER_WERT = "extrahierter_wert"
    ERGAENZUNG = "ergaenzung"
    KOMPONENTENERFASSUNG = "komponentenerfassung"


NACHWEIS_ART_API_WERTE: tuple[str, ...] = tuple(member.value for member in NachweisArtEnum)


class NachweisErfassenRequest(BaseModel):
    art: NachweisArtEnum
    payload: dict[str, Any] = Field(default_factory=dict)
    ist_automatisch: bool = False


class NachweisResponse(BaseModel):
    nachweis_id: str
    art: str


class FotoNachweisResponse(BaseModel):
    nachweis_id: str
    art: str
    datei_id: str
    mime_type: str
    groesse_bytes: int
    dateiname: str | None = None


class ErrorResponse(BaseModel):
    """Einheitliches API-Fehlerformat — vor Ausführungsbeginn."""

    detail: str
    code: str


class AutomatisierungFehlerartEnum(str, Enum):
    KEINE_GERAETEANTWORT = "keine_geraeteantwort"
    GERAETEFEHLSCHLAG = "geraetefehlschlag"
    UNGUELTIGE_ANTWORT = "ungueltige_antwort"


class AutomatisierungAusfuehrenRequest(BaseModel):
    """Leerer Body — unbekannte Felder werden abgelehnt (Gate 7.3f)."""

    model_config = ConfigDict(extra="forbid")


class AutomatisierungAusfuehrenResponse(BaseModel):
    ausfuehrung_id: str
    fehlgeschlagen: bool
    ausgefuehrte_aktionen: int
    abgebrochen_bei_aktion_position: int | None
    fehlerart: AutomatisierungFehlerartEnum | None
    nachweise: list[NachweisResponse]


class AbschlussResponse(BaseModel):
    prueflauf_id: str
    status: str
    ist_gueltig: bool
    snapshot_id: str


class ProzedurSchrittEntwurfRequest(BaseModel):
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any] = Field(default_factory=dict)


class EntwurfAnlegenRequest(BaseModel):
    produktkodierung: str
    prozedur_schritte: list[ProzedurSchrittEntwurfRequest]
    sollbestueckung: list[str] = Field(default_factory=list)
    basisprodukt_sollvorgaben: dict[str, Any] = Field(default_factory=dict)
    kundenprofil_sollvorgaben: dict[str, Any] = Field(default_factory=dict)
    definition_sollvorgaben: dict[str, Any] = Field(default_factory=dict)


class EntwurfResponse(BaseModel):
    produktdefinition_id: str
    produktkodierung: str


class ProzedurSchrittEntwurfResponse(BaseModel):
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any] = Field(default_factory=dict)
    kommando_id: str | None = None
    routine_id: str | None = None


class EntwurfDetailResponse(BaseModel):
    produktdefinition_id: str
    produktkodierung: str
    sollbestueckung: list[str] = Field(default_factory=list)
    prozedur_schritte: list[ProzedurSchrittEntwurfResponse] = Field(default_factory=list)


class ProzedurSchrittAnlegenRequest(BaseModel):
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    sollvorgaben: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class ProzedurSchrittAktualisierenRequest(BaseModel):
    vorlage_id: str
    ist_pflicht: bool
    sollvorgaben: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class ProzedurSchrittReihenfolgeRequest(BaseModel):
    schritt_ids: list[str]

    model_config = ConfigDict(extra="forbid")


class VersionResponse(BaseModel):
    version_id: str
    produktdefinition_id: str
    produktkodierung: str


class ExternesKommandoAnlegenRequest(BaseModel):
    """Bibliothek — Externes Kommando anlegen (Gate 6.3a)."""

    bezeichnung: str
    kommandocode: str

    model_config = ConfigDict(extra="forbid")


class ExternesKommandoAnlegenResponse(BaseModel):
    """Schmaler Setup-Response — ohne kommandocode (Ausführung aus Materialisierung)."""

    kommando_id: str
    bezeichnung: str


class AutomatisierungZuweisenRequest(BaseModel):
    """Automatisierung an Entwurfsschritt — Gate 6.3a + 8.2a."""

    kommando_id: str | None = None
    routine_id: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_zuweisung(self) -> AutomatisierungZuweisenRequest:
        if self.kommando_id is not None and self.routine_id is not None:
            raise ValueError("kommando_id und routine_id sind gegenseitig exklusiv")
        fields_set = self.model_fields_set
        if self.kommando_id is None and self.routine_id is None:
            if "kommando_id" in fields_set and "routine_id" in fields_set:
                return self
            raise ValueError(
                "Entweder kommando_id, routine_id oder beide null für Entfernen angeben"
            )
        return self


class AutomatisierungZuweisenResponse(BaseModel):
    produktdefinition_id: str
    schritt_id: str
    kommando_id: str | None
    routine_id: str | None


class NachweisDetailResponse(BaseModel):
    nachweis_id: str
    art: str
    erfasst_am: datetime
    payload: dict[str, Any]
    ist_automatisch: bool


class BeurteilungResponse(BaseModel):
    ergebnis: str
    festgelegt_am: datetime
    kommentar: str | None = None


class SchrittDurchfuehrungResponse(BaseModel):
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any]
    nachweise: list[NachweisDetailResponse]
    beurteilung: BeurteilungResponse | None = None
    kann_nachweis_erfassen: bool = False
    kann_beurteilt_werden: bool = False
    hat_automatisierung: bool = False
    kann_automatisierung_ausfuehren: bool = False
    automatisierung_bezeichnung: str | None = None


class PrueflaufDetailResponse(BaseModel):
    prueflauf_id: str
    version_id: str
    produktkodierung: str
    pruefobjekt_kennung: str
    pruefer_id: str
    status: str
    gestartet_am: datetime
    abgeschlossen_am: datetime | None = None
    schritte: list[SchrittDurchfuehrungResponse]
    sollbestueckung: list[str]
    erfasste_komponenten: list[str]
    ist_abgeschlossen: bool = False
    fehlende_komponenten: list[str] = Field(default_factory=list)
    kann_komponente_erfassen: bool = False
    kann_abgeschlossen_werden: bool = False


class ExternesKommandoListenEintragResponse(BaseModel):
    kommando_id: str
    bezeichnung: str


class ExternesKommandoListeResponse(BaseModel):
    kommandos: list[ExternesKommandoListenEintragResponse]


class ExternesKommandoDetailResponse(BaseModel):
    kommando_id: str
    bezeichnung: str
    kommandocode: str


class ExternesKommandoAktualisierenRequest(BaseModel):
    bezeichnung: str
    kommandocode: str

    model_config = ConfigDict(extra="forbid")


class RoutineAnlegenRequest(BaseModel):
    bezeichnung: str
    kommando_ids: list[str]

    model_config = ConfigDict(extra="forbid")


class RoutineAktionResponse(BaseModel):
    position: int
    kommando_id: str


class RoutineListenEintragResponse(BaseModel):
    routine_id: str
    bezeichnung: str
    anzahl_aktionen: int


class RoutineListeResponse(BaseModel):
    routinen: list[RoutineListenEintragResponse]


class RoutineDetailResponse(BaseModel):
    routine_id: str
    bezeichnung: str
    aktionen: list[RoutineAktionResponse]


class RoutineAnlegenResponse(BaseModel):
    routine_id: str
    bezeichnung: str
    aktionen: list[RoutineAktionResponse]


class RoutineAktualisierenRequest(BaseModel):
    bezeichnung: str
    kommando_ids: list[str]

    model_config = ConfigDict(extra="forbid")


class PruefschrittVorlageAnlegenRequest(BaseModel):
    bezeichnung: str
    beschreibung: str | None = None

    model_config = ConfigDict(extra="forbid")


class PruefschrittVorlageAnlegenResponse(BaseModel):
    vorlage_id: str
    bezeichnung: str


class PruefschrittVorlageListenEintragResponse(BaseModel):
    vorlage_id: str
    bezeichnung: str


class PruefschrittVorlageListeResponse(BaseModel):
    vorlagen: list[PruefschrittVorlageListenEintragResponse]


class PruefschrittVorlageDetailResponse(BaseModel):
    vorlage_id: str
    bezeichnung: str
    beschreibung: str | None = None


class PruefschrittVorlageAktualisierenRequest(BaseModel):
    bezeichnung: str
    beschreibung: str | None = None

    model_config = ConfigDict(extra="forbid")


class VeroeffentlichenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    einweisung_uebernehmen: bool = False


class ProfilAnlegenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bezeichnung: str
    beschreibung: str | None = None
    produktdefinition_ids: list[str] | None = None


class ProfilAktualisierenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bezeichnung: str
    beschreibung: str | None = None
    produktdefinition_ids: list[str] | None = None


class ProfilResponse(BaseModel):
    profil_id: str
    bezeichnung: str
    beschreibung: str | None = None
    produktdefinition_ids: list[str]
    aktiv: bool = True


class EinweisungAnlegenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    benutzer_id: str
    version_id: str
    gueltig_bis: str | None = None  # ISO date
    bemerkung: str | None = None


class EinweisungResponse(BaseModel):
    einweisung_id: str
    benutzer_id: str
    version_id: str
    eingewiesen_durch: str
    datum: datetime
    status: str
    gueltig_bis: str | None = None
    bemerkung: str | None = None
    herkunft_einweisung_id: str | None = None
    uebernommen_bei_publish: bool = False
