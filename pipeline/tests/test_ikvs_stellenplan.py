"""Tests für Schritt 05 im IKVS-Layout (Hörstel, Phase 11): die Abschrift des nur als Bild
gedruckten Stellenplans (S. 568-574) in `daten/manuell/` und ihre Gegenproben.

Die Abschrift liegt im Projekt-`daten/` (nicht im Ostbevern-Referenzstand, auf den
conftest.py die übrigen Tests umlenkt) und wird deshalb über PROJEKT_WURZEL gelesen.
"""

from __future__ import annotations

import polars as pl
import pytest

from ostbevern.ikvs_stellenplan import (
    IkvsStellenplanFehler,
    baue_stellenplan,
    pruefe_stellenuebersicht,
)
from ostbevern.konfiguration import PROJEKT_WURZEL
from ostbevern.pruefung import _pruefe_regel10
from ostbevern.schema import (
    HIERARCHIE_SPALTEN,
    STELLENPLAN_MANUELL_CSV,
    STELLENUEBERSICHT_CSV,
    lies_stellenplan_csv,
    lies_stellenuebersicht_csv,
)

HAUSHALTSJAHR = 2026
_MANUELL = PROJEKT_WURZEL / "daten"

# Spalten der Stellenübersicht, deren gerundete Zellen nicht exakt die gedruckte
# Spaltensumme ergeben (Σ Zellen, gedruckt; S. 570/571 Beamte, S. 572/573 Tarif). Regel 10
# meldet dieselben Gruppen als belegte Abweichung gegen Teil A/B.
_RUNDUNG = {
    ("beamte", "A14"): (204, 200),
    ("beamte", "A12"): (377, 375),
    ("beamte", "A11"): (235, 234),
    ("beamte", "A10"): (522, 521),
    ("beamte", "A9Z"): (280, 278),
    ("tarif", "09c"): (657, 659),
    ("tarif", "09b"): (894, 892),
    ("tarif", "08"): (598, 599),
    ("tarif", "07"): (1298, 1297),
    ("tarif", "06"): (3313, 3312),
    ("tarif", "05"): (786, 785),
}


@pytest.fixture(scope="module")
def teil_ab() -> pl.DataFrame:
    return lies_stellenplan_csv(_MANUELL / STELLENPLAN_MANUELL_CSV)


@pytest.fixture(scope="module")
def uebersicht() -> pl.DataFrame:
    return lies_stellenuebersicht_csv(_MANUELL / STELLENUEBERSICHT_CSV)


def _hierarchie(produkte: set[str]) -> pl.DataFrame:
    """Hierarchie nach dem Hörsteler Codeschema (PB 2-, PG 5-, Produkt 7-stellig)."""
    zeilen = []
    for pb in sorted({p[:2] for p in produkte}):
        zeilen.append(("PB", pb, pb, None))
    for pg in sorted({p[:5] for p in produkte}):
        zeilen.append(("PG", pg, pg, pg[:2]))
    for p in sorted(produkte):
        zeilen.append(("P", p, p, p[:5]))
    return pl.DataFrame(
        [
            {
                "ebene": e,
                "code": c,
                "name": n,
                "eltern_code": el,
                "pdf_seite_start": 1,
                "synthetisch": False,
            }
            for e, c, n, el in zeilen
        ],
        schema=HIERARCHIE_SPALTEN,
    )


@pytest.fixture(scope="module")
def stellenplan(teil_ab: pl.DataFrame, uebersicht: pl.DataFrame) -> pl.DataFrame:
    produkte = set(uebersicht["produkt"].drop_nulls())
    return baue_stellenplan(teil_ab, uebersicht, _hierarchie(produkte), haushaltsjahr=HAUSHALTSJAHR)


def test_teil_ab_summen(teil_ab: pl.DataFrame) -> None:
    """Gedruckte Insgesamt-Zeilen S. 568/569: Teil A 19,81, Teil B 105,21 Stellen (2026)."""
    stellen = teil_ab.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2026))
    je_teil = dict(stellen.group_by("teil").agg(pl.col("stellen_hundertstel").sum()).iter_rows())
    assert je_teil["beamte"] == 1981
    assert je_teil["tarif"] + je_teil["sozial_erziehungsdienst"] == 10521
    vorgesehen = teil_ab.filter(pl.col("merkmal") == "vorgesehen")
    assert vorgesehen["personen"].sum() == 13


