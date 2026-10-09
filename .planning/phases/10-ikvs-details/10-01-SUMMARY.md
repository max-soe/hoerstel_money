---
phase: 10-ikvs-details
plan: 01
subsystem: pipeline
tags: [ikvs, hoerstel, produktinformationen, erlaeuterungen, investitionen, querschnitte, datenschutz]
documented: "nachträglich von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 09-ikvs-seiten-und-teilplaene
    provides: "seiten.csv, hierarchie.csv, Plan-CSVs für Hörstel; ostbevern/ikvs.py-Tabellenleser"
provides:
  - "ostbevern/ikvs_produkte.py: Produktinformationen (ohne Personennamen), Stellen-/Kennzahlentabellen als Grundzahlen, Erläuterungen je Teilergebnisplan-Zeile"
  - "ostbevern/ikvs_investitionen.py: Investitionsübersichten B mit Saldo-Gegenproben"
  - "ostbevern/ikvs_querschnitte.py: Haushaltsquerschnitte je PG und Gesamthaushalt (geometrische Spaltenerkennung)"
  - "ostbevern/ikvs.py: Spaltenkopf ohne Jahr (VE), verbinde_teile (Silbentrennung vs. Bindestrich-Kompositum), öffentliche Hilfsfunktionen"
  - "ostbevern/produkte.py, investitionen.py, querschnitte.py: Verzweigung für software = ikvs"
  - "ostbevern/pruefung.py: Regel 6 (VE-Spalte, PB-Listen, VE-Fälligkeiten), Regel 7 (Gesamthaushalt, nur gedruckte Komponenten) und Regel 8 (IKVS-Pflichtfelder) layoutabhängig; Planwerte.ist_gedruckt"
  - "jahrgaenge/2026.toml: [layout.ikvs_querschnitte], [layout.ikvs_investitionen], [layout.ikvs_produktinformationen], [layout.ikvs_erlaeuterungen]"
  - "tests/test_ikvs_details.py: 16 Tests"
affects: [11-manuelle-daten-und-app-daten-hoerstel, 12-app-auf-hoerstel-umstellen]

key-files:
  created:
    - pipeline/ostbevern/ikvs_produkte.py
    - pipeline/ostbevern/ikvs_investitionen.py
    - pipeline/ostbevern/ikvs_querschnitte.py
    - pipeline/tests/test_ikvs_details.py
  modified:
    - pipeline/ostbevern/ikvs.py
    - pipeline/ostbevern/produkte.py
    - pipeline/ostbevern/investitionen.py
    - pipeline/ostbevern/querschnitte.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/jahrgaenge/2026.toml
---

# 10-01: Produktinformationen, Erläuterungen, Investitionen, Querschnitte, Regeln 6–8

## Ergebnis

- **Schritt 03:** `produkte.json` mit 69 Produkten, `grundzahlen.csv` mit 1.321 Werten (383 Stellen, 938 Kennzahlen), `erlaeuterungen.csv` mit 1.239 Positionen. Jedes Produkt hat Beschreibung oder Leistungsliste, Auftragsgrundlage und Erläuterungen; die Zielgruppe fehlt nur bei 0111106 (im PDF nicht gedruckt). Kein Name eines Produktverantwortlichen steht in einer erzeugten Datei (Test).
- **Schritt 04:** `investitionen.csv` mit 566 Werten aus 188 Maßnahmen in 29 Produkten. Je Maßnahme Saldo = Einzahlung − Auszahlung, je Produkt Summenzeile = Σ Maßnahmen. `ve_faelligkeiten.csv` und `investitionen_pb.csv` sind leer (im IKVS-Layout nicht gedruckt).
- **Querschnitte:** 593 Werte für 50 Produktgruppen und den Gesamthaushalt.
- **Prüfregeln:** Regel 7: 409 Prüfungen, 0 Abweichungen. Regel 6: 840 Prüfungen, 11 belegte Abweichungen, 0 Lücken. Regel 8: 346 Prüfungen, 0 Lücken.

## Befunde des PDF (für die Hörsteler `befunde.md` in Phase 11)

