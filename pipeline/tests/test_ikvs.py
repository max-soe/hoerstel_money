"""Tests für ostbevern.ikvs: Gesamtpläne im IKVS-Layout (Hörstel).

Die PDF-Tests lesen nur das Original-PDF, nie daten/. Seiten, Spalten und Sollwerte kommen
aus lade_jahrgang(STANDARD_JAHR) bzw. lade_sollwerte(STANDARD_JAHR); die Einheitstests
bauen synthetische Textzeilen mit der Geometrie der Hörsteler Gesamtpläne.
"""

from __future__ import annotations

import polars as pl
import pytest

from ostbevern.ikvs import (
    IKVS_ZEILEN,
    IkvsFehler,
    gesamtplan_datensaetze,
    lies_ikvs_betrag,
    lies_ikvs_plantabelle,
)
from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_jahrgang, lade_sollwerte
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.pruefung import TOLERANZ_EURO, Planwerte, _pruefe_regel1, _pruefe_regel4_satzung
from ostbevern.schema import PLAN_SPALTEN, zerlege_spaltenkopf
from ostbevern.zeilen import ZEILEN

_SPALTEN = ("Ergebnis 2024", "Ansatz 2025", "Ansatz 2026")
# Rechte Kanten der Betragsspalten und Mitten der Jahreszahlen wie auf PDF S. 79/80.
_BETRAG_X1 = (249.3, 309.9, 370.8)
_JAHR_MITTE = (223.6, 285.0, 345.7)


def _wort(text: str, x0: float, x1: float, top: float) -> Wort:
    return Wort(text=text, x0=x0, x1=x1, top=top, groesse=8.0)


def _zeile(top: float, *woerter: Wort) -> Textzeile:
    return Textzeile(top=top, woerter=tuple(woerter))


def _bezeichnung(top: float, text: str, x0: float = 42.2) -> list[Wort]:
    woerter = []
    for teil in text.split():
        breite = 3.0 * len(teil)
        woerter.append(_wort(teil, x0, x0 + breite, top))
        x0 += breite + 2.0
    return woerter


def _werte(top: float, *texte: str) -> list[Wort]:
    return [
        _wort(text, x1 - 5.0 * len(text), x1, top)
        for text, x1 in zip(texte, _BETRAG_X1, strict=True)
    ]


def _kopf() -> list[Textzeile]:
    bezeichnungen = [kopf.split()[0] for kopf in _SPALTEN]
    jahre = [kopf.split()[1] for kopf in _SPALTEN]
    return [
        _zeile(100.0, *_bezeichnung(100.0, "Haushaltsplan 2026 Hörstel", x0=236.0)),
        _zeile(
            133.0,
            *(
                _wort(text, mitte - 15.0, mitte + 15.0, 133.0)
                for text, mitte in zip(bezeichnungen, _JAHR_MITTE, strict=True)
            ),
        ),
        _zeile(
            143.0,
            *(
                _wort(text, mitte - 10.0, mitte + 10.0, 143.0)
                for text, mitte in zip(jahre, _JAHR_MITTE, strict=True)
            ),
        ),
    ]


def _lies(zeilen: list[Textzeile], plantyp: str = "gesamtfinanzplan") -> dict[str, tuple]:
    gelesen = lies_ikvs_plantabelle(
        [*_kopf(), *zeilen, _zeile(790.0, _wort("80", 292.0, 303.0, 790.0))],
        plantyp=plantyp,
        gedruckte_spalten=_SPALTEN,
        pdf_seite=80,
    )
    return {z.zeile: z.werte for z in gelesen}


@pytest.mark.parametrize(
    ("text", "erwartet"),
    [
        ("--", 0),
        ("1.234", 1234),
        ("-9.187.144", -9187144),
        ("32.813.040,08", 32813040),
        ("409.506,51", 409507),
        ("-209.511,68", -209512),
        ("0,50", 1),
        ("-0,50", -1),
    ],
)
def test_lies_ikvs_betrag(text: str, erwartet: int) -> None:
    assert lies_ikvs_betrag(text) == erwartet


@pytest.mark.parametrize("text", ["-", "1.23", "12,345", "abc", ""])
def test_lies_ikvs_betrag_bricht_ab(text: str) -> None:
    with pytest.raises(IkvsFehler):
        lies_ikvs_betrag(text)


