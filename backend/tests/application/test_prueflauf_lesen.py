"""Application-Tests — PrueflaufLesen."""

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository, InMemoryPrueflaufRepository
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.prueflauf_lesen import PrueflaufLesen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf


def test_prueflauf_lesen_liefert_materialisierte_schritte():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"druck": {"min": 1, "max": 2}},
            ),
        ),
        sollbestueckung=("platine",),
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="OBJ-1",
        pruefer_id="p1",
    )

    detail = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)

    assert detail.prueflauf_id == prueflauf.prueflauf_id
    assert len(detail.schritte) == 1
    assert detail.schritte[0].schritt_id == "s1"
    assert detail.schritte[0].sollvorgaben["druck"]["min"] == 1
    assert detail.sollbestueckung == ("platine",)
