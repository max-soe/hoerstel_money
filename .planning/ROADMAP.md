# Roadmap: Hörstel Money

## Milestones

- ✅ **v1.0 MVP** — Phases 1-7 (shipped 2026-10-07, Gemeinde Ostbevern) — [Archiv](milestones/v1.0-ROADMAP.md)
- 🚧 **v2.0 Hörstel** — Phases 8-12 (in progress, von Hand gepflegt)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-7) — SHIPPED 2026-10-07</summary>

- [x] Phase 1: Setup (5/5 plans) — completed 2026-10-01
- [x] Phase 2: Kernzahlen (5/5 plans) — completed 2026-10-01
- [x] Phase 3: Details (5/5 plans) — completed 2026-10-02
- [x] Phase 4: Manuelle Daten und App-Daten (6/6 plans) — completed 2026-10-04
- [x] Phase 5: Leitfragen-Seiten (16/16 plans) — completed 2026-10-05
- [x] Phase 6: Kontext-Seiten (17/17 plans) — completed 2026-10-06
- [x] Phase 7: Feinschliff und Veröffentlichung (14/14 plans) — completed 2026-10-07

</details>

### 🚧 v2.0 Hörstel (Phases 8-12)

Ziel: Die App erklärt den Haushalt 2026 der Stadt Hörstel. Das Hörsteler PDF ist ein Word-Export von Axians IKVS und kein ProFIS+-Export. Die PDF-lesenden Pipeline-Schritte bekommen deshalb eine zweite Leselogik (`software = "ikvs"`). Prüfregeln, App-Daten und App bleiben, Ostbevern bleibt als ProFIS+-Referenz testbar. Grundlage: `discussion/HOERSTEL_MACHBARKEIT.md`.

Die Phasen werden ohne GSD-Befehle bearbeitet und hier von Hand nachgeführt.

- [x] **Phase 8: Hörstel-Grundlage** — Jahrgang Hörstel, IKVS-Leser für die Gesamtpläne, Ostbevern als Testreferenz (HOE-01, HOE-02, HOE-03) (completed 2026-10-08)
- [x] **Phase 9: IKVS-Seiten und Teilpläne** — Seitenklassifikation ohne Kopfzeile, Hierarchie 2/5/7-stellig, Teilergebnis- und Teilfinanzpläne, Regeln 1–3, Sollwerte je PB (HOE-04, HOE-05, HOE-14) (completed 2026-10-08)
- [x] **Phase 10: IKVS-Details** — Produktinformationen ohne Personennamen, Erläuterungen, Investitionsübersichten mit VE, Haushaltsquerschnitte (HOE-06 bis HOE-09) (completed 2026-10-08)
- [x] **Phase 11: Manuelle Daten und App-Daten Hörstel** — Bildseiten (Stellenplan, Fraktionen, Eigenkapital) manuell, Vorberichtsdaten, `meta.json`, Texte; `alle.py` und CI auf Hörstel (HOE-10 bis HOE-12) (completed 2026-10-09)
- [ ] **Phase 12: App auf Hörstel umstellen** — Texte, Namen, Links, Deployment (HOE-13)

## Phase Details

### Phase 8: Hörstel-Grundlage
**Goal**: Der Hörsteler Haushalt ist als Jahrgang 2026 eingebunden, die Gesamtpläne werden geprüft gelesen, und die bestehenden Ostbevern-Tests laufen weiter als Regressionstests.
**Requirements**: HOE-01, HOE-02, HOE-03
**Plans**: 2 plans (nachträglich dokumentiert)
- [x] 08-01: IKVS-Leser für die Gesamtpläne und Jahrgang Hörstel
- [x] 08-02: Ostbevern als ProFIS+-Referenz für Tests und CI

### Phase 9: IKVS-Seiten und Teilpläne
**Goal**: `seiten.csv`, `hierarchie.csv`, `ergebnisplan.csv` und `finanzplan.csv` enthalten den vollständigen Hörsteler Haushalt; Regeln 1–3 sind grün.
**Requirements**: HOE-04, HOE-05, HOE-14
**Plans**: 1 plan (nachträglich dokumentiert)
- [x] 09-01: IKVS-Seitenklassifikation, Teilpläne, Regeln 1–3, Sollwerte je PB
**Success Criteria**:
1. 69 Produkte, 16 PB und alle gedruckten PG werden mit Startseite erkannt
2. Jeder Teilergebnis- und Teilfinanzplan ist gelesen; Regel 1 (Formeln), Regel 2 (Produkte → PG → PB) und Regel 3 (PB → Gesamt) ohne unbelegte Abweichung
3. Sollwerte je PB in `2026_sollwerte.toml`

### Phase 10: IKVS-Details
**Goal**: Produktinformationen, Erläuterungen, Investitionen und Querschnitte im Hörsteler Layout, Regeln 6–8 grün.
**Requirements**: HOE-06, HOE-07, HOE-08, HOE-09
**Plans**: 1 plan (nachträglich dokumentiert)
- [x] 10-01: Produktinformationen, Kennzahlen, Erläuterungen, Investitionsübersichten, Querschnitte, Regeln 6–8

### Phase 11: Manuelle Daten und App-Daten Hörstel
**Goal**: `alle.py` erzeugt `daten/` und `app/src/data/` aus dem Hörsteler Haushalt, die CI prüft die Reproduzierbarkeit für Hörstel.
**Requirements**: HOE-10, HOE-11, HOE-12
**Plans**: 5 plans (von Hand geführt)
- [x] 11-01: Ostbevern-Referenzstand nach `pipeline/referenz/ostbevern/` auslagern (`PIPELINE_REFERENZ`)
- [x] 11-02: Stellenplan (Bildseiten S. 568–574) abschreiben, Schritt 05 und Regel 10 im IKVS-Layout
- [x] 11-03: Vorberichtstabellen, Fraktionszuwendungen, Eigenkapital (Bild S. 588), Verbindlichkeiten, VE-Übersicht, `meta.json`, Eckwerte; Regel 5/9
- [x] 11-04: Erklärtexte und Glossar für Hörstel
- [x] 11-05: `befunde.md`, Prüfbericht, App-Daten, Quellenbelege mit Schwärzliste, `alle.py` durchgehend, CI-Reproduzierbarkeit auf Hörstel

### Phase 12: App auf Hörstel umstellen
**Goal**: Die öffentliche App erklärt den Hörsteler Haushalt.
**Requirements**: HOE-13
**Plans**: 4 plans (von Hand geführt)
- [ ] 12-01: App lädt die Hörsteler Daten: Typen, optionale Ostbevern-Strukturen (Kita, Einzelzuschüsse, Konzessions-Sparten, HSK-Schwellen, Bindungsgrad, Steuer-Zeitreihen), Eigenkapitalstände zum Jahresende, Maßnahmen ohne Sachkonto
- [ ] 12-02: App-Tests auf die Hörsteler Daten
- [ ] 12-03: Texte, Namen und Links (Stadt Hörstel, PDF, Repository, Impressum), README, Deployment
- [ ] 12-04: Browser-Tests (Playwright, axe, Kachelbreiten) und Sichtprüfung