def test_uebersicht_nur_rundungsdifferenzen(uebersicht: pl.DataFrame) -> None:
    differenzen = pruefe_stellenuebersicht(uebersicht)
    assert {(d.teil, d.gruppe): (d.summe_zellen, d.gedruckt) for d in differenzen} == _RUNDUNG


def test_uebersicht_spaltensummen_gleich_teil_ab(
    teil_ab: pl.DataFrame, uebersicht: pl.DataFrame
) -> None:
    """Die gedruckten Spaltensummen der Übersicht treffen Teil A/B exakt."""
    spalten = uebersicht.filter(
        pl.col("ist_summe")
        & pl.col("produkt").is_null()
        & pl.col("gruppe").is_not_null()
        & (pl.col("stellen_hundertstel") != 0)
    )
    soll = teil_ab.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == HAUSHALTSJAHR))
    assert dict(
        ((z["teil"], z["gruppe"]), z["stellen_hundertstel"]) for z in spalten.iter_rows(named=True)
    ) == dict(
        ((z["teil"], z["gruppe"]), z["stellen_hundertstel"]) for z in soll.iter_rows(named=True)
    )


def test_produktsumme_falsch_bricht_ab(uebersicht: pl.DataFrame) -> None:
    erste_zelle = uebersicht.with_row_index().filter(~pl.col("ist_summe"))["index"][0]
    kaputt = uebersicht.with_columns(
        pl.when(pl.int_range(pl.len()) == erste_zelle)
        .then(pl.col("stellen_hundertstel") + 1)
        .otherwise(pl.col("stellen_hundertstel"))
        .alias("stellen_hundertstel")
    )
    with pytest.raises(IkvsStellenplanFehler, match="gedruckte Summe"):
        pruefe_stellenuebersicht(kaputt)


def test_stellenplan_je_produktbereich(stellenplan: pl.DataFrame) -> None:
    pb = stellenplan.filter(pl.col("produktbereich").is_not_null())
    assert set(pb["merkmal"]) == {"stellen"}
    assert set(pb["jahr"]) == {HAUSHALTSJAHR}
    # Σ Übersicht je Tabelle = Σ Zellen (Beamte 19,91, Tarif inkl. S 105,21 + Rundung)
    beamte = pb.filter(pl.col("teil") == "beamte")["stellen_hundertstel"].sum()
    assert beamte == 1981 + sum(z - g for (t, _), (z, g) in _RUNDUNG.items() if t == "beamte")
    # PB 01 (Innere Verwaltung) trägt die B4-Stelle des Bürgermeisters
    b4 = pb.filter(pl.col("gruppe") == "B4")
    assert b4.select("produktbereich", "stellen_hundertstel").rows() == [("01", 100)]


def test_regel10_meldet_nur_rundung(stellenplan: pl.DataFrame) -> None:
    ergebnis = _pruefe_regel10(stellenplan=stellenplan, haushaltsjahr=HAUSHALTSJAHR)
    gemeldet = {
        (p.plan.removeprefix("stellenuebersicht_"), p.zeile): (p.ist, p.soll)
        for p in ergebnis.abweichungen
    }
    assert gemeldet == {
        (teil, gruppe): (zellen, gedruckt)
        for (teil, gruppe), (zellen, gedruckt) in _RUNDUNG.items()
    }
    assert ergebnis.geprueft == 23  # 8 Beamten-, 13 Tarif-, 2 S-Gruppen


def test_gruppe_ohne_teil_ab_bricht_ab(teil_ab: pl.DataFrame, uebersicht: pl.DataFrame) -> None:
    ohne_a8 = teil_ab.filter(pl.col("gruppe") != "A8")
    produkte = set(uebersicht["produkt"].drop_nulls())
    with pytest.raises(IkvsStellenplanFehler, match="fehlt in Teil A/B"):
        baue_stellenplan(ohne_a8, uebersicht, _hierarchie(produkte), haushaltsjahr=HAUSHALTSJAHR)
