"""HTTP-Routen — Prüflauf (delegiert an Application-Use-Cases)."""

from __future__ import annotations

from fastapi import APIRouter, Body, File, Request, UploadFile
from fastapi.responses import Response
from urllib.parse import quote

from api.automatisierung_beobachtung import (
    beobachte_ausgefuehrte_automatisierung,
    beobachte_automatisierung_nicht_begonnen,
)
from api.automatisierung_response import automatisierung_ausfuehren_response
from api.current_user import RequestCurrentUserProvider
from api.deps import get_request_deps
from api.schemas import (
    AbschlussResponse,
    AutomatisierungAusfuehrenRequest,
    AutomatisierungAusfuehrenResponse,
    BeurteilungResponse,
    ErrorResponse,
    FotoNachweisResponse,
    KomponenteErfassenRequest,
    NachweisDetailResponse,
    NachweisErfassenRequest,
    NachweisResponse,
    PrueflaufDetailResponse,
    PrueflaufResponse,
    PrueflaufStartenRequest,
    SchrittDurchfuehrungResponse,
    StartbarePruefungResponse,
    StartbarePruefungenListeResponse,
)
from application.pruefausfuehrung.prueflauf_lesen import PrueflaufDetailAnsicht, PrueflaufLesen
from application.protokoll.erzeugen import ProtokollErzeugen
from application.pruefausfuehrung.foto_nachweis_erfassen import FotoNachweisErfassen
from application.pruefausfuehrung.nachweis_datei_lesen import NachweisDateiLesen
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehren
from application.pruefausfuehrung.komponente_erfassen import KomponenteErfassen
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen
from application.pruefausfuehrung.startbare_pruefungen_listen import StartbarePruefungenListen
from domain.pruefausfuehrung.datei_verweis import DateiVerweis
from domain.pruefausfuehrung.errors import PrueflaufNichtEigentuemer, PrueflaufNichtGefunden
from domain.pruefausfuehrung.typen import NachweisArt
from domain.shared.errors import DomainError


router = APIRouter(prefix="/prueflaeufe", tags=["Prüflauf"])


def _require_prueflauf_eigentuemer(request: Request, prueflauf_id: str) -> None:
    deps = get_request_deps(request)
    prueflauf = deps.prueflauf_repo.get(prueflauf_id)
    if prueflauf is None:
        raise PrueflaufNichtGefunden(f"Prüflauf {prueflauf_id} nicht gefunden")
    benutzer = RequestCurrentUserProvider(request).require()
    if benutzer.benutzer_id != prueflauf.pruefer_id:
        raise PrueflaufNichtEigentuemer("Nicht Eigentümer des Prüflaufs")


def _prueflauf_response(prueflauf) -> PrueflaufResponse:
    return PrueflaufResponse(
        prueflauf_id=prueflauf.prueflauf_id,
        version_id=prueflauf.version_id,
        produktkodierung=prueflauf.produktkodierung,
        pruefobjekt_kennung=prueflauf.pruefobjekt_kennung,
        pruefer_id=prueflauf.pruefer_id,
        status=prueflauf.status.value,
    )


def _prueflauf_detail_response(detail: PrueflaufDetailAnsicht) -> PrueflaufDetailResponse:
    return PrueflaufDetailResponse(
        prueflauf_id=detail.prueflauf_id,
        version_id=detail.version_id,
        produktkodierung=detail.produktkodierung,
        pruefobjekt_kennung=detail.pruefobjekt_kennung,
        pruefer_id=detail.pruefer_id,
        status=detail.status,
        gestartet_am=detail.gestartet_am,
        abgeschlossen_am=detail.abgeschlossen_am,
        schritte=[
            SchrittDurchfuehrungResponse(
                schritt_id=s.schritt_id,
                vorlage_id=s.vorlage_id,
                ist_pflicht=s.ist_pflicht,
                reihenfolge=s.reihenfolge,
                sollvorgaben=s.sollvorgaben,
                nachweise=[
                    NachweisDetailResponse(
                        nachweis_id=n.nachweis_id,
                        art=n.art,
                        erfasst_am=n.erfasst_am,
                        payload=n.payload,
                        ist_automatisch=n.ist_automatisch,
                    )
                    for n in s.nachweise
                ],
                beurteilung=(
                    BeurteilungResponse(
                        ergebnis=s.beurteilung.ergebnis,
                        festgelegt_am=s.beurteilung.festgelegt_am,
                        kommentar=s.beurteilung.kommentar,
                    )
                    if s.beurteilung
                    else None
                ),
                kann_nachweis_erfassen=s.kann_nachweis_erfassen,
                kann_beurteilt_werden=s.kann_beurteilt_werden,
                hat_automatisierung=s.hat_automatisierung,
                kann_automatisierung_ausfuehren=s.kann_automatisierung_ausfuehren,
                automatisierung_bezeichnung=s.automatisierung_bezeichnung,
            )
            for s in detail.schritte
        ],
        sollbestueckung=list(detail.sollbestueckung),
        erfasste_komponenten=list(detail.erfasste_komponenten),
        ist_abgeschlossen=detail.ist_abgeschlossen,
        fehlende_komponenten=list(detail.fehlende_komponenten),
        kann_komponente_erfassen=detail.kann_komponente_erfassen,
        kann_abgeschlossen_werden=detail.kann_abgeschlossen_werden,
    )


