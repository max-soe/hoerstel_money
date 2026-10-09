---
phase: 11-manuelle-daten-und-app-daten-hoerstel
plan: 03
subsystem: pipeline
tags: [hoerstel, vorbericht, manuell, regel-5, regel-9, konfiguration]
documented: "von Hand, ohne GSD-Befehle (Plan: 11-03-PLAN.md)"

requires:
  - phase: 11-manuelle-daten-und-app-daten-hoerstel
    provides: "11-01: Projekt-daten/ frei für Hörstel; 11-02: Stellenplan"
provides:
  - "daten/manuell/: Hörsteler Vorberichtstabellen (steuerarten, zuwendungen, transferaufwendungen, investitionszuwendungen, weitere_vorberichtstabellen), verbindlichkeiten, ve_uebersicht, eigenkapital (Bild S. 588), fraktionszuwendungen (Bild S. 576/577, neu), meta.json, README"
  - "jahrgaenge/2026_sollwerte.toml: [eckwerte] für Hörstel (Regel 5 § 4, Regel 9)"
  - "[layout.vorbericht], [layout.weitergabe_kreis_land] posten/namen, [layout.schulden] in beiden Jahrgangsdateien (Ostbevern: bisheriges Verhalten)"
  - "pruefung.py: lies_vorberichtstabellen, vorbericht_tabellen, weitergabe_posten; Regel 9 prüft die genannten Eckwerte (neu: stellen_beamte_hundertstel); Konzessions- und Kreisumlage-Prüfung nur mit Daten; Fraktionszuwendungen-Summen; privatrechtliche_leistungsentgelte (GEP 05)"
  - "manuell.py: meta.json-Block kreisumlage optional, schuldenstand_euro mit Postenliste"
  - "app_daten.py/quellen.py: gemeinsame Tabellenliste, KL-Posten und Schuldenposten aus der Jahrgangsdatei"
  - "tests/test_hoerstel_manuell.py: 9 Tests"
affects: [11-04, 11-05, 12-app-auf-hoerstel-umstellen]
---

# 11-03: Vorberichtsdaten Hörstel

## Ergebnis

- Alle Vorberichtstabellen, die Hörstel druckt, sind abgeschrieben (Plan-Tabelle in 11-03-PLAN.md). Grafikwerte (Schlüsselzuweisungen S. 22, Kreis- und Jugendamtsumlage S. 35) und berechnete Restposten sind in `anmerkung` gekennzeichnet.
- Regel 5 für Hörstel (gegen die Scratch-Pläne aus den Schritten 01–05): 71 Prüfungen der Vorberichtstabellen mit 3 Abweichungen. Dazu kommen Eigenkapital (6 Summen, 6 Jahresergebnisse gegen GEP Z. 28, Satzung § 4: alle ohne Abweichung), die Fraktionszuwendungen (3 Summen ohne Abweichung) und die Kreditfortschreibung (1 Abweichung). Regel 9: 7 Eckwerte ohne Abweichung.
- Die Weitergabe an Kreis und Land (Kreis-, Jugendamts- und Gewerbesteuerumlage) trifft TP 1661101 Z. 15 in allen sechs Jahren.

## Befunde des PDF (für die Hörsteler `befunde.md`)

| Regel | Plan / Zeile | Jahr | Soll | Ist | Seite |
|---|---|---|---|---|---|
| 5 | vorbericht_leistungsentgelte / summe_posten | 2025 | 10.841.000 | 10.842.000 | 24 |
| 5 | vorbericht_sonstige_aufwendungen / summe_posten | 2026 | 2.368.000 | 2.369.000 | 37 |
| 5 | vorbericht_verbindlichkeiten / summe_posten | 2026 | 56.535.000 | 56.715.000 | 587 |
| 5 | kredite_fortschreibung | 2026 | 43.887.000 | 43.578.158 | 587 |

## Entscheidungen

- **Jahrgangsdatei statt Lockerung:** Tabellenliste, Weitergabe-Posten und Schuldendefinition stehen in `[layout.*]`. Ostbevern listet genau den bisherigen Stand und behält die exakten Mengenprüfungen.
- **Restposten statt erfundener Aufteilung:** `uebrige_*` = gedruckte Summe − einzeln gedruckte Posten, nur wo die Tabelle selbst unvollständig ist. Abweichungen von ±1 T€ bleiben Rundungsbefunde.
- **Schulden Hörstel = Investitionskredite:** Die Verbindlichkeiten aus Transferleistungen sind in Hörstel keine Kreditmittel (anders als die NRW.Bank-Mittel in Ostbevern). Die App-Reihe `nrw_bank` ist für Hörstel 0.
- **Eckwerte aus einer zweiten Fundstelle:** Einwohner aus S. 67 (meta.json: S. 5), Hebesätze aus S. 12 (meta.json: Satzung S. 8).

## Offene Punkte

- `befunde.md`, Regel 4 (§ 3 VE) und die VE-Übersicht gegen die Investitionsübersichten (Hörstel hat keine VE-Fälligkeiten je Produkt und keine VE-Spalte im Gesamtfinanzplan) → 11-05.
- App-Folgen (fehlende Kita-/Einzelzuschusstabellen, HSK-Schwellen, Bilanzierungshilfe, Konzessions-Sparten, Reihe `nrw_bank`) → Phase 12.
