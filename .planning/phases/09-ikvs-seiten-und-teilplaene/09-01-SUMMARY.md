---
phase: 09-ikvs-seiten-und-teilplaene
plan: 01
subsystem: pipeline
tags: [ikvs, hoerstel, seitenklassifikation, hierarchie, teilplaene, pruefregeln]
documented: "nachträglich von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 08-hoerstel-grundlage
    provides: "Jahrgang Hörstel (software = ikvs), ostbevern/ikvs.py für die Gesamtpläne"
provides:
  - "ostbevern/ikvs_seiten.py: klassifiziere_dokument_ikvs (Seitentypen, Kontext fortgeschrieben, Hierarchie PB/PG/P)"
  - "ostbevern/ikvs.py: Tabellenleser für Gesamt- und Teilpläne (ein-, zwei-, dreizeilige Köpfe, Zeilen über Seitengrenzen), Teilplan-Wörterbücher mit gedruckten Varianten, lies_ikvs_teilplaene, teilplan_datensaetze (PG-Summen, abgeleitete PB-Z. 17)"
  - "ostbevern/seiten.py, ostbevern/plaene.py: Schritte 01/02 verzweigen für software = ikvs"
  - "ostbevern/zeilen.py: Teilfinanzplan Z. 32 (Finanzmittelüberschuss) mit Formel 17 + 31"
  - "ostbevern/pruefung.py: Regel 1 mit Schalter nur_mit_gedruckten_komponenten (IKVS)"
  - "jahrgaenge/2026.toml: [kopfzeilen] für IKVS, [layout.ikvs_teilplaene]"
  - "jahrgaenge/2026_sollwerte.toml: [teilergebnisplaene_pb], [teilergebnisplaene_pb_summe], [anhang_a] (16 PB aus dem Inhaltsverzeichnis)"
  - "tests/test_ikvs_teilplaene.py: 10 Tests (Kopfvarianten, Hierarchie, Startseiten, Seiten, Vollständigkeit, Regeln 1-3, B.3, abgeleitete Z. 17)"
affects: [10-ikvs-details, 11-manuelle-daten-und-app-daten-hoerstel]

key-files:
  created:
    - pipeline/ostbevern/ikvs_seiten.py
    - pipeline/tests/test_ikvs_teilplaene.py
  modified:
    - pipeline/ostbevern/ikvs.py
    - pipeline/ostbevern/seiten.py
    - pipeline/ostbevern/plaene.py
    - pipeline/ostbevern/zeilen.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
---

# 09-01: IKVS-Seitenklassifikation, Teilpläne, Regeln 1–3, Sollwerte je PB

## Ergebnis

- **Schritt 01:** alle 592 Seiten klassifiziert, keine unbekannte Seite. Hierarchie: 16 PB, 50 PG (5-stellig), 69 Produkte (7-stellig). Die PB-Startseiten stimmen mit dem Inhaltsverzeichnis (S. 3) überein.
- **Schritt 02:** 85 Teilergebnis- und 85 Teilfinanzpläne (16 PB, 69 Produkte) gelesen, dazu die PG-Summen. `ergebnisplan.csv`: 11.874 Zeilen, `finanzplan.csv`: 4.494 Zeilen.
- **Prüfregeln:** Regel 1 (7.332 Prüfungen), Regel 2 (8.166) und Regel 3 (114) ergeben zusammen 11 Abweichungen über 1 €. Alle sind im PDF so gedruckt (siehe Befunde). Anhang B.3 (16 PB × 3 Werte + 2 Summen) ohne Abweichung.
- Die 50 PG-Summen für ordentliche Erträge und Aufwendungen 2026 treffen die unabhängig gedruckten Haushaltsquerschnitte (S. 85–109) exakt.

## Befunde des PDF (für die Hörsteler `befunde.md` in Phase 11)

| Regel | Knoten | Zeile | Jahr | Soll | Ist | Seite | Ursache |
|---|---|---|---|---|---|---|---|
| 1 | P 0212601 (und PG 02126) | 10 | 2024 | 287.143 | 287.141 | 206 | Rundung der Ist-Werte |
| 2 | PB 05 | 29, 31 | 2024 | −1.389.035 | −1.389.037 | 274 | Rundung der Ist-Werte |
| 2 | PB 12 | 29, 31 | 2024 | −3.365.180 | −3.365.182 | 442 | Rundung der Ist-Werte |
| 3 | GESAMT | 10 | 2024 | 55.423.003 | 55.423.001 | 79 | Rundung (Gesamtplan mit Cent) |
| 3 | GESAMT | 15, 17 | 2026 | 28.772.760 / 61.336.557 | 28.766.960 / 61.330.757 | 79 | Teilpläne enthalten 5.800 € weniger Transferaufwendungen als der Gesamtplan; auch Σ Querschnitte S. 85–109 ≠ Querschnitt S. 110 |
| 3 | GESAMT | 15, 17 | 2027 | 28.800.660 / 61.830.585 | 28.796.260 / 61.826.185 | 79 | wie oben, 4.400 € |

## Entscheidungen

- **Kontext statt Kopfzeile:** Trennseiten („Produktbereich“/„Produkt“) setzen den Kontext; jeder Titel (Teilergebnisplan, Teilfinanzplan, Investitionsübersicht) wird gegen ihn geprüft. Seiten ohne Titel in der ersten Zeile setzen den letzten Abschnitt der Vorseite fort.
- **Namen:** Maßgeblich ist der Produktname der Produktinformationen (wie in den Teilplantiteln); die Trennseite kürzt teils anders (S. 555 „und“ statt „u.“).
- **Startseiten:** PB = Planseite mit Kopf „Produktbereich NN Name“ (wie Inhaltsverzeichnis), Produkt = Produktinformationen, PG = erstes Produkt.
- **Produktgruppen:** keine eigenen Teilpläne; PG-Werte = Summe der Produkte, Zeilen und Hierarchie `synthetisch`.
- **PB-Teilfinanzplan Z. 17:** nicht gedruckt, aber Z. 32; abgeleitet als Z. 32 − Z. 31 (`synthetisch`), damit Regel 2 den Saldo der laufenden Verwaltung prüft.
- **Regel 1 im IKVS-Layout:** nur Formeln mit mindestens einer gedruckten Komponente (Teilfinanzpläne drucken Z. 17 ohne Z. 09/16). Ostbevern unverändert.
- **Tabellenleser:** Spaltenköpfe ein-, zwei- oder dreizeilig (S. 511); Planzeilen dürfen über eine Seitengrenze laufen (S. 169/170); Teilplan-Bezeichnungen mit gedruckten Varianten (z. B. Z. 17 „Saldo aus laufender Verwaltungstätigkeit“ / „… aus der Verwaltungstätigkeit“).

## Offene Punkte

- Die 11 Befunde stehen bisher nur im Test und hier; `pruefe_alles` und `befunde.md` für Hörstel folgen in Phase 11.
- `alle.py` bricht für Hörstel ab Schritt 03 ab (Phase 10).
