---
gsd_state_version: "1.0"
milestone: v2.0
milestone_name: Hörstel
status: In progress
stopped_at: Phase 12 complete (Milestone v2.0) (von Hand gepflegt, ohne GSD-Befehle)
last_updated: "2026-10-09T00:00:00.000Z"
last_activity: 2026-10-09
last_activity_desc: Upstream v1.0.1 (bitwerkstatt/ostbevern_money) auf Branch claude/upstream-v1.0.1 integriert, siehe .planning/UPSTREAM.md; Phase 12 und v2.0 fertig
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 9
  completed_plans: 9
  percent: 80
current_phase: 11
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-09)

**Core value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt. Die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.
**Current focus:** Meilenstein v2.0 Hörstel: den Haushalt 2026 der Stadt Hörstel (IKVS-Layout) lesen und die App darauf umstellen.

## Current Position

Milestone: v2.0 Hörstel (Phases 8-12)
Phase: 12 of 8-12 (App auf Hörstel umstellen) — complete
Plan: 11-05 complete
Status: Milestone v2.0 complete — bereit für Merge nach main und Veröffentlichung
Last activity: 2026-10-09 — Phase 12 abgeschlossen

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

Decisions are logged in PROJECT.md Key Decisions table (Stand v2.0, Phase 8). Der Abgleich mit dem Ursprungsprojekt (Remote `upstream`) ist in `.planning/UPSTREAM.md` festgehalten. Die Phasen-Entscheidungen von v1.0 sind in `.planning/milestones/v1.0-phases/` archiviert.

### Pending Todos

None.

### Blockers/Concerns

Aus v2.0:
- Die App ist auf Hörstel umgestellt und geprüft (vitest, Playwright mit axe, Sichtprüfung; Stand 12-04). Offen: Lighthouse-Lauf (Docker), PDF-Link mit `#page=n` von Hand prüfen, Merge nach `main` für die Veröffentlichung; die CI läuft nur für `main` und Pull Requests.
- Quellenbelege Hörstel: 899 von 2.768 Belegen ohne Markierung (597 davon berechnete Produktgruppen-Zeilen, 171 Stellenplan auf Bildseiten, Rest Vorberichtsgrafiken und umbrochene Tabellenzeilen); die App zeigt dann die Seite ohne Markierung.
- Hörstel druckt Ist-Ergebnisse 2024 mit Cent; gerundet wird kaufmännisch auf Euro (Rundungsbefunde in `befunde.md`).

Aus v1.0 übernommen (offen):
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
Stopped at: Phase 12 complete
Resume file: .planning/phases/11-manuelle-daten-und-app-daten-hoerstel/11-05-SUMMARY.md

## Operator Next Steps

- Phase 12 (App auf Hörstel umstellen, HOE-13): App-Typen und -Tests an die Hörsteler Daten anpassen, Texte, Namen, Links, Deployment
