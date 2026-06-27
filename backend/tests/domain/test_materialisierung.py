"""Domain-Tests — Sollvorgaben-Materialisierung."""

from domain.katalog.materialisierung import materialisiere_sollvorgaben


def test_materialisierung_aufloesungskette():
    result = materialisiere_sollvorgaben(
        {"spannung": {"min": 200, "max": 250}, "toleranz": 5},
        {"spannung": {"min": 220, "max": 240}},
        {"toleranz": 3},
        {"spannung": {"min": 225, "max": 235}},
    )

    assert result["spannung"] == {"min": 225, "max": 235}
    assert result["toleranz"] == 3


def test_materialisierung_leere_ebenen():
    result = materialisiere_sollvorgaben({}, {}, {"gewicht": 10.5}, {})
    assert result == {"gewicht": 10.5}
