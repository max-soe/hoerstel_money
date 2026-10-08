"""Tests für die IKVS-Schritte 01 und 02 (Hörstel): Seitenklassifikation, Hierarchie,
Teilergebnis- und Teilfinanzpläne, Prüfregeln 1-3 und Anhang B.3.

Die PDF-Tests laufen die öffentlichen Schritte `klassifiziere_seiten` und
`extrahiere_plaene` einmal gegen ein temporäres `daten/`-Verzeichnis, nie gegen das
eingecheckte. Jahrgang und Sollwerte kommen aus dem aktiven Jahrgang
(STANDARD_JAHRGAENGE_VERZEICHNIS), auch wenn conftest.py die übrigen Tests auf den
Ostbevern-Referenzjahrgang umlenkt.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from ostbevern.ikvs import lies_tabellenkopf
from ostbevern.konfiguration import (
    STANDARD_JAHR,
    STANDARD_JAHRGAENGE_VERZEICHNIS,
    Jahrgang,
    lade_jahrgang,
    lade_sollwerte,
)
from ostbevern.pdf import Textzeile, Wort
from ostbevern.plaene import extrahiere_plaene
from ostbevern.pruefung import (
    Planwerte,
    Pruefpunkt,
    _pruefe_regel1,
    _pruefe_regel2,
    _pruefe_regel3,
    _pruefe_regel4_b3,
)
from ostbevern.schema import (
    HIERARCHIE_CSV,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
)
from ostbevern.seiten import klassifiziere_seiten

_SPALTEN = ("Ergebnis 2024", "Ansatz 2025", "Ansatz 2026", "Plan 2027", "Plan 2028", "Plan 2029")

# Gedruckte Abweichungen des Hörsteler PDF (je > 1 €), Schlüssel (Regel, Ebene, Code, Zeile,
# Jahr). Rundungsdifferenzen der Ist-Ergebnisse 2024 von 2 €: Produkt 0212601 Z. 10 (S. 206,
# die Einzelwerte ergeben 287.141 €, gedruckt 287.143 €; die PG 02126 erbt sie), PB 05 und
# PB 12 Z. 29/31 (S. 274/442). Regel 3: Die Teilpläne enthalten 5.800 € (2026) bzw. 4.400 €
# (2027) weniger Transferaufwendungen als der Gesamtergebnisplan (S. 79); auch die
# Haushaltsquerschnitte der 50 Produktgruppen (S. 85-109) ergeben in Summe weniger als der
# Querschnitt "Gesamthaushalt" (S. 110).
_BEFUNDE = {
    (1, "PG", "02126", "10", 2024),
    (1, "P", "0212601", "10", 2024),
    (2, "PB", "05", "29", 2024),
    (2, "PB", "05", "31", 2024),
    (2, "PB", "12", "29", 2024),
    (2, "PB", "12", "31", 2024),
    (3, "GESAMT", "", "10", 2024),
    (3, "GESAMT", "", "15", 2026),
    (3, "GESAMT", "", "15", 2027),
    (3, "GESAMT", "", "17", 2026),
    (3, "GESAMT", "", "17", 2027),
}


def _schluessel(punkt: Pruefpunkt) -> tuple[int, str, str, str, int]:
    return (punkt.regel, punkt.ebene, punkt.code, punkt.zeile, punkt.jahr)


def _woerter(top: float, *eintraege: tuple[str, float, float]) -> Textzeile:
    return Textzeile(
        top=top,
        woerter=tuple(Wort(text=t, x0=x0, x1=x1, top=top, groesse=8.0) for t, x0, x1 in eintraege),
    )


def test_tabellenkopf_einzeilig() -> None:
    zeile = _woerter(
        112.0,
        *(
            (text, x, x + 20.0)
            for text, x in zip(
                [w for kopf in _SPALTEN for w in kopf.split()],
                [
                    119.7,
                    157.8,
                    198.2,
                    228.2,
                    272.7,
                    302.8,
                    351.9,
                    372.5,
                    426.4,
                    447.0,
                    501.0,
                    521.6,
                ],
                strict=True,
            )
        ),
    )
    kopf = lies_tabellenkopf([zeile], 0, _SPALTEN, 113)
    assert kopf is not None
    spalten, anzahl = kopf
    assert anzahl == 1
    assert len(spalten.grenzen) == 6


def test_tabellenkopf_dreizeilig() -> None:
    """S. 511: "Ergebnis" und "2024" stehen über bzw. unter den übrigen Spaltenköpfen."""
    oben = _woerter(133.1, ("Ergebnis", 157.0, 193.0))
    mitte = _woerter(
        138.2,
        ("Ansatz", 214.0, 241.0),
        ("2025", 244.0, 264.0),
        ("Ansatz", 282.0, 309.0),
        ("2026", 312.0, 332.0),
        ("Plan", 359.0, 377.0),
        ("2027", 379.0, 399.0),
        ("Plan", 431.0, 449.0),
        ("2028", 451.0, 471.0),
        ("Plan", 503.0, 521.0),
        ("2029", 523.0, 543.0),
    )
    unten = _woerter(143.4, ("2024", 165.0, 185.0))
    zeilen = [oben, mitte, unten]
    kopf = lies_tabellenkopf(zeilen, 0, _SPALTEN, 511)
    assert kopf is not None
    _, anzahl = kopf
    assert anzahl == 3


def test_tabellenkopf_ist_keine_planzeile() -> None:
    zeile = _woerter(150.0, ("17", 42.0, 51.0), ("-", 53.0, 56.0), ("Saldo", 58.0, 80.0))
    assert lies_tabellenkopf([zeile], 0, _SPALTEN, 511) is None


@pytest.fixture(scope="module")
def jahrgang() -> Jahrgang:
    jahrgang = lade_jahrgang(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)
    assert jahrgang.software == "ikvs"
    return jahrgang


@pytest.fixture(scope="module")
def sollwerte() -> dict:
    return lade_sollwerte(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)


@pytest.fixture(scope="module")
def daten(jahrgang: Jahrgang, tmp_path_factory: pytest.TempPathFactory) -> Path:
    wurzel = tmp_path_factory.mktemp("daten")
    (wurzel / "zwischen").mkdir()
    (wurzel / "aufbereitet").mkdir()
    klassifiziere_seiten(jahrgang, daten_wurzel=wurzel)
    extrahiere_plaene(jahrgang, daten_wurzel=wurzel)
    return wurzel


@pytest.fixture(scope="module")
def plaene(daten: Path) -> dict[str, pl.DataFrame]:
    return {
        datei: lies_plan_csv(daten / "aufbereitet" / f"{datei}.csv")
        for datei in ("ergebnisplan", "finanzplan")
    }


@pytest.fixture(scope="module")
def hierarchie(daten: Path) -> pl.DataFrame:
    return lies_hierarchie_csv(daten / HIERARCHIE_CSV)


def test_hierarchie_vollstaendig(jahrgang: Jahrgang, hierarchie: pl.DataFrame) -> None:
    anzahl = dict(hierarchie.group_by("ebene").len().iter_rows())
    assert anzahl["PB"] == jahrgang.anzahlen.produktbereiche
    assert anzahl["P"] == jahrgang.anzahlen.produkte
    codes = {z["code"]: z for z in hierarchie.iter_rows(named=True)}
    for zeile in hierarchie.filter(pl.col("ebene") != "PB").iter_rows(named=True):
        eltern = codes[zeile["eltern_code"]]
        assert zeile["code"].startswith(eltern["code"])
        assert eltern["ebene"] == {"PG": "PB", "P": "PG"}[zeile["ebene"]]
    assert hierarchie.filter(pl.col("ebene") == "PG")["synthetisch"].all()


def test_pb_startseiten_wie_inhaltsverzeichnis(hierarchie: pl.DataFrame, sollwerte: dict) -> None:
    pb = {
        z["code"]: (z["name"], z["pdf_seite_start"])
        for z in hierarchie.filter(pl.col("ebene") == "PB").iter_rows(named=True)
    }
    assert pb == {
        code: (eintrag["name"], eintrag["pdf_seite"])
        for code, eintrag in sollwerte["anhang_a"].items()
    }


def test_seiten_ohne_unbekannte(daten: Path, jahrgang: Jahrgang) -> None:
    seiten = lies_seiten_csv(daten / SEITEN_CSV)
    assert seiten.height == jahrgang.anzahlen.pdf_seiten
    assert seiten.filter(pl.col("typ") == "unbekannt").height == 0
    teilplan = jahrgang.seitenbereiche["teilplaene"]
    im_teilplan = seiten.filter(pl.col("pdf_seite").is_between(teilplan.von, teilplan.bis))
    assert im_teilplan["pb"].null_count() == 0
    produktseiten = im_teilplan.filter(pl.col("produkt").is_not_null())
    assert produktseiten["pg"].null_count() == 0
    assert set(produktseiten.filter(pl.col("typ") == "produktinformationen")["produkt"]) == set(
        produktseiten["produkt"]
    )


def test_jeder_knoten_hat_beide_teilplaene(
    plaene: dict[str, pl.DataFrame], hierarchie: pl.DataFrame
) -> None:
    for datei, df in plaene.items():
        teil = df.filter(pl.col("ebene") != "GESAMT")
        for ebene in ("PB", "PG", "P"):
            erwartet = set(hierarchie.filter(pl.col("ebene") == ebene)["code"])
            gefunden = set(teil.filter(pl.col("ebene") == ebene)["code"])
            assert gefunden == erwartet, (datei, ebene)


def test_regeln_1_bis_3_nur_belegte_abweichungen(
    jahrgang: Jahrgang, plaene: dict[str, pl.DataFrame], hierarchie: pl.DataFrame
) -> None:
    ergebnisplan, finanzplan = plaene["ergebnisplan"], plaene["finanzplan"]
    ergebnisse = [
        _pruefe_regel1(
            ergebnisplan=ergebnisplan, finanzplan=finanzplan, nur_mit_gedruckten_komponenten=True
        ),
        _pruefe_regel2(
            ergebnisplan=ergebnisplan,
            finanzplan=finanzplan,
            hierarchie=hierarchie,
            jahrgang=jahrgang,
        ),
        _pruefe_regel3(
            planwerte=Planwerte(ergebnisplan, datei="ergebnisplan"),
            hierarchie=hierarchie,
            spalten=jahrgang.spalten["ergebnisplan"],
            pdf_seite=jahrgang.seitenbereiche["gesamtergebnisplan"].von,
        ),
    ]
    for ergebnis in ergebnisse:
        assert ergebnis.geprueft > 0
    gefunden = {_schluessel(p) for e in ergebnisse for p in e.abweichungen}
    assert gefunden == _BEFUNDE


def test_teilergebnisplaene_pb_treffen_sollwerte(
    jahrgang: Jahrgang, plaene: dict[str, pl.DataFrame], hierarchie: pl.DataFrame, sollwerte: dict
) -> None:
    geprueft, abweichungen = _pruefe_regel4_b3(
        planwerte=Planwerte(plaene["ergebnisplan"], datei="ergebnisplan"),
        hierarchie=hierarchie,
        sollwerte=sollwerte,
        haushaltsjahr=jahrgang.haushaltsjahr,
    )
    assert geprueft == 3 * jahrgang.anzahlen.produktbereiche + 2
    assert abweichungen == []


def test_pb_finanzplan_z17_ist_abgeleitet(plaene: dict[str, pl.DataFrame]) -> None:
    """PB-Teilfinanzpläne drucken Z. 32, aber nicht Z. 17; Z. 17 = Z. 32 - Z. 31 (synthetisch)."""
    pb = plaene["finanzplan"].filter(pl.col("ebene") == "PB")
    planwerte = Planwerte(plaene["finanzplan"], datei="finanzplan")
    z17 = pb.filter(pl.col("zeile") == "17")
    assert z17.height > 0
    assert z17["synthetisch"].all()
    for zeile in z17.iter_rows(named=True):
        z32 = planwerte.wert("PB", zeile["code"], "32", zeile["jahr"], zeile["wertart"])
        z31 = planwerte.wert("PB", zeile["code"], "31", zeile["jahr"], zeile["wertart"])
        assert zeile["betrag"] == z32 - z31
