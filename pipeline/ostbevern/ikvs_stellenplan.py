"""Schritt 05 im IKVS-Layout (Hörstel, Phase 11, HOE-10): Stellenplan aus der Abschrift.

Das Hörsteler PDF druckt Stellenplan, Stellenübersichten und Nachwuchskräfte nur als Bild
ohne Textebene (S. 568-574). Die Werte sind deshalb von Hand abgeschrieben:

- `manuell/stellenplan.csv`: Teil A (Beamte), Teil B (Tarif, Sozial- und Erziehungsdienst)
  und Nachwuchskräfte im Format von `aufbereitet/stellenplan.csv`, ohne Produktbereich.
- `manuell/stellenuebersicht.csv`: die Stellenübersichten je Produkt mit allen gedruckten
  Summen (je Produkt, je Spalte, gesamt).

Die Abschrift wird hier gegen ihre eigenen gedruckten Summen geprüft. Die Zellen der
Übersicht sind auf Hundertstel gerundet, die Spaltensummen offenbar aus ungerundeten
Anteilen gebildet; je Spalte ist deshalb eine Abweichung bis zu ½ Hundertstel je Zelle
zulässig (Befund, Regel 10). Je Produkt stimmen Zellen und Produktsumme exakt.

Das Ergebnis hat dasselbe Format wie im ProFIS+-Layout: Teil A/B ohne Produktbereich und die
Übersicht je Produktbereich summiert (Position und Teil der Gruppe aus Teil A/B).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang
from ostbevern.schema import (
    HIERARCHIE_CSV,
    STELLENPLAN_MANUELL_CSV,
    STELLENPLAN_SPALTEN,
    STELLENUEBERSICHT_CSV,
    lies_hierarchie_csv,
    lies_stellenplan_csv,
    lies_stellenuebersicht_csv,
)

# Tabelle der Stellenübersicht, in der ein Teil gedruckt ist (Produkt- und Gesamtsummen
# tragen den Tabellennamen).
_TABELLE = {"beamte": "beamte", "tarif": "tarif", "sozial_erziehungsdienst": "tarif"}


class IkvsStellenplanFehler(ValueError):
    """Die Stellenplan-Abschrift ist unvollständig oder widerspricht ihren Summen."""


@dataclass(frozen=True)
class Rundungsdifferenz:
    """Spalte der Stellenübersicht, deren Zellen nicht exakt die gedruckte Summe ergeben."""

    teil: str
    gruppe: str
    summe_zellen: int
    gedruckt: int
    zellen: int


def _produktbereiche(hierarchie: pl.DataFrame) -> dict[str, str]:
    """Produktcode → PB-Code über die Elternkette der Hierarchie."""
    eltern = {z["code"]: (z["ebene"], z["eltern_code"]) for z in hierarchie.iter_rows(named=True)}
    ergebnis: dict[str, str] = {}
    for code, (ebene, _) in eltern.items():
        if ebene != "P":
            continue
        aktuell = code
        while aktuell in eltern and eltern[aktuell][0] != "PB":
            aktuell = eltern[aktuell][1]
        if aktuell in eltern:
            ergebnis[code] = aktuell
    return ergebnis


def pruefe_stellenuebersicht(uebersicht: pl.DataFrame) -> list[Rundungsdifferenz]:
    """Prüft die Abschrift gegen ihre gedruckten Summen und gibt die Spalten mit
    Rundungsdifferenz zurück. Bricht ab, wenn eine Produktsumme nicht exakt stimmt, eine
    Spalte mehr als ½ Hundertstel je Zelle abweicht oder die Gesamtsumme nicht der Summe
    der Spaltensummen entspricht."""
    zellen = uebersicht.filter(~pl.col("ist_summe"))
    summen = uebersicht.filter(pl.col("ist_summe"))
    if zellen.filter(pl.col("produkt").is_null() | pl.col("gruppe").is_null()).height:
        raise IkvsStellenplanFehler("Stellenübersicht: Zelle ohne Produkt oder Gruppe")
    unbekannt = set(uebersicht["teil"]) - set(_TABELLE)
    if unbekannt:
        raise IkvsStellenplanFehler(f"Stellenübersicht: unbekannte Teile {sorted(unbekannt)}")

    je_produkt: dict[tuple[str, str], int] = defaultdict(int)
    je_spalte: dict[tuple[str, str], list[int]] = defaultdict(list)
    for z in zellen.iter_rows(named=True):
        je_produkt[(_TABELLE[z["teil"]], z["produkt"])] += z["stellen_hundertstel"]
        je_spalte[(z["teil"], z["gruppe"])].append(z["stellen_hundertstel"])

    produktsummen = {
        (z["teil"], z["produkt"]): z["stellen_hundertstel"]
        for z in summen.filter(pl.col("produkt").is_not_null()).iter_rows(named=True)
    }
    if set(produktsummen) != set(je_produkt):
        raise IkvsStellenplanFehler(
            "Stellenübersicht: Produkte ohne Summe oder Summe ohne Zellen: "
            f"{sorted(set(produktsummen) ^ set(je_produkt))}"
        )
    for schluessel, gedruckt in produktsummen.items():
        if je_produkt[schluessel] != gedruckt:
            raise IkvsStellenplanFehler(
                f"Stellenübersicht {schluessel}: Zellen {je_produkt[schluessel]}, "
                f"gedruckte Summe {gedruckt} (Hundertstel)"
            )

    spaltensummen = {
        (z["teil"], z["gruppe"]): z["stellen_hundertstel"]
        for z in summen.filter(
            pl.col("produkt").is_null() & pl.col("gruppe").is_not_null()
        ).iter_rows(named=True)
    }
    fehlend = set(je_spalte) - set(spaltensummen)
    if fehlend:
        raise IkvsStellenplanFehler(f"Stellenübersicht: Spalten ohne Summe {sorted(fehlend)}")
    differenzen: list[Rundungsdifferenz] = []
    for (teil, gruppe), gedruckt in sorted(spaltensummen.items()):
        werte = je_spalte.get((teil, gruppe), [])
        differenz = sum(werte) - gedruckt
        if 2 * abs(differenz) > len(werte):
            raise IkvsStellenplanFehler(
                f"Stellenübersicht {teil}/{gruppe}: Zellen {sum(werte)}, gedruckte "
                f"Spaltensumme {gedruckt} (mehr als Rundung bei {len(werte)} Zellen)"
            )
        if differenz:
            differenzen.append(Rundungsdifferenz(teil, gruppe, sum(werte), gedruckt, len(werte)))

    gesamtsummen = summen.filter(pl.col("produkt").is_null() & pl.col("gruppe").is_null())
    for z in gesamtsummen.iter_rows(named=True):
        spalten = sum(
            wert for (teil, _), wert in spaltensummen.items() if _TABELLE[teil] == z["teil"]
        )
        if spalten != z["stellen_hundertstel"]:
            raise IkvsStellenplanFehler(
                f"Stellenübersicht {z['teil']}: Spaltensummen {spalten}, gedruckte "
                f"Gesamtsumme {z['stellen_hundertstel']}"
            )
    if set(gesamtsummen["teil"]) != {_TABELLE[teil] for teil, _ in spaltensummen}:
        raise IkvsStellenplanFehler("Stellenübersicht: Gesamtsumme je Tabelle fehlt")
    return differenzen


def baue_stellenplan(
    teil_ab: pl.DataFrame,
    uebersicht: pl.DataFrame,
    hierarchie: pl.DataFrame,
    *,
    haushaltsjahr: int,
) -> pl.DataFrame:
    """Teil A/B und Nachwuchs aus der Abschrift, dazu die Stellenübersicht je Produkt-
    bereich summiert (merkmal `stellen`, Haushaltsjahr), im STELLENPLAN_SPALTEN-Format."""
    if teil_ab.filter(pl.col("produktbereich").is_not_null()).height:
        raise IkvsStellenplanFehler("manuell/stellenplan.csv: Produktbereich ist dort leer")
    pruefe_stellenuebersicht(uebersicht)

    positionen = {
        (z["teil"], z["gruppe"]): z["position"]
        for z in teil_ab.filter(
            (pl.col("merkmal") == "stellen") & (pl.col("jahr") == haushaltsjahr)
        ).iter_rows(named=True)
    }
    pb_von = _produktbereiche(hierarchie)

    summen: dict[tuple[str, str, str], int] = defaultdict(int)
    seiten: dict[tuple[str, str, str], int] = {}
    for z in uebersicht.filter(~pl.col("ist_summe")).iter_rows(named=True):
        if z["produkt"] not in pb_von:
            raise IkvsStellenplanFehler(f"Stellenübersicht: Produkt {z['produkt']} unbekannt")
        if (z["teil"], z["gruppe"]) not in positionen:
            raise IkvsStellenplanFehler(
                f"Stellenübersicht: Gruppe {z['teil']}/{z['gruppe']} fehlt in Teil A/B "
                f"{haushaltsjahr}"
            )
        schluessel = (z["teil"], z["gruppe"], pb_von[z["produkt"]])
        summen[schluessel] += z["stellen_hundertstel"]
        seiten[schluessel] = min(seiten.get(schluessel, z["pdf_seite"]), z["pdf_seite"])

    uebersicht_zeilen = [
        {
            "teil": teil,
            "position": positionen[(teil, gruppe)],
            "gruppe": gruppe,
            "produktbereich": pb,
            "merkmal": "stellen",
            "jahr": haushaltsjahr,
            "stellen_hundertstel": wert,
            "pdf_seite": seiten[(teil, gruppe, pb)],
        }
        for (teil, gruppe, pb), wert in summen.items()
    ]
    return pl.concat(
        [teil_ab, pl.DataFrame(uebersicht_zeilen, schema=STELLENPLAN_SPALTEN)],
        how="vertical",
    )


def lies_ikvs_stellenplan(jahrgang: Jahrgang, *, daten_wurzel: Path) -> pl.DataFrame:
    """Liest Abschrift und Hierarchie aus `daten_wurzel` und baut den Stellenplan."""
    return baue_stellenplan(
        lies_stellenplan_csv(daten_wurzel / STELLENPLAN_MANUELL_CSV),
        lies_stellenuebersicht_csv(daten_wurzel / STELLENUEBERSICHT_CSV),
        lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV),
        haushaltsjahr=jahrgang.haushaltsjahr,
    )
