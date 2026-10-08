"""Tests für die IKVS-Detailschritte (Hörstel): Produktinformationen, Kennzahlen,
Erläuterungen (Schritt 03), Investitionsübersichten (Schritt 04), Haushaltsquerschnitte
und die Prüfregeln 6-8.

Die PDF-Tests laufen die öffentlichen Schritte einmal gegen ein temporäres
`daten/`-Verzeichnis. Jahrgang und Sollwerte kommen aus dem aktiven Jahrgang
(STANDARD_JAHRGAENGE_VERZEICHNIS), auch wenn conftest.py die übrigen Tests auf den
Ostbevern-Referenzjahrgang umlenkt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import polars as pl
import pytest

from ostbevern.ikvs import normalisiere, verbinde_teile
from ostbevern.ikvs_produkte import _ansatz_haushaltsjahr, _teilergebnisplan_zeilen
from ostbevern.investitionen import extrahiere_investitionen
from ostbevern.konfiguration import (
    STANDARD_JAHR,
    STANDARD_JAHRGAENGE_VERZEICHNIS,
    Jahrgang,
    lade_jahrgang,
    lade_sollwerte,
    layout_text,
)
from ostbevern.pdf import PdfDokument
from ostbevern.plaene import extrahiere_plaene
from ostbevern.produkte import extrahiere_produkte
from ostbevern.pruefung import Planwerte, _pruefe_regel6, _pruefe_regel7, _pruefe_regel8
from ostbevern.querschnitte import extrahiere_querschnitte
from ostbevern.schema import (
    ERGEBNISPLAN_CSV,
    ERLAEUTERUNGEN_CSV,
    FINANZPLAN_CSV,
    GRUNDZAHLEN_CSV,
    HIERARCHIE_CSV,
    INVESTITIONEN_CSV,
    INVESTITIONEN_PB_CSV,
    PRODUKTE_JSON,
    QUERSCHNITTE_CSV,
    SEITEN_CSV,
    VE_FAELLIGKEITEN_CSV,
    lies_erlaeuterungen_csv,
    lies_grundzahlen_csv,
    lies_hierarchie_csv,
    lies_investitionen_csv,
    lies_investitionen_pb_csv,
    lies_plan_csv,
    lies_produkte_json,
    lies_querschnitte_csv,
    lies_seiten_csv,
    lies_ve_faelligkeiten_csv,
)
from ostbevern.seiten import klassifiziere_seiten

# Regel 6: im PDF so gedruckte Abweichungen zwischen Investitionsübersichten und
# Teilfinanzplan (Schlüssel: Plan, Code, Zeile, Jahr). Produkt 0212201 (S. 196): Übersicht
# 105.000 € (2026) und 0 € (2027-2029) gegen Teilfinanzplan 108.125 € bzw. 3.125 €.
# Produkt 1557302 (S. 542/543): Teilfinanzplan Z. 23 2025 = 62.333 €, die Übersicht hat
# keine Einzahlung. Die GESAMT-Abweichungen folgen daraus, 2024 zusätzlich 2 € Rundung der
# mit Cent gedruckten Ist-Werte.
_REGEL6_BEFUNDE = {
    ("investitionen_produkt", "0212201", "30", 2026),
    ("investitionen_produkt", "0212201", "30", 2027),
    ("investitionen_produkt", "0212201", "30", 2028),
    ("investitionen_produkt", "0212201", "30", 2029),
    ("investitionen_produkt", "1557302", "23", 2025),
    ("investitionen_gesamt", "", "23", 2024),
    ("investitionen_gesamt", "", "23", 2025),
    ("investitionen_gesamt", "", "30", 2026),
    ("investitionen_gesamt", "", "30", 2027),
    ("investitionen_gesamt", "", "30", 2028),
    ("investitionen_gesamt", "", "30", 2029),
}

# Erläuterungen, deren Ansatz 2026 nicht zum gedruckten Teilergebnisplan passt (Produkt,
# Zeile, Erläuterung, Plan, Seite der Erläuterung); im PDF so gedruckt.
_ERLAEUTERUNG_BEFUNDE = {
    ("0111107", "06", 26660, 26600, 151),
    ("0111110", "02", 69630, 106130, 172),
    ("0111112", "16", 16000, 36000, 182),
    ("0842403", "27", 189000, 189500, 379),
    ("1254501", "04", 48826, 46826, 476),
    ("1254701", "05", 1000, 0, 486),
    ("1557101", "15", 145500, 151300, 531),
}

# Verpflichtungsermächtigung "Neubau eines Verwaltungsgebäudes Hörstel" (5.100 T€): Die
# VE-Übersicht (S. 586) und die Satzung (§ 3, S. 7) enthalten sie, die
# Investitionsübersicht von Maßnahme 111.02-004 (S. 124) druckt dagegen nur 250.000 €.
_VE_NUR_IN_UEBERSICHT = 5_100_000


def test_verbinde_teile() -> None:
    assert verbinde_teile(["SW- und RW-", "Kanal Energie-Inno-", "vationspark"]) == (
        "SW- und RW-Kanal Energie-Innovationspark"
    )
    assert verbinde_teile(["Grund-", "stücksverkauf", "Industrie- und", "Gewerbegebiete"]) == (
        "Grundstücksverkauf Industrie- und Gewerbegebiete"
    )


@pytest.mark.parametrize(
    ("zeile", "erwartet"),
    [
        ("Ansatz 2025 = 4.349 €, Ansatz 2026 = 200 €", 200),
        ("Ansatz 2025 = 329.083 € Ansatz 2026 = 446.802 €", 446802),
        ("Ansatz 2025 =915.590 €, Ansatz 2026 = 1.646.024 €", 1646024),
        ("Ansatz 2025 = 223.830 €, Ansatz 2026 = 235.990€", 235990),
        ("Ansatz 2025 = 442.860 €, Ansatz 2025 = 498.890 €", 498890),
        ("Ansatz 20245= 1.444.000 €, Ansatz 2026 = 1.327.000 €", 1327000),
        ("Ansatz 2024 = 290.000 €, Ansatz 2025 = 0 €", None),
    ],
)
def test_ansatz_haushaltsjahr(jahrgang: Jahrgang, zeile: str, erwartet: int | None) -> None:
    muster = re.compile(layout_text(jahrgang, "ikvs_erlaeuterungen", "ansatz_muster"))
    treffer = muster.match(zeile)
    assert treffer is not None
    assert _ansatz_haushaltsjahr(treffer, jahrgang.haushaltsjahr, 1) == erwartet


@pytest.fixture(scope="module")
def jahrgang() -> Jahrgang:
    jahrgang = lade_jahrgang(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)
    assert jahrgang.software == "ikvs"
    return jahrgang


@pytest.fixture(scope="module")
def daten(jahrgang: Jahrgang, tmp_path_factory: pytest.TempPathFactory) -> Path:
    wurzel = tmp_path_factory.mktemp("daten")
    for unter in ("zwischen", "aufbereitet"):
        (wurzel / unter).mkdir()
    klassifiziere_seiten(jahrgang, daten_wurzel=wurzel)
    extrahiere_plaene(jahrgang, daten_wurzel=wurzel)
    extrahiere_produkte(jahrgang, daten_wurzel=wurzel)
    extrahiere_investitionen(jahrgang, daten_wurzel=wurzel)
    extrahiere_querschnitte(jahrgang, daten_wurzel=wurzel)
    return wurzel


@pytest.fixture(scope="module")
def planwerte(daten: Path) -> dict[str, Planwerte]:
    return {
        "ergebnisplan": Planwerte(lies_plan_csv(daten / ERGEBNISPLAN_CSV), datei="ergebnisplan"),
        "finanzplan": Planwerte(lies_plan_csv(daten / FINANZPLAN_CSV), datei="finanzplan"),
    }


def test_querschnitte_treffen_teilplaene(
    daten: Path, jahrgang: Jahrgang, planwerte: dict[str, Planwerte]
) -> None:
    querschnitte = lies_querschnitte_csv(daten / QUERSCHNITTE_CSV)
    hierarchie = lies_hierarchie_csv(daten / HIERARCHIE_CSV)
    pg = set(hierarchie.filter(pl.col("ebene") == "PG")["code"])
    assert set(querschnitte["pg"].drop_nulls()) <= pg
    assert querschnitte.filter(pl.col("gesamtsumme")).height > 0
    ergebnis = _pruefe_regel7(
        querschnitte=querschnitte,
        planwerte_ergebnisplan=planwerte["ergebnisplan"],
        planwerte_finanzplan=planwerte["finanzplan"],
        haushaltsjahr=jahrgang.haushaltsjahr,
        nur_mit_gedruckten_komponenten=True,
    )
    assert ergebnis.geprueft > 300
    assert ergebnis.abweichungen == ()


def test_querschnitte_salden_in_sich_stimmig(daten: Path) -> None:
    """Einzahlungen - Auszahlungen = Saldo je Block (auch für Kennzahlen, die kein
    Teilfinanzplan druckt, z. B. laufende Verwaltungstätigkeit)."""
    querschnitte = lies_querschnitte_csv(daten / QUERSCHNITTE_CSV).filter(
        pl.col("plan") == "finanzplan"
    )
    for (pg,), block in querschnitte.group_by(["pg"]):
        werte = dict(zip(block["kennzahl"], block["betrag"], strict=True))
        for art in ("laufende_verwaltung", "investitionen", "finanzierung"):
            ein = werte.get(f"einzahlungen_{art}", 0)
            aus = werte.get(f"auszahlungen_{art}", 0)
            assert werte.get(f"saldo_{art}", 0) == ein - aus, (pg, art)


def test_investitionen_regel6_nur_belegte_abweichungen(
    daten: Path, jahrgang: Jahrgang, planwerte: dict[str, Planwerte]
) -> None:
    investitionen = lies_investitionen_csv(daten / INVESTITIONEN_CSV)
    assert lies_ve_faelligkeiten_csv(daten / VE_FAELLIGKEITEN_CSV).height == 0
    assert lies_investitionen_pb_csv(daten / INVESTITIONEN_PB_CSV).height == 0
    ergebnis = _pruefe_regel6(
        investitionen=investitionen,
        investitionen_pb=lies_investitionen_pb_csv(daten / INVESTITIONEN_PB_CSV),
        ve_faelligkeiten=lies_ve_faelligkeiten_csv(daten / VE_FAELLIGKEITEN_CSV),
        planwerte_finanzplan=planwerte["finanzplan"],
        hierarchie=lies_hierarchie_csv(daten / HIERARCHIE_CSV),
        jahrgang=jahrgang,
    )
    assert ergebnis.luecken == ()
    gefunden = {(p.plan, p.code, p.zeile, p.jahr) for p in ergebnis.abweichungen}
    assert gefunden == _REGEL6_BEFUNDE


def test_verpflichtungsermaechtigungen_gegen_satzung(daten: Path) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)
    investitionen = lies_investitionen_csv(daten / INVESTITIONEN_CSV)
    ve = investitionen.filter(pl.col("wertart") == "ve")["betrag"].sum()
    assert ve + _VE_NUR_IN_UEBERSICHT == sollwerte["satzung"]["verpflichtungsermaechtigungen"]


def test_produkte_vollstaendig_regel8(
    daten: Path, jahrgang: Jahrgang, planwerte: dict[str, Planwerte]
) -> None:
    produkte = lies_produkte_json(daten / PRODUKTE_JSON)
    assert len(produkte) == jahrgang.anzahlen.produkte
    ergebnis = _pruefe_regel8(
        produkte=produkte,
        ergebnisplan=lies_plan_csv(daten / ERGEBNISPLAN_CSV),
        finanzplan=lies_plan_csv(daten / FINANZPLAN_CSV),
        hierarchie=lies_hierarchie_csv(daten / HIERARCHIE_CSV),
        jahrgang=jahrgang,
    )
    assert ergebnis.luecken == ()


def test_keine_personennamen(daten: Path, jahrgang: Jahrgang) -> None:
    """D-09: Die Namen unter "Produktverantwortlicher" stehen in keiner erzeugten Datei."""
    beschriftung = layout_text(jahrgang, "ikvs_produktinformationen", "verantwortlich")
    seiten = lies_seiten_csv(daten / SEITEN_CSV).filter(pl.col("typ") == "produktinformationen")
    namen: set[str] = set()
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        for pdf_seite in seiten["pdf_seite"]:
            texte = [z.text for z in dokument.zeilen(pdf_seite)]
            if beschriftung in texte:
                namen.add(texte[texte.index(beschriftung) + 1])
    assert len(namen) > 10
    nachnamen = {name.split(",")[0].strip() for name in namen}
    inhalt = "\n".join(
        (daten / pfad).read_text(encoding="utf-8")
        for pfad in (PRODUKTE_JSON, GRUNDZAHLEN_CSV, ERLAEUTERUNGEN_CSV)
    )
    gefunden = {name for name in nachnamen if re.search(rf"\b{re.escape(name)}\b", inhalt)}
    assert gefunden == set()


def test_kennzahlen_stichprobe(daten: Path) -> None:
    """S. 116: Produkt 0111101, Vollzeitstellen Plan 2026 = 2,78; Kennzahl Ist 2024."""
    grundzahlen = lies_grundzahlen_csv(daten / GRUNDZAHLEN_CSV)
    stellen = grundzahlen.filter(
        (pl.col("produkt") == "0111101")
        & (pl.col("gruppe") == "Stellenplan")
        & (pl.col("jahr") == 2026)
    )
    assert stellen["bezeichnung"].to_list() == ["Anzahl der Vollzeitstellen"]
    assert stellen["wert"].to_list() == [2.78]
    ist = grundzahlen.filter(
        (pl.col("produkt") == "0111101") & (pl.col("jahr") == 2024) & pl.col("hinweis").is_null()
    )
    assert 221311.96 in ist["wert"].to_list()


def test_erlaeuterungen_ansaetze_wie_teilplan(daten: Path, planwerte: dict[str, Planwerte]) -> None:
    """Die Überschrift einer Teilergebnisplan-Zeile trägt deren Ansatz 2026; abweichend nur
    die im PDF so gedruckten Fälle."""
    erlaeuterungen = lies_erlaeuterungen_csv(daten / ERLAEUTERUNGEN_CSV)
    zeilen = dict(_teilergebnisplan_zeilen())
    produkte = json.loads((daten / PRODUKTE_JSON).read_text(encoding="utf-8"))
    assert all(p["erlaeuterungen"] for p in produkte)
    geprueft = 0
    abweichend: set[tuple[str, str, int, int, int]] = set()
    for zeile in erlaeuterungen.filter(
        pl.col("betrag").is_not_null() & pl.col("zu_zeilen").is_not_null()
    ).iter_rows(named=True):
        if zeilen.get(normalisiere(zeile["text"])) != zeile["zu_zeilen"] and not any(
            k.startswith(normalisiere(zeile["text"])) and v == zeile["zu_zeilen"]
            for k, v in zeilen.items()
        ):
            continue  # Sachkonto-Überschrift innerhalb des Blocks
        geprueft += 1
        plan = planwerte["ergebnisplan"].wert(
            "P", zeile["produkt"], zeile["zu_zeilen"], 2026, "ansatz"
        )
        if abs(plan) != abs(zeile["betrag"]):
            abweichend.add(
                (zeile["produkt"], zeile["zu_zeilen"], zeile["betrag"], plan, zeile["pdf_seite"])
            )
    assert geprueft > 300
    assert abweichend == _ERLAEUTERUNG_BEFUNDE