def test_umbrochene_bezeichnung_mit_betraegen_in_zwischenzeile() -> None:
    zeilen = [
        _zeile(200.0, *_bezeichnung(200.0, "2 - Zuwendungen und allgemeine Umla-")),
        _zeile(205.0, *_werte(205.0, "6.028.720,50", "5.849.400", "7.164.460")),
        _zeile(210.0, *_bezeichnung(210.0, "gen")),
        _zeile(
            223.0,
            *_bezeichnung(223.0, "3 - Sonstige Transfereinzahlungen"),
            *_werte(223.0, "675.599,46", "--", "479.503"),
        ),
    ]
    assert _lies(zeilen) == {
        "02": (6028721, 5849400, 7164460),
        "03": (675599, 0, 479503),
    }


def test_abgetrenntes_minuszeichen_gehoert_zum_betrag_darunter() -> None:
    zeilen = [
        _zeile(
            709.0,
            *_bezeichnung(709.0, "31 - Saldo aus Investitionstätigkeit (="),
            _wort("-", 246.5, 249.2, 709.0),
        ),
        _zeile(714.0, *_werte(714.0, "", "-9.187.144", "-17.527.813")[1:]),
        _zeile(
            718.0,
            *_bezeichnung(718.0, "Zeilen 23 und 30)"),
            _wort("17.261.143,94", 198.1, 249.3, 718.0),
        ),
    ]
    assert _lies(zeilen) == {"31": (-17261144, -9187144, -17527813)}


def test_ungedruckte_zeile_wird_ueber_bezeichnung_zugeordnet() -> None:
    zeilen = [
        _zeile(
            300.0,
            *_bezeichnung(300.0, "39 - Anfangsbestand an Finanzmitteln"),
            *_werte(300.0, "14.064.806,01", "4.798.412", "-1.779.452"),
        ),
        _zeile(310.0, *_bezeichnung(310.0, "Änderung des Bestandes an fremden Fi-")),
        _zeile(315.0, *_werte(315.0, "7.440,98", "--", "--")),
        _zeile(320.0, *_bezeichnung(320.0, "nanzmitteln")),
        _zeile(
            330.0,
            *_bezeichnung(330.0, "40 - Liquide Mittel (= Zeilen 38 und 39)"),
            *_werte(330.0, "4.943.998,75", "-1.779.452", "-5.944.981"),
        ),
    ]
    assert _lies(zeilen) == {
        "39": (14064806, 4798412, -1779452),
        "40": (7441, 0, 0),
        "41": (4943999, -1779452, -5944981),
    }


@pytest.mark.parametrize(
    ("zeilen", "meldung"),
    [
        (
            [_zeile(200.0, *_bezeichnung(200.0, "99 - Unbekannt"), *_werte(200.0, "1", "2", "3"))],
            "unbekannte Zeilennummer",
        ),
        (
            [
                _zeile(
                    200.0,
                    *_bezeichnung(200.0, "1 - Steuern und andere Abgaben"),
                    *_werte(200.0, "1", "2", "3"),
                )
            ],
            "unerwartete Zeile|passt nicht zum Wörterbuch",
        ),
        (
            [
                _zeile(
                    200.0,
                    *_bezeichnung(200.0, "1 - Steuern und ähnliche Abgaben"),
                    *_werte(200.0, "1", "2", "3")[:2],
                )
            ],
            "1 Beträge fehlen",
        ),
        (
            [
                _zeile(
                    200.0,
                    *_bezeichnung(200.0, "1 - Steuern und ähnliche Abgaben"),
                    *_werte(200.0, "1", "2", "3"),
                ),
                _zeile(205.0, *_werte(205.0, "4", "5", "6")),
            ],
            "zwei Beträge",
        ),
        (
            [
                _zeile(
                    200.0,
                    *_bezeichnung(200.0, "1 - Steuern und ähnliche Abgaben"),
                    _wort("Text", 300.0, 309.9, 200.0),
                )
            ],
            "Betragszone",
        ),
    ],
)
def test_lies_ikvs_plantabelle_bricht_ab(zeilen: list[Textzeile], meldung: str) -> None:
    with pytest.raises(IkvsFehler, match=meldung):
        _lies(zeilen)


def test_abweichender_spaltenkopf_bricht_ab() -> None:
    with pytest.raises(IkvsFehler, match="Spaltenköpfe"):
        lies_ikvs_plantabelle(
            _kopf(),
            plantyp="gesamtfinanzplan",
            gedruckte_spalten=("Ergebnis 2023", "Ansatz 2025", "Ansatz 2026"),
            pdf_seite=80,
        )


