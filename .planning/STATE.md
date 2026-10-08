---
gsd_state_version: "1.0"
milestone: v2.0
milestone_name: Hörstel
status: In progress
stopped_at: Phase 9 complete (von Hand gepflegt, ohne GSD-Befehle)
last_updated: "2026-10-08T00:00:00.000Z"
last_activity: 2026-10-08
last_activity_desc: Phase 9 abgeschlossen (IKVS-Seitenklassifikation, Teilpläne, Regeln 1-3, Sollwerte je PB)
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 3
  completed_plans: 3
  percent: 40
current_phase: 09
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-08)

**Core value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt. Die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.
**Current focus:** Meilenstein v2.0 Hörstel: den Haushalt 2026 der Stadt Hörstel (IKVS-Layout) lesen und die App darauf umstellen.

## Current Position

Milestone: v2.0 Hörstel (Phases 8-12)
Phase: 9 of 8-12 (IKVS-Seiten und Teilpläne) — complete
Plan: 09-01 complete
Status: Ready for Phase 10 (IKVS-Details)
Last activity: 2026-10-08 — Phase 9 abgeschlossen

Hinweis: Dieser Meilenstein wird in einer Cloud-Session ohne GSD-Befehle bearbeitet. ROADMAP, REQUIREMENTS, STATE und die Phasen-Summaries unter `.planning/phases/` werden von Hand nachgeführt; PLAN-, VERIFICATION- und UAT-Dateien gibt es für diese Phasen nicht.

## Performance Metrics

**Velocity:**
- Total plans completed: 68
- Average duration: -
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | - | - |
| 2 | 5 | - | - |
| 03 | 5 | - | - |
| 04 | 6 | - | - |
| 05 | 16 | - | - |
| 06 | 17 | - | - |
| 07 | 14 | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 07 P10 | mehrere Sitzungen | 3 tasks | 5 files |
| Phase 07 P12 | n/a | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table (Stand v2.0, Phase 8). Die Phasen-Entscheidungen von v1.0 sind in `.planning/milestones/v1.0-phases/` archiviert.

### Pending Todos

None.

### Blockers/Concerns

Aus v2.0 (Phase 8):
- `alle.py` läuft für Hörstel bis Schritt 02 (Seiten, Hierarchie, alle Pläne); ab Schritt 03 (Produktinformationen) fehlt die IKVS-Leselogik (Phase 10). `daten/` und `app/src/data/` stammen weiter aus Ostbevern; die CI-Reproduzierbarkeit prüft bis Phase 11 den Ostbevern-Referenzjahrgang.
- Stellenplan (S. 568–574), Fraktionszuwendungen (S. 576/577) und Eigenkapitalentwicklung (S. 588) sind Bilder ohne Textebene: nur manuelle Erfassung oder OCR.
- Hörstel druckt Ist-Ergebnisse 2024 in den Gesamtplänen mit Cent; gerundet wird kaufmännisch auf Euro (bisher ohne Formelabweichung).
- 11 gedruckte Abweichungen aus Phase 9 (Regeln 1–3) sind bisher nur im Test `tests/test_ikvs_teilplaene.py` und in 09-01-SUMMARY belegt; sie müssen in Phase 11 in die Hörsteler `befunde.md`. Darunter die 5.800 € (2026) bzw. 4.400 € (2027) Transferaufwendungen, die den Teilplänen gegenüber dem Gesamtergebnisplan fehlen.

Aus v1.0 übernommen (offen):
- `app/node_modules` im gemounteten Repo enthält macOS-Binaries; im Linux-Sandbox App-Checks in einer Scratch-Kopie ausführen.
- Code-Review-Restbefunde: 02-REVIEW.md (3 Warnungen), 04-REVIEW-DISPOSITION.md (WR-01…WR-05, IN-02), alle ohne Auswirkung auf die Daten.
- `/gsd-secure-phase 04` steht aus.
- Kein Milestone-Audit für v1.0; Phasen-Verifikationen „stale“ (vom Nutzer akzeptiert).

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-08
Stopped at: Phase 9 complete
Resume file: .planning/phases/09-ikvs-seiten-und-teilplaene/09-01-SUMMARY.md

## Operator Next Steps

- Phase 10 (IKVS-Details: Produktinformationen, Erläuterungen, Investitionsübersichten, Querschnitte) beginnen; Details in ROADMAP.md und `discussion/HOERSTEL_MACHBARKEIT.md`