@router.get("/startbar", response_model=StartbarePruefungenListeResponse)
def startbare_pruefungen_listen(request: Request) -> StartbarePruefungenListeResponse:
    benutzer = RequestCurrentUserProvider(request).require()
    deps = get_request_deps(request)
    pruefungen = StartbarePruefungenListen(
        deps.katalog,
        deps.benutzer_repo,
        deps.profile_repo,
        deps.einweisung_repo,
    ).execute(benutzer_id=benutzer.benutzer_id)
    return StartbarePruefungenListeResponse(
        pruefungen=[
            StartbarePruefungResponse(produktkodierung=p.produktkodierung)
            for p in pruefungen
        ]
    )


@router.get("/{prueflauf_id}", response_model=PrueflaufDetailResponse)
def prueflauf_lesen(prueflauf_id: str, request: Request) -> PrueflaufDetailResponse:
    deps = get_request_deps(request)
    detail = PrueflaufLesen(deps.katalog, deps.prueflauf_repo).execute(prueflauf_id)
    return _prueflauf_detail_response(detail)


@router.post("", status_code=201, response_model=PrueflaufResponse)
def prueflauf_starten(body: PrueflaufStartenRequest, request: Request) -> PrueflaufResponse:
    deps = get_request_deps(request)
    benutzer = RequestCurrentUserProvider(request).require()
    prueflauf = PruefungStarten(
        deps.katalog,
        deps.prueflauf_repo,
        deps.benutzer_repo,
        deps.profile_repo,
        deps.einweisung_repo,
    ).execute(
        produktkodierung=body.produktkodierung,
        pruefobjekt_kennung=body.pruefobjekt_kennung,
        pruefer_id=benutzer.benutzer_id,
    )
    return _prueflauf_response(prueflauf)


@router.post("/{prueflauf_id}/komponenten", status_code=201, response_model=NachweisResponse)
def komponente_erfassen(
    prueflauf_id: str,
    body: KomponenteErfassenRequest,
    request: Request,
) -> NachweisResponse:
    _require_prueflauf_eigentuemer(request, prueflauf_id)
    deps = get_request_deps(request)
    nachweis = KomponenteErfassen(deps.prueflauf_repo).execute(
        prueflauf_id, body.komponenten_typ, body.seriennummer
    )
    return NachweisResponse(nachweis_id=nachweis.nachweis_id, art=nachweis.art.value)


@router.post(
    "/{prueflauf_id}/schritte/{schritt_id}/automatisierung/ausfuehren",
    status_code=200,
    response_model=AutomatisierungAusfuehrenResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def automatisierung_ausfuehren(
    prueflauf_id: str,
    schritt_id: str,
    request: Request,
    _body: AutomatisierungAusfuehrenRequest = Body(
        default_factory=AutomatisierungAusfuehrenRequest
    ),
) -> AutomatisierungAusfuehrenResponse:
    deps = get_request_deps(request)
    try:
        _require_prueflauf_eigentuemer(request, prueflauf_id)
        ergebnis = RoutineAusfuehren(
            deps.katalog,
            deps.prueflauf_repo,
            deps.kommando_port,
        ).execute(prueflauf_id, schritt_id)
    except DomainError as exc:
        beobachte_automatisierung_nicht_begonnen(
            exc, prueflauf_id=prueflauf_id, schritt_id=schritt_id
        )
        raise
    beobachte_ausgefuehrte_automatisierung(
        ergebnis, prueflauf_id=prueflauf_id, schritt_id=schritt_id
    )
    return automatisierung_ausfuehren_response(ergebnis)


@router.post(
    "/{prueflauf_id}/schritte/{schritt_id}/nachweise",
    status_code=201,
    response_model=NachweisResponse,
)
def nachweis_erfassen(
    prueflauf_id: str,
    schritt_id: str,
    body: NachweisErfassenRequest,
    request: Request,
) -> NachweisResponse:
    _require_prueflauf_eigentuemer(request, prueflauf_id)
    deps = get_request_deps(request)
    nachweis = NachweisErfassen(deps.prueflauf_repo).execute(
        prueflauf_id,
        schritt_id,
        NachweisArt(body.art.value),
        body.payload,
        ist_automatisch=body.ist_automatisch,
    )
    return NachweisResponse(nachweis_id=nachweis.nachweis_id, art=nachweis.art.value)


def _foto_nachweis_response(nachweis) -> FotoNachweisResponse:
    verweis = DateiVerweis.from_payload(nachweis.payload)
    return FotoNachweisResponse(
        nachweis_id=nachweis.nachweis_id,
        art=nachweis.art.value,
        datei_id=verweis.datei_id,
        mime_type=verweis.mime_type,
        groesse_bytes=verweis.groesse_bytes,
        dateiname=verweis.dateiname,
    )


def _sicherer_download_dateiname(dateiname: str | None, mime_type: str) -> str:
    if dateiname:
        basis = dateiname.replace("\r", "").replace("\n", "").replace('"', "")
        basis = basis.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].strip()
        if basis:
            return basis
    if mime_type == "image/png":
        return "foto.png"
    return "foto.jpg"


