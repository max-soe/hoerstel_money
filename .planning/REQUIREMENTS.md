# Requirements: Hörstel Money (v2.0)

**Defined:** 2026-10-08 (von Hand gepflegt, ohne `/gsd-new-milestone`)
**Core Value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt; die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.

Grundlage: `discussion/HOERSTEL_MACHBARKEIT.md` (Strukturvergleich ProFIS+/IKVS, Einschätzung je Pipeline-Schritt). Fachliche Detailquelle bleibt `discussion/SPEZIFIKATION.md`, soweit sie nicht Ostbevern-spezifisch ist. Die v1-Anforderungen (Ostbevern) sind in `milestones/v1.0-REQUIREMENTS.md` archiviert.

## v2.0 Requirements

### Grundlage

- [x] **HOE-01**: Der Jahrgang 2026 beschreibt den Haushalt der Stadt Hörstel (592 Seiten, Word-Export von Axians IKVS): `software = "ikvs"`, Seitenbereiche, kanonische und gedruckte Spaltenköpfe in `pipeline/jahrgaenge/2026.toml`
- [x] **HOE-02**: Gesamtergebnisplan (S. 79) und Gesamtfinanzplan (S. 80–81) werden im IKVS-Layout gelesen und auf die kanonischen Zeilennummern abgebildet; Regel 1 (Zeilenformeln) und Satzung § 1–2 (S. 7) ohne Abweichung
- [x] **HOE-03**: Ostbevern bleibt als Referenz für das ProFIS+-Layout testbar: archivierter Jahrgang unter `jahrgaenge/archiv/ostbevern/`, PDF unter `raw_data/ostbevern/`, Tests und CI-Reproduzierbarkeit über `PIPELINE_JAHRGAENGE`

### Extraktion IKVS

- [x] **HOE-04**: Seitenklassifikation im IKVS-Layout ohne laufende Kopfzeile (Kontext wird von Seite zu Seite fortgeschrieben): 16 Produktbereiche, 5-stellige Produktgruppen, 69 Produkte mit 7-stelligem Code; `seiten.csv` und `hierarchie.csv`
- [x] **HOE-05**: Teilergebnis- und Teilfinanzpläne (PB und Produkt) im IKVS-Layout (nur belegte Zeilen gedruckt, umbrochene Bezeichnungen); Regeln 1–3 grün
- [ ] **HOE-06**: Produktinformationen (Beschreibung, Auftragsgrundlage, Zielgruppe, Vollzeitstellen, Kennzahlen); der Produktverantwortliche (Personenname) wird beim Parsen verworfen
- [ ] **HOE-07**: Erläuterungen im Format „Bezeichnung / Ansatz 2025 = X €, Ansatz 2026 = Y € / Text“
- [ ] **HOE-08**: Investitionsübersichten B mit Maßnahmen (`111.02-004`), Ein-/Auszahlungen und VE; Satzung § 3 (VE) grün
- [ ] **HOE-09**: Haushaltsquerschnitte je Produktgruppe (S. 85–110) als Kontrollquelle (Regel 7)

### Daten und App

- [ ] **HOE-10**: Stellenplan, Fraktionszuwendungen und Eigenkapitalentwicklung (Bildseiten ohne Textebene) manuell mit Seitenbeleg erfasst
- [ ] **HOE-11**: Manuelle Vorberichtsdaten, `meta.json` (Einwohnerzahl Hörstel), Eckwerte in der Sollwertdatei und Erklärtexte für Hörstel
- [ ] **HOE-12**: `alle.py` läuft für Hörstel durch; `daten/` und `app/src/data/` stammen aus Hörstel; die CI-Reproduzierbarkeit prüft den Hörsteler Jahrgang
- [ ] **HOE-13**: App-Texte, Namen und Links auf Hörstel umgestellt (Stadt statt Gemeinde, PDF-Link, Repository, Deployment)
- [x] **HOE-14**: Hörsteler Sollwertdatei mit PB-Teilergebnisplänen und Produktverzeichnis (die Eckwerte folgen mit HOE-11)

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| HOE-01 | Phase 8 | Complete |
| HOE-02 | Phase 8 | Complete |
| HOE-03 | Phase 8 | Complete |
| HOE-04 | Phase 9 | Complete |
| HOE-05 | Phase 9 | Complete |
| HOE-14 | Phase 9 | Complete |
| HOE-06 | Phase 10 | Pending |
| HOE-07 | Phase 10 | Pending |
| HOE-08 | Phase 10 | Pending |
| HOE-09 | Phase 10 | Pending |
| HOE-10 | Phase 11 | Pending |
| HOE-11 | Phase 11 | Pending |
| HOE-12 | Phase 11 | Pending |
| HOE-13 | Phase 12 | Pending |

---
*Last updated: 2026-10-08*
