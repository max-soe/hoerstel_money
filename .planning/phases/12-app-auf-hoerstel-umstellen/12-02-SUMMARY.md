---
phase: 12-app-auf-hoerstel-umstellen
plan: 02
subsystem: app, pipeline
tags: [hoerstel, vitest, quellenbelege, geldfluss, investitionen, bezugsgroessen]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md); Testdateien parallel von vier Agenten umgestellt, App- und Pipeline-Fehler zentral behoben"

requires:
  - phase: 12-app-auf-hoerstel-umstellen
    provides: "12-01"
provides:
  - "App-Tests auf Hörstel: 45 Dateien, 2.067 Tests grün; Ostbevern-Strukturen über synthetische Daten (vi.doMock) weiter abgedeckt"
  - "app_daten.py: Maßnahmen getrennt nach Richtung (IKVS ohne Sachkonto), Abbruch bei doppeltem Jahr"
  - "app_daten.py: Vorberichtsposten berechnet bei Anmerkung „berechnet: …“; Seite und Anmerkung aus der Zeile des Haushaltsjahrs"
  - "app_daten.py + [layout.bezugsgroessen]: Bezugsgrößen „Zuschussbedarf je Einheit“ aus dem Jahrgang statt BEZUGSGROESSEN im Code (Hörstel leer)"
  - "geldfluss.ts: Differenz Gesamtplan/Teilpläne als eigener berechneter Knoten"
  - "einnahmen.ts, ebenenBeleg.ts, InvestitionenPage.vue: Belege je Finanzplanseite, ordentliches Ergebnis ohne gedruckte Z. 17, VE-Übersicht ohne VE-Spalte"
  - "erklaerungen.md: ueberschuss_ruecklage ohne Jahresbindung"
affects: [12-03, 12-04]
---

# 12-02: App-Tests auf die Hörsteler Daten

## Ergebnis

- `npm run type-check`, `lint`, `format:check`, `test` (2.067/2.067) und `build` grün.
- Die Umstellung der Tests hat sieben echte Fehler aufgedeckt, alle behoben:
  1. Maßnahmen ohne Sachkonto: Ein- und Auszahlung derselben Maßnahme überschrieben sich (31 von 219 Einträgen fehlten, Auszahlungen 2026–2029 71,7 statt 77,0 Mio. €, PB 13 fehlte). Jetzt 219 Einträge, Summe 76.972.571 € (= GFP Z. 30 abzüglich Befund 0212201).
  2. Finanzplan-Zeilen nannten S. 80, auch wenn sie auf S. 81 stehen.
  3. VE-Kachel belegte mit der Summenzeile des Finanzplans, die bei IKVS keine VE-Spalte hat (jetzt S. 586).
  4. Drilldown-Beleg im Modus Zuschussbedarf für reine Ertragsprodukte (1153101, 1153201) nicht auflösbar.
  5. Geldfluss 2026/2027 um 5.800 €/4.400 € unausgeglichen (Befund Regel 3); die Differenz steht jetzt als berechneter Knoten rechts.
  6. Abgeschriebene Reste `uebrige_*` erschienen als gedruckte Werte; Seiten der Vorberichtsposten kamen aus dem letzten Planjahr (Grafikseite) statt aus dem Haushaltsjahr.
  7. Erklärtext zum Überschuss erschien nie (an 2024 gebunden, aber nur im Haushaltsjahr gültig).
- `BEZUGSGROESSEN` (Ostbevern-Produktcodes im Code) liegt jetzt im Jahrgang.

## Offen

- Ein Vorberichtsposten trägt `berechnet` für alle Jahre, wenn er in einem Jahr berechnet ist (Gewerbesteuerumlage: 2025/2026 gedruckt, übrige Jahre berechnet). Vorsichtig, aber gröber als nötig; ein Flag je Jahr wäre genauer.
- Allgemeine Rücklage sinkt 2025→2026 um 1.612.802 € ohne Fehlbetrag (direkte Buchung, S. 588); `abbau()` bildet das nicht ab, die Rückgangsgrafik zeigt nur Planjahre ab 2026.