@router.post(
    "/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
    status_code=201,
    response_model=FotoNachweisResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def foto_nachweis_erfassen(
    prueflauf_id: str,
    schritt_id: str,
    request: Request,
    datei: UploadFile = File(...),
) -> FotoNachweisResponse:
    _require_prueflauf_eigentuemer(request, prueflauf_id)
    deps = get_request_deps(request)
    inhalt = await datei.read()
    mime_type = datei.content_type or "application/octet-stream"
    nachweis = FotoNachweisErfassen(deps.prueflauf_repo, deps.datei_speicher).execute(
        prueflauf_id,
        schritt_id,
        inhalt,
        mime_type,
        dateiname=datei.filename,
    )
    return _foto_nachweis_response(nachweis)


@router.get(
    "/{prueflauf_id}/nachweise/{nachweis_id}/datei",
    responses={
        404: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def nachweis_datei_lesen(
    prueflauf_id: str,
    nachweis_id: str,
    request: Request,
) -> Response:
    deps = get_request_deps(request)
    ergebnis = NachweisDateiLesen(deps.prueflauf_repo, deps.datei_speicher).execute(
        prueflauf_id,
        nachweis_id,
    )
    dateiname = _sicherer_download_dateiname(ergebnis.dateiname, ergebnis.mime_type)
    disposition = f'inline; filename="{dateiname}"; filename*=UTF-8\'\'{quote(dateiname)}'
    return Response(
        content=ergebnis.inhalt,
        media_type=ergebnis.mime_type,
        headers={"Content-Disposition": disposition},
    )


@router.post(
    "/{prueflauf_id}/schritte/{schritt_id}/beurteilung",
    status_code=204,
    response_class=Response,
)
def schritt_beurteilen(prueflauf_id: str, schritt_id: str, request: Request) -> Response:
    _require_prueflauf_eigentuemer(request, prueflauf_id)
    deps = get_request_deps(request)
    SchrittBeurteilen(deps.katalog, deps.prueflauf_repo).execute(prueflauf_id, schritt_id)
    return Response(status_code=204)


@router.post("/{prueflauf_id}/abschluss", response_model=AbschlussResponse)
def prueflauf_abschliessen(prueflauf_id: str, request: Request) -> AbschlussResponse:
    _require_prueflauf_eigentuemer(request, prueflauf_id)
    deps = get_request_deps(request)
    prueflauf, snapshot = PruefungAbschliessen(
        deps.katalog, deps.prueflauf_repo, deps.abschluss_persistenz
    ).execute(prueflauf_id)
    return AbschlussResponse(
        prueflauf_id=prueflauf.prueflauf_id,
        status=prueflauf.status.value,
        ist_gueltig=prueflauf.ist_gueltig(),
        snapshot_id=snapshot.snapshot_id,
    )


@router.get("/{prueflauf_id}/protokoll/pdf")
def protokoll_pdf(prueflauf_id: str, request: Request) -> Response:
    deps = get_request_deps(request)
    dokument = ProtokollErzeugen(deps.protokoll_repo, deps.erzeugung_port).execute(prueflauf_id)
    return Response(
        content=dokument.inhalt,
        media_type=dokument.medientyp,
        headers={"Content-Disposition": f'attachment; filename="{dokument.dateiname}"'},
    )
