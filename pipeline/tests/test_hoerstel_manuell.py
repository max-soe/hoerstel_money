"""Tests für die manuellen Hörsteler Vorberichtsdaten (Phase 11, Plan 11-03).

Die Daten liegen im Projekt-`daten/manuell/` (conftest.py lenkt die übrigen Tests auf den
Ostbevern-Referenzstand um) und werden deshalb über PROJEKT_WURZEL gelesen; Jahrgang und
Sollwerte kommen aus STANDARD_JAHRGAENGE_VERZEICHNIS. Die Prüfungen gegen Gesamt- und
Teilpläne laufen in Plan 11-05 mit `pruefe_alles`, sobald `daten/aufbereitet/` Hörstel enthält.
"""

from __future__ import annotations

import polars as pl
import pytest

from ostbevern.ikvs_investitionen import IkvsVeFehler, ve_faelligkeiten_aus_uebersicht
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    STANDARD_JAHRGAENGE_VERZEICHNIS,
    Jahrgang,
    lade_jahrgang,
    lade_sollwerte,
    layout_liste,
)
from ostbevern.manuell import lies_meta_json, schuldenstand_euro
from ostbevern.pruefung import (
    _pruefe_regel5_eigenkapital_summe,
    _pruefe_regel5_fraktionszuwendungen,
    lies_vorberichtstabellen,
    pruefe_eckwerte_konsumiert,
    validiere_ve_uebersicht,
    weitergabe_posten,
)
from ostbevern.schema import (
    EIGENKAPITAL_CSV,
    FRAKTIONSZUWENDUNGEN_CSV,
    INVESTITIONEN_SPALTEN,
    META_JSON,
    VE_UEBERSICHT_CSV,
    VERBINDLICHKEITEN_CSV,
    lies_eigenkapital_csv,
    lies_ve_uebersicht_csv,
    lies_vorbericht_csv,
)

_DATEN = PROJEKT_WURZEL / "daten"

# Gedruckte Summen, die nicht der Summe ihrer Posten entsprechen (Befunde, T€):
# (tabelle, jahr) -> Σ Posten − gedruckte Summe.
_SUMMEN_BEFUNDE = {
    ("leistungsentgelte", 2025): 1,  # S. 24, Rundung
    ("sonstige_aufwendungen", 2026): 1,  # S. 37, Rundung
    ("verbindlichkeiten", 2026): 180,  # S. 587, Summe 56.535 statt 56.715
}

# Teilergebnisplan 1661101 Z. 15 (S. 557), Euro: Weitergabe an Kreis und Land.
_TP_1661101_Z15 = {
    2024: 20701460,
    2025: 22599653,
    2026: 23994000,
    2027: 23820000,
    2028: 24739000,
    2029: 25618000,
}


@pytest.fixture(scope="module")
def jahrgang() -> Jahrgang:
    return lade_jahrgang(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)


@pytest.fixture(scope="module")
def vorbericht(jahrgang: Jahrgang) -> dict[str, pl.DataFrame]:
    tabellen = lies_vorberichtstabellen(_DATEN, jahrgang)
    tabellen["verbindlichkeiten"] = lies_vorbericht_csv(_DATEN / VERBINDLICHKEITEN_CSV).filter(
        pl.col("tabelle") == "verbindlichkeiten"
    )
    return tabellen


def test_tabellenmenge(jahrgang: Jahrgang, vorbericht: dict[str, pl.DataFrame]) -> None:
    assert list(vorbericht) == [
        "steuerarten",
        "zuwendungen",
        "transferaufwendungen",
        "investitionszuwendungen",
        "leistungsentgelte",
        "privatrechtliche_leistungsentgelte",
        "personal",
        "sachaufwand",
        "sonstige_aufwendungen",
        "sonstige_ertraege",
        "verbindlichkeiten",
    ]
    assert not (_DATEN / "manuell" / "kita_zuschuesse.csv").exists()


def test_summen_je_tabelle_und_jahr(vorbericht: dict[str, pl.DataFrame]) -> None:
    """Je (Tabelle, Jahr) genau eine Gesamtzeile; Σ Posten = Gesamt außer den Befunden."""
    gefunden = {}
    for tabelle, df in vorbericht.items():
        for jahr in sorted(df["jahr"].unique().to_list()):
            jahr_df = df.filter(pl.col("jahr") == jahr)
            gesamt = jahr_df.filter(pl.col("ist_gesamt"))["betrag_teur"].to_list()
            assert len(gesamt) == 1, (tabelle, jahr)
            differenz = jahr_df.filter(~pl.col("ist_gesamt"))["betrag_teur"].sum() - gesamt[0]
            if differenz:
                gefunden[(tabelle, jahr)] = differenz
    assert gefunden == _SUMMEN_BEFUNDE


def test_berechnete_posten_sind_markiert(vorbericht: dict[str, pl.DataFrame]) -> None:
    """Restposten (gedruckte Summe minus einzeln gedruckte Posten) tragen `berechnet` in der
    Anmerkung; jeder `uebrige_*`-Posten ist berechnet."""
    for tabelle, df in vorbericht.items():
        uebrige = df.filter(pl.col("posten").str.starts_with("uebrige_"))
        for zeile in uebrige.iter_rows(named=True):
            assert zeile["anmerkung"].startswith("berechnet"), (tabelle, zeile["posten"])


