"""HTTP-Routen — Prüflauf (delegiert an Application-Use-Cases)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import Response

from api.schemas import (
    AbschlussResponse,
    BeurteilungResponse,
    KomponenteErfassenRequest,
    NachweisDetailResponse,
    NachweisErfassenRequest,
    NachweisResponse,
    PrueflaufDetailResponse,
    PrueflaufResponse,
    PrueflaufStartenRequest,
    SchrittDurchfuehrungResponse,
)
from application.pruefausfuehrung.prueflauf_lesen import PrueflaufDetailAnsicht, PrueflaufLesen
from application.protokoll.erzeugen import ProtokollErzeugen
from application.pruefausfuehrung.komponente_erfassen import KomponenteErfassen
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen
from domain.pruefausfuehrung.typen import NachweisArt


router = APIRouter(prefix="/prueflaeufe", tags=["Prüflauf"])


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


@router.get("/{prueflauf_id}", response_model=PrueflaufDetailResponse)
def prueflauf_lesen(prueflauf_id: str, request: Request) -> PrueflaufDetailResponse:
    deps = request.app.state.deps
    detail = PrueflaufLesen(deps.katalog, deps.prueflauf_repo).execute(prueflauf_id)
    return _prueflauf_detail_response(detail)


@router.post("", status_code=201, response_model=PrueflaufResponse)
def prueflauf_starten(body: PrueflaufStartenRequest, request: Request) -> PrueflaufResponse:
    deps = request.app.state.deps
    prueflauf = PruefungStarten(deps.katalog, deps.prueflauf_repo).execute(
        produktkodierung=body.produktkodierung,
        pruefobjekt_kennung=body.pruefobjekt_kennung,
        pruefer_id=body.pruefer_id,
    )
    return _prueflauf_response(prueflauf)


@router.post("/{prueflauf_id}/komponenten", status_code=201, response_model=NachweisResponse)
def komponente_erfassen(
    prueflauf_id: str,
    body: KomponenteErfassenRequest,
    request: Request,
) -> NachweisResponse:
    deps = request.app.state.deps
    nachweis = KomponenteErfassen(deps.prueflauf_repo).execute(
        prueflauf_id, body.komponenten_typ, body.seriennummer
    )
    return NachweisResponse(nachweis_id=nachweis.nachweis_id, art=nachweis.art.value)


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
    deps = request.app.state.deps
    nachweis = NachweisErfassen(deps.prueflauf_repo).execute(
        prueflauf_id,
        schritt_id,
        NachweisArt(body.art.value),
        body.payload,
        ist_automatisch=body.ist_automatisch,
    )
    return NachweisResponse(nachweis_id=nachweis.nachweis_id, art=nachweis.art.value)


@router.post(
    "/{prueflauf_id}/schritte/{schritt_id}/beurteilung",
    status_code=204,
    response_class=Response,
)
def schritt_beurteilen(prueflauf_id: str, schritt_id: str, request: Request) -> Response:
    deps = request.app.state.deps
    SchrittBeurteilen(deps.katalog, deps.prueflauf_repo).execute(prueflauf_id, schritt_id)
    return Response(status_code=204)


@router.post("/{prueflauf_id}/abschluss", response_model=AbschlussResponse)
def prueflauf_abschliessen(prueflauf_id: str, request: Request) -> AbschlussResponse:
    deps = request.app.state.deps
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
    deps = request.app.state.deps
    dokument = ProtokollErzeugen(deps.protokoll_repo, deps.erzeugung_port).execute(prueflauf_id)
    return Response(
        content=dokument.inhalt,
        media_type=dokument.medientyp,
        headers={"Content-Disposition": f'attachment; filename="{dokument.dateiname}"'},
    )