| Regel | Knoten | Zeile | Jahr | Soll (Plan) | Ist (Übersicht) | Seite |
|---|---|---|---|---|---|---|
| 6 | P 0212201 | 30 | 2026 | 108.125 | 105.000 | 196 |
| 6 | P 0212201 | 30 | 2027–2029 | je 3.125 | 0 | 196 |
| 6 | P 1557302 | 23 | 2025 | 62.333 | 0 | 542/543 |
| 6 | GESAMT | 23/30 | 2024–2029 | Folgen der obigen, 2024 zusätzlich 2 € Rundung | | 80 |
| 4 (§ 3) | GESAMT | VE | 2026 | 18.331.000 | 13.231.000 | 7, 124, 586 |

Die VE „Neubau eines Verwaltungsgebäudes Hörstel“ (5.100 T€) steht in der VE-Übersicht (S. 586) und in der Satzung, die Investitionsübersicht der Maßnahme 111.02-004 (S. 124) druckt nur 250.000 €.

Erläuterungen mit abweichendem Ansatz 2026 (Erläuterung / Teilergebnisplan): 0111107 Z. 06 26.660/26.600 (S. 151), 0111110 Z. 02 69.630/106.130 (S. 172), 0111112 Z. 16 16.000/36.000 (S. 182), 0842403 Z. 27 189.000/189.500 (S. 379), 1254501 Z. 04 48.826/46.826 (S. 476), 1254701 Z. 05 1.000/0 (S. 486), 1557101 Z. 15 145.500/151.300 (S. 531).

## Entscheidungen

- **Schema unverändert:** Felder, die das IKVS-Layout nicht kennt (Fachbereich, Gremium, Bindungsgrad, Klassifizierung, Ziele, Sachkonto, Investitionsart), bleiben null. Listenpunkte der Beschreibung werden `leistungen`, Fließtext `beschreibung`.
- **Kennzahlen als Grundzahlen:** Gruppen „Stellenplan“ (Vollzeitstellen, Auszubildende) und „Kennzahlen“; `hinweis = "Planwert"` kennzeichnet Planjahre. Die Produktnummer vor der Bezeichnung („01.111.07 “) wird entfernt. „Ergänzende Erläuterungen“ werden nicht übernommen.
- **Erläuterungen:** Eine Überschrift mit Ansatzzeile, die eine Teilergebnisplan-Zeile benennt, eröffnet einen Block (`zu_zeilen`), Sachkonto-Überschriften bleiben im Block. Ansatzzeilen mit Tippfehler (doppeltes Vorjahr, „20245“) gelten positionsweise als Haushaltsjahr; Texte ausgelaufener Produkte (Ansatz 2024/2025) erhalten keinen Betrag.
- **Investitionen:** Maßnahmennummern auch mit Druckfehler („424.02.-006“, S. 372); nur gedruckte Werte, „--“ entfällt.
- **Querschnitte:** Spalten geometrisch (Phrasen je Zeile, Überlappung über Zeilen), alphabetisch gedruckte Spaltennamen über `[layout.ikvs_querschnitte]` den Kennzahlen zugeordnet; leere Blöcke (S. 91) erlaubt.
- **Prüfregeln layoutabhängig über `jahrgang.software`:** Regel 6 ohne VE-Spalte gegen die Finanzpläne, ohne PB-Gegenprobe und VE-Fälligkeiten; Regel 7 Gesamthaushalt gegen die Gesamtpläne und nur Kennzahlen mit gedruckten Komponenten; Regel 8 mit Pflichtfeld Auftragsgrundlage und Beschreibung oder Leistungen. Ostbevern unverändert (volle Suite und Reproduzierbarkeitslauf).

## Offene Punkte

- Stellenplan (Schritt 05) ist im Hörsteler PDF nur als Bild gedruckt → Phase 11 (manuell).
- `befunde.md`, `pruefe_alles` (Regel 4 § 3 VE, Regel 5/9/10) und `alle.py` für Hörstel → Phase 11.
- Quellenbelege (Schritt 08): Die Seiten der Produktinformationen enthalten Personennamen; die Schwärzliste (`[layout.quellenbelege]`) muss für Hörstel neu erstellt werden → Phase 11.
