---
phase: 12-app-auf-hoerstel-umstellen
plan: 01
subsystem: app, pipeline
tags: [hoerstel, app, typen, bindungsgrad, zuschuesse, ruecklagen, eigenkapital]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 11-manuelle-daten-und-app-daten-hoerstel
    provides: "app/src/data aus Hörstel"
provides:
  - "haushalt.json: eigenkapital_stand, finanzierungsprodukt (aus [layout.eigenkapital] und [layout.weitergabe_kreis_land]); neue Felder hängen hinten an"
  - "investitionen.json: VE-Fälligkeiten mit name (VE-Übersicht, wenn keine Maßnahme passt)"
  - "typen.ts: nullbare Produkt-, Grundzahl-, Maßnahmen- und VE-Felder; Meta.kreisumlage optional"
  - "bindungsgrad.ts: Segment „Ohne Angabe im Plan“ (ohneAngabe); RatEntscheidetPage zeigt ohne Bindungsgrade die Produktliste statt des Balkens"
  - "zuschuesse.ts, aufwandsarten.ts, einnahmen.ts: Kita-Tabelle, Einzelzuschüsse, Konzessions-Sparten optional; Sozialleistungen = sozialleistungen oder sozialtransferaufwendungen"
  - "ruecklagen.ts: bestandText(), Stand vor Ergebnisverrechnung, Verrechnung der Bilanzierungshilfe optional, hskSchwellen() null ohne Schwellen im Vorbericht"
affects: [12-02]
---

# 12-01: App-Module laden die Hörsteler Daten

## Ergebnis

- Alle Bibliotheksmodule laden mit den Hörsteler Daten ohne Fehler; Typprüfung des App-Codes grün.
- Keine Jahrgangswerte im Code: Finanzierungsprodukt und Eigenkapitalstand kommen aus dem Jahrgang über `haushalt.json`.
- Hörstel druckt keine HSK-Schwellen (S. 78 nennt nur § 76 GO NRW): Schwellenlinie und Schwellensatz entfallen, statt Zahlen von Hand einzusetzen.
- Ostbevern-Referenz neu erzeugt (nur die beiden neuen Felder).

Commit: 545c1ed
