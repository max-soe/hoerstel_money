---
phase: 08-hoerstel-grundlage
plan: 01
subsystem: pipeline
tags: [ikvs, hoerstel, pdfplumber, gesamtplaene, konfiguration]
documented: "nachträglich von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 02-kernzahlen
    provides: "ostbevern/zeilen.py (kanonische Zeilen und Formeln), pruefung.Planwerte, Regel 1 und Satzungsprüfung"
provides:
  - "pipeline/jahrgaenge/2026.toml: Jahrgang Hörstel mit software = \"ikvs\", Seitenbereichen und [layout.ikvs_gesamtplaene]"
  - "pipeline/jahrgaenge/2026_sollwerte.toml: Satzung § 1-3 (S. 7), Gesamtergebnisplan (S. 79), Gesamtfinanzplan Ansatz 2026 (S. 80/81)"
  - "ostbevern/konfiguration.py: Jahrgang.software, SOFTWARE_LAYOUTS; leere teilergebnisplaene_pb_summe erlaubt"
  - "ostbevern/ikvs.py: IKVS-Zeilen-Wörterbuch, lies_ikvs_betrag, lies_ikvs_plantabelle, gesamtplan_datensaetze"
  - "ostbevern/plaene.py: extrahiere_plaene schreibt für IKVS die GESAMT-Zeilen"
  - "ostbevern/seiten.py: klassifiziere_seiten bricht für IKVS mit Hinweis ab"
  - "tests/test_ikvs.py: 28 Tests (Einheiten + echtes PDF)"
affects: [09-ikvs-seiten-und-teilplaene]

commits:
  - 201ae8a  # PDF umbenannt, Machbarkeitsbericht
  - 442b9bc  # IKVS-Leser für die Gesamtpläne

key-files:
  created:
    - pipeline/ostbevern/ikvs.py
    - pipeline/tests/test_ikvs.py
    - discussion/HOERSTEL_MACHBARKEIT.md
  modified:
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/ostbevern/konfiguration.py
    - pipeline/ostbevern/plaene.py
    - pipeline/ostbevern/seiten.py
---

# 08-01: IKVS-Leser für die Gesamtpläne und Jahrgang Hörstel

## Ergebnis

- Gesamtergebnisplan (S. 79, 33 Zeilen) und Gesamtfinanzplan (S. 80–81, 38 Zeilen) werden vollständig gelesen: 198 bzw. 228 Datensätze im Plan-Langformat.
- Regel 1 (Zeilenformeln) über beide Gesamtpläne: 108 Prüfungen, 0 Abweichungen, auch nach kaufmännischer Rundung der Ist-Ergebnisse 2024 (Cent).
- Satzung § 1–2 (S. 7) gegen die Gesamtpläne: 0 Abweichungen. § 3 (VE 18.331.000 €) folgt mit den Investitionsübersichten, weil der Gesamtfinanzplan keine VE-Spalte druckt.

## Entscheidungen

- **Eigene Leselogik statt Umbau:** `software = "ikvs"` in der Jahrgangsdatei wählt die Leselogik; die ProFIS+-Leser bleiben unverändert.
- **Spaltenzuordnung:** Beträge stehen rechtsbündig, Jahreszahlen zentriert. Jedes Betragswort wird über seine Mitte der Spalte zwischen den Mitten benachbarter Jahreszahlen zugeordnet.
- **Zeilenaufbau:** Eine Zeile beginnt mit „NN -“. Folgezeilen gehören zur offenen Zeile, solange die zusammengesetzte Bezeichnung ein Präfix der Wörterbuchbezeichnung bleibt; sonst wird eine ungedruckte Zeile (fremde Finanzmittel) über die Bezeichnung erkannt. Ein einzelnes „-“ in der Betragszone gilt als Vorzeichen des Betrags derselben Spalte.
- **Kanonische Nummern:** Gedruckte Nummern werden auf `ostbevern/zeilen.py` abgebildet (Finanzplan einstellig → zweistellig, „40 Liquide Mittel“ → 41, ungedruckte fremde Finanzmittel → 40).
- **Spalten:** Gedruckte Köpfe („Ansatz 2027“) stehen in `[layout.ikvs_gesamtplaene]`, kanonische („Planung 2027“) in `[spalten]`; die Abbildung ist positionsweise und prüft das Jahr.
- **Rundung:** Ist-Ergebnisse mit Cent werden kaufmännisch (ROUND_HALF_UP) auf Euro gerundet.

## Offene Punkte

- Schritt 01 (Seitenklassifikation) und die Teilpläne im IKVS-Layout fehlen; `alle.py` läuft für Hörstel noch nicht durch (Phase 9).
- Die Sollwerte sind aus dem PDF-Text übertragen, nicht aus einer unabhängigen Spezifikation.