def test_weitergabe_gegen_teilergebnisplan(
    jahrgang: Jahrgang, vorbericht: dict[str, pl.DataFrame]
) -> None:
    """Kreis-, Jugendamts- und Gewerbesteuerumlage ergeben TP 1661101 Z. 15 je Jahr (±1 T€ je
    Posten, die Gewerbesteuerumlage 2025/2026 ist gedruckt, sonst berechnet)."""
    posten = weitergabe_posten(jahrgang)
    assert posten == ("kreisumlage", "jugendamtsumlage", "gewerbesteuerumlage")
    transfer = vorbericht["transferaufwendungen"].filter(pl.col("posten").is_in(list(posten)))
    for jahr, soll in _TP_1661101_Z15.items():
        ist = transfer.filter(pl.col("jahr") == jahr)["betrag_teur"].sum() * 1000
        assert abs(ist - soll) <= len(posten) * 1000, jahr
    # S. 33: Allgemeine Umlagen = Kreisumlage + Jugendamtsumlage (S. 34)
    allgemeine_umlagen = {2025: 21156, 2026: 22667}
    for jahr, soll in allgemeine_umlagen.items():
        umlagen = transfer.filter(
            (pl.col("jahr") == jahr) & pl.col("posten").is_in(["kreisumlage", "jugendamtsumlage"])
        )
        assert umlagen["betrag_teur"].sum() == soll


def test_meta_json() -> None:
    meta = lies_meta_json(_DATEN / META_JSON)
    assert meta["einwohner"]["wert"] == 20166
    assert "kreisumlage" not in meta
    assert {k: v["wert"] for k, v in meta["hebesaetze"].items()} == {
        "grundsteuer_a": 312,
        "grundsteuer_b": 800,
        "gewerbesteuer": 421,
    }


def test_eckwerte_konsumiert_und_satzung_paragraf4() -> None:
    eckwerte = lade_sollwerte(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)[
        "eckwerte"
    ]
    pruefe_eckwerte_konsumiert(eckwerte)
    eigenkapital = lies_eigenkapital_csv(_DATEN / EIGENKAPITAL_CSV)
    ausgleich = dict(
        eigenkapital.filter(pl.col("posten") == "ausgleichsruecklage")
        .select("jahr", "betrag")
        .iter_rows()
    )
    assert (
        ausgleich[STANDARD_JAHR] - ausgleich[STANDARD_JAHR + 1]
        == eckwerte["verringerung_ausgleichsruecklage"]["wert"]
    )


def test_eigenkapital_und_fraktionszuwendungen_summen() -> None:
    _geprueft, abweichungen = _pruefe_regel5_eigenkapital_summe(
        eigenkapital=lies_eigenkapital_csv(_DATEN / EIGENKAPITAL_CSV)
    )
    assert abweichungen == []
    geprueft, abweichungen = _pruefe_regel5_fraktionszuwendungen(
        fraktionszuwendungen=lies_eigenkapital_csv(_DATEN / FRAKTIONSZUWENDUNGEN_CSV)
    )
    assert (geprueft, abweichungen) == (3, [])


def test_ve_uebersicht_gleich_satzung() -> None:
    ve = lies_ve_uebersicht_csv(_DATEN / VE_UEBERSICHT_CSV)
    validiere_ve_uebersicht(ve)
    gesamt = ve.filter(pl.col("ist_gesamt") & pl.col("faellig_jahr").is_null())
    satzung = lade_sollwerte(STANDARD_JAHR, verzeichnis=STANDARD_JAHRGAENGE_VERZEICHNIS)["satzung"]
    assert gesamt["betrag_teur"].to_list() == [18331]
    assert satzung["verpflichtungsermaechtigungen"] == 18331000


def test_schuldenstand_nur_investitionskredite(jahrgang: Jahrgang) -> None:
    posten = layout_liste(jahrgang, "schulden", "posten")
    verbindlichkeiten = lies_vorbericht_csv(_DATEN / VERBINDLICHKEITEN_CSV)
    assert schuldenstand_euro(verbindlichkeiten, 2025, posten) == 28345000


def _ve_investitionen(*zeilen: tuple[str, str, int]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "produkt": produkt,
                "massnahme_id": massnahme_id,
                "massnahme_name": massnahme_id,
                "konto": None,
                "konto_name": None,
                "richtung": "auszahlung",
                "art": None,
                "jahr": 2026,
                "wertart": "ve",
                "betrag": betrag,
                "pdf_seite": 1,
            }
            for produkt, massnahme_id, betrag in zeilen
        ],
        schema=INVESTITIONEN_SPALTEN,
    )


def test_ve_faelligkeiten_aus_uebersicht() -> None:
    """Die VE-Fälligkeiten (S. 586) werden der Maßnahme mit gleicher VE zugeordnet; der
    Neubau des Verwaltungsgebäudes (5.100 T€) hat keine Maßnahme mit dieser VE."""
    ve = lies_ve_uebersicht_csv(_DATEN / VE_UEBERSICHT_CSV)
    investitionen = _ve_investitionen(
        ("0111102", "111.02-004", 250000), ("0212601", "126.01-005", 650000)
    )
    faellig = ve_faelligkeiten_aus_uebersicht(ve, investitionen)
    assert faellig["betrag"].sum() == 18331000
    feuerwehr = faellig.filter(pl.col("produkt") == "0212601")
    assert feuerwehr.select("massnahme_id", "jahr", "betrag").rows() == [
        ("126.01-005", 2027, 325000),
        ("126.01-005", 2029, 325000),
    ]
    neubau = faellig.filter(pl.col("betrag") == 5100000)
    assert neubau["massnahme_id"].to_list() == [None]


def test_ve_faelligkeiten_mehrdeutig_bricht_ab() -> None:
    ve = lies_ve_uebersicht_csv(_DATEN / VE_UEBERSICHT_CSV)
    investitionen = _ve_investitionen(
        ("0212601", "126.01-005", 650000), ("0212601", "126.01-099", 650000)
    )
    with pytest.raises(IkvsVeFehler, match="mehrere Maßnahmen"):
        ve_faelligkeiten_aus_uebersicht(ve, investitionen)