def test_woerterbuch_zeigt_auf_kanonische_zeilen() -> None:
    for plantyp, eintraege in IKVS_ZEILEN.items():
        kanonisch = [e.kanonisch for e in eintraege]
        assert len(set(kanonisch)) == len(kanonisch)
        assert set(kanonisch) <= set(ZEILEN[plantyp])


@pytest.fixture(scope="module")
def jahrgang() -> Jahrgang:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    if jahrgang.software != "ikvs":
        pytest.skip("Standardjahrgang ist kein IKVS-Jahrgang")
    return jahrgang


@pytest.fixture(scope="module")
def gesamtplaene(jahrgang: Jahrgang) -> dict[str, pl.DataFrame]:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return {
            datei: pl.DataFrame(
                gesamtplan_datensaetze(dokument, jahrgang, datei=datei), schema=PLAN_SPALTEN
            )
            for datei in ("ergebnisplan", "finanzplan")
        }


def test_gesamtergebnisplan_trifft_sollwerte(
    jahrgang: Jahrgang, gesamtplaene: dict[str, pl.DataFrame]
) -> None:
    soll = lade_sollwerte(STANDARD_JAHR)["gesamtergebnisplan"]
    planwerte = Planwerte(gesamtplaene["ergebnisplan"], datei="ergebnisplan")
    spalten = [zerlege_spaltenkopf(kopf) for kopf in jahrgang.spalten["ergebnisplan"]]
    assert [jahr for _, jahr in spalten] == soll["jahre"]
    for zeile, werte in soll["zeilen"].items():
        ist = [planwerte.wert("GESAMT", "", zeile, jahr, wertart) for wertart, jahr in spalten]
        assert ist == werte, f"Zeile {zeile}"


def test_gesamtfinanzplan_trifft_sollwerte(
    jahrgang: Jahrgang, gesamtplaene: dict[str, pl.DataFrame]
) -> None:
    soll = lade_sollwerte(STANDARD_JAHR)["gesamtfinanzplan"]["ansatz"]
    planwerte = Planwerte(gesamtplaene["finanzplan"], datei="finanzplan")
    for zeile, wert in soll.items():
        assert planwerte.wert("GESAMT", "", zeile, jahrgang.haushaltsjahr, "ansatz") == wert


def test_gesamtplaene_vollstaendig(gesamtplaene: dict[str, pl.DataFrame]) -> None:
    """Der Gesamtergebnisplan druckt alle Zeilen, der Gesamtfinanzplan mindestens alle
    Summenzeilen (leere Einzelzeilen wie Liquiditätskredite darf er auslassen)."""
    ergebnisplan = set(gesamtplaene["ergebnisplan"]["zeile"].unique())
    assert ergebnisplan == {e.kanonisch for e in IKVS_ZEILEN["gesamtergebnisplan"]}
    finanzplan = set(gesamtplaene["finanzplan"]["zeile"].unique())
    summen = {z for z, d in ZEILEN["gesamtfinanzplan"].items() if d.ist_summe}
    assert summen <= finanzplan <= {e.kanonisch for e in IKVS_ZEILEN["gesamtfinanzplan"]}


def test_gesamtplaene_zeilenformeln_stimmen(gesamtplaene: dict[str, pl.DataFrame]) -> None:
    """Regel 1: jede Summenzeile gleich ihren Bestandteilen, auch nach Cent-Rundung."""
    ergebnis = _pruefe_regel1(
        ergebnisplan=gesamtplaene["ergebnisplan"], finanzplan=gesamtplaene["finanzplan"]
    )
    assert ergebnis.geprueft > 0
    assert ergebnis.abweichungen == ()


def test_satzung_trifft_gesamtplaene(
    jahrgang: Jahrgang, gesamtplaene: dict[str, pl.DataFrame]
) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    satzung = dict(sollwerte["satzung"])
    # Die VE druckt erst die Investitionsübersicht; der Gesamtfinanzplan hat keine VE-Spalte.
    satzung.pop("verpflichtungsermaechtigungen")
    geprueft, abweichungen = _pruefe_regel4_satzung(
        planwerte_ergebnisplan=Planwerte(gesamtplaene["ergebnisplan"], datei="ergebnisplan"),
        planwerte_finanzplan=Planwerte(gesamtplaene["finanzplan"], datei="finanzplan"),
        sollwerte={"satzung": satzung},
        haushaltsjahr=jahrgang.haushaltsjahr,
    )
    assert geprueft == len(satzung) - 1
    assert [p for p in abweichungen if abs(p.abweichung) > TOLERANZ_EURO] == []
