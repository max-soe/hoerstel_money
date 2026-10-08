---
phase: 11-manuelle-daten-und-app-daten-hoerstel
plan: 02
subsystem: pipeline
tags: [ikvs, hoerstel, stellenplan, manuell, regel-10]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 11-manuelle-daten-und-app-daten-hoerstel
    provides: "11-01: Projekt-daten/ frei für Hörstel"
provides:
  - "daten/manuell/stellenplan.csv: Teil A (Beamte), Teil B (Tarif, Sozial- und Erziehungsdienst), Nachwuchskräfte (S. 568, 569, 574), STELLENPLAN_SPALTEN-Format ohne Produktbereich"
  - "daten/manuell/stellenuebersicht.csv: Stellenübersichten je Produkt mit gedruckten Summen (S. 570-573)"
  - "ostbevern/ikvs_stellenplan.py: Gegenprobe der Abschrift, Summierung je Produktbereich"
  - "ostbevern/stellenplan.py: Schritt 05 verzweigt für software = ikvs"
  - "schema.py: STELLENPLAN_MANUELL_CSV, STELLENUEBERSICHT_CSV, STELLENUEBERSICHT_SPALTEN"
  - "tests/test_ikvs_stellenplan.py: 7 Tests"
affects: [11-05]
---

# 11-02: Stellenplan Hörstel

## Ergebnis

- Der Stellenplan ist im Hörsteler PDF nur als Bild gedruckt. Er wurde von den gerenderten Seiten abgeschrieben: Teil A 19,81 Stellen (2026), Teil B 105,21 Stellen (inkl. S 12 und S 11b), 13 vorgesehene Nachwuchskräfte, dazu die Stellenübersichten je Produkt (47 Produkte mit Beamten-, 59 mit Tarifstellen, zusammen 60 der 69 Produkte).
- Gegenproben der Abschrift: jede Produktsumme exakt, jede Gesamtsumme gleich der Summe der gedruckten Spaltensummen, die gedruckten Spaltensummen gleich Teil A/B.
- Schritt 05 schreibt `aufbereitet/stellenplan.csv` (224 Zeilen) im ProFIS+-Format: Teil A/B und Nachwuchs ohne Produktbereich, die Übersicht je Produktbereich summiert.

## Befunde des PDF (für die Hörsteler `befunde.md`)

Die Zellen der Stellenübersicht sind auf Hundertstel gerundet, die gedruckten Spaltensummen offenbar aus ungerundeten Anteilen gebildet. In 11 Spalten ergibt die Summe der Zellen nicht die Spaltensumme (und damit nicht Teil A/B). Regel 10 meldet genau diese Gruppen:

| Teil | Gruppe | Σ Zellen | gedruckt (= Teil A/B) | Seite |
|---|---|---|---|---|
| Beamte | A14 | 2,04 | 2,00 | 570/571 |
| Beamte | A12 | 3,77 | 3,75 | 570/571 |
| Beamte | A11 | 2,35 | 2,34 | 570/571 |
| Beamte | A10 | 5,22 | 5,21 | 570/571 |
| Beamte | A9Z | 2,80 | 2,78 | 570/571 |
| Tarif | EG 9c | 6,57 | 6,59 | 572/573 |
| Tarif | EG 9b | 8,94 | 8,92 | 572/573 |
| Tarif | EG 8 | 5,98 | 5,99 | 572/573 |
| Tarif | EG 7 | 12,98 | 12,97 | 572/573 |
| Tarif | EG 6 | 33,13 | 33,12 | 572/573 |
| Tarif | EG 5 | 7,86 | 7,85 | 572/573 |

## Entscheidungen

- **Abschrift je Produkt, Summierung im Code:** Hörstel gliedert die Übersicht nach Produkten, nicht nach Produktbereichen. Die Abschrift bleibt wie gedruckt, Schritt 05 summiert über die Hierarchie.
- **Rundungstoleranz nur in der Gegenprobe der Abschrift** (½ Hundertstel je Zelle). Regel 10 bleibt exakt; die Differenzen werden als Befunde belegt.
- **Fraktionszuwendungen und Eigenkapital** (ebenfalls Bildseiten) folgen mit den Vorberichtstabellen in 11-03, weil sie dort im Datenmodell liegen.
