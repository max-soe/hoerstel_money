"""Tests für die Hörsteler Erklärtexte und das Glossar (Phase 11, Plan 11-04).

Die Texte liegen im Projekt-`daten/manuell/texte/` (conftest.py lenkt die übrigen Tests auf
den Ostbevern-Referenzstand um). Hier wird das Format geprüft und dass die Schlüsselmengen zu
denen passen, die die App erwartet; dass jeder Platzhalter auflöst, prüft Schritt 07 im
Gesamtlauf (Plan 11-05).
"""

from __future__ import annotations

import pytest

from ostbevern.konfiguration import PROJEKT_WURZEL
from ostbevern.schema import ERKLAERUNGEN_MD, GLOSSAR_MD
from ostbevern.texte import ABGELEITET, TexteFehler, lies_erklaerungen, lies_glossar, pruefe_text

_DATEN = PROJEKT_WURZEL / "daten"

# Schlüssel, die die App über `ErklaerText`/`drilldown.ts` anfragt (Stand v1.0), und
# GLOSSAR_SCHLUESSEL aus app/src/lib/glossar.ts.
_ERKLAERTEXTE = {
    "schluesselzuweisung",
    "gewerbesteuer",
    "kreisumlage",
    "grundsteuer_hebesaetze",
    "sonderposten",
    "globaler_minderaufwand",
    "defizit_ruecklagen",
    "schulden",
    "verpflichtungsermaechtigungen",
    "nicht_im_haushalt",
    "nicht_im_haushalt_ausgaben",
    "nicht_im_haushalt_einnahmen",
    "nicht_im_haushalt_kurz",
    "steuern_selbst_festgelegt",
    "zuwendungen_laufende_zwecke",
    "ueberschuss_pb_16",
    "ueberschuss_pb_11",
    "ueberschuss_allgemein",
    "ueberschuss_ruecklage",
    "geldfluss_lesehilfe",
    "bindungsgrad_selbstauskunft",
    "ueberschuss_produkte",
    "polster",
    "schulden_anstieg",
}
_GLOSSAR = {
    "ergebnisplan",
    "finanzplan",
    "ertrag_aufwand",
    "einzahlung_auszahlung",
    "produkt",
    "produktgruppe",
    "produktbereich",
    "transferaufwendungen",
    "kreisumlage",
    "jugendamtsumlage",
    "gewerbesteuerumlage",
    "schluesselzuweisung",
    "hebesatz",
    "sonderposten",
    "abschreibungen",
    "globaler_minderaufwand",
    "ausgleichsruecklage",
    "allgemeine_ruecklage",
    "verpflichtungsermaechtigung",
    "bindungsgrad",
    "zuschussbedarf",
    "nkf",
    "haushaltssicherung",
    "wertart",
    "nicht_im_haushalt",
    "vzae",
    "entgeltgruppen",
}


def test_erklaertexte_hoerstel() -> None:
    texte = lies_erklaerungen(_DATEN / ERKLAERUNGEN_MD)
    assert {text.schluessel for text in texte} == _ERKLAERTEXTE
    for text in texte:
        for absatz in text.absaetze:
            pruefe_text(absatz)
            assert "Ostbevern" not in absatz and "Warendorf" not in absatz


def test_glossar_hoerstel() -> None:
    begriffe = lies_glossar(_DATEN / GLOSSAR_MD)
    assert {begriff.schluessel for begriff in begriffe} == _GLOSSAR
    for begriff in begriffe:
        for absatz in begriff.absaetze:
            pruefe_text(absatz)
            assert "Ostbevern" not in absatz and "Warendorf" not in absatz


# Eigenkapitalübersicht Hörstel (S. 588), Stände zum 31.12. vor Ergebnisverrechnung, Euro.
_EIGENKAPITAL_HOERSTEL = {
    "jahr.haushaltsjahr": 2026,
    "jahr.vorjahr": 2025,
    "jahr.letztes_jahr": 2029,
    **{
        f"eigenkapital.ausgleichsruecklage.{jahr}": wert
        for jahr, wert in zip(
            range(2024, 2030),
            [19809852, 20219358, 12243578, 9503248, 7914979, 4339938],
            strict=True,
        )
    },
    **{
        f"eigenkapital.jahresergebnis.{jahr}": wert
        for jahr, wert in zip(
            range(2024, 2030),
            [409507, -7975780, -2740330, -1588269, -3575041, -5014196],
            strict=True,
        )
    },
    **{f"eigenkapital.allgemeine_ruecklage.{jahr}": 50844885 for jahr in range(2026, 2030)},
}


def test_ausgleichsruecklage_aufgebraucht_vor_verrechnung() -> None:
    """Vorbericht S. 72: „Die Ausgleichsrücklage wird … in 2029 aufgebraucht sein“."""
    formel = ABGELEITET["ausgleichsruecklage_aufgebraucht_jahr_vor_verrechnung"]
    assert formel(_EIGENKAPITAL_HOERSTEL) == 2029


def test_allgemeine_ruecklage_ende_vor_verrechnung() -> None:
    """S. 588 nachrichtlich: Veränderung der allgemeinen Rücklage 2029 −674.257,92 €; die
    Summe Eigenkapital 2029 ist 50.170.627,51 €."""
    formel = ABGELEITET["allgemeine_ruecklage_ende_letztes_jahr_vor_verrechnung"]
    assert formel(_EIGENKAPITAL_HOERSTEL) == 50844885 - 674258


def test_ausgleichsruecklage_reicht_bricht_ab() -> None:
    werte = dict(_EIGENKAPITAL_HOERSTEL)
    werte["eigenkapital.ausgleichsruecklage.2029"] = 6000000
    with pytest.raises(TexteFehler, match="reicht bis zum letzten Planjahr"):
        ABGELEITET["ausgleichsruecklage_aufgebraucht_jahr_vor_verrechnung"](werte)


def test_schluesselzuweisung_anstieg() -> None:
    werte = {
        "jahr.haushaltsjahr": 2026,
        "vorbericht.zuwendungen.schluesselzuweisung.2025": 3034000,
        "vorbericht.zuwendungen.schluesselzuweisung.2026": 4478000,
    }
    assert ABGELEITET["schluesselzuweisung_anstieg_haushaltsjahr"](werte) == 1444000
