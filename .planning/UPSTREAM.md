# Upstream-Abgleich mit bitwerkstatt/ostbevern_money

Dieses Repository ist ein Fork von <https://github.com/bitwerkstatt/ostbevern_money> (Remote `upstream`).
Dieses Dokument hält fest, welcher Upstream-Stand eingearbeitet ist und wie bei einem weiteren Abgleich vorzugehen ist.

## Stand

| Upstream | Eingearbeitet | Branch | Inhalt |
|---|---|---|---|
| v1.0.1 (`61225a9`) | 2026-10-09 | `claude/upstream-v1.0.1` | 216 Commits: 59 mit Code (Textkorrekturen TXT-01..06, Barrierefreiheit A11Y-01..03, Superlativ-Fix G-09-01, `rd.`-Regel in `format.ts`, gemeinsame Hilfsfunktionen), 157 Planungsdokumente (Archiv unter `.planning/milestones/v1.0.1-phases/`) |

## Vorgehen beim nächsten Abgleich

1. `git fetch upstream` und `git merge --no-commit --no-ff upstream/main` auf einem eigenen Branch.
2. Konflikte: Hörstel-Logik behalten, Upstreams neue Hilfsfunktionen übernehmen. `.planning/PROJECT.md`, `ROADMAP.md`, `STATE.md`, `README.md` und `CLAUDE.md` bleiben in der Hörsteler Fassung. Erklärtexte und Glossar (`daten/manuell/texte/`) ebenfalls; Upstreams Änderungen daran gehören in die Ostbevern-Referenz (`pipeline/referenz/ostbevern/daten/manuell/texte/`): `git diff <alt> upstream/main -- daten/manuell/texte | git apply --directory=pipeline/referenz/ostbevern`.
3. **Zuerst die Typprüfung** (`npm --prefix app run type-check`): Upstream entfernt oder benennt Hilfsfunktionen um, die Git still zusammenführt (hier: `postenName`, `jahrIndex`, `betragMitHinweis`).
4. Pipeline-Schritt 07 für Hörstel **und** Referenz (`PIPELINE_REFERENZ=referenz/ostbevern`) neu erzeugen; die Textprüfung wird von Upstream verschärft (keine getippten Jahreszahlen, Jahresbeschriftung je Absatz).
5. Gesamte Suite: Pipeline, App, Playwright (`ci`, `mobil`).

## Entscheidungen aus dem Abgleich v1.0.1

- **Superlativ „größter Einzelposten“ (G-09-01):** `istGroessterEinzelposten` vergleicht die Weitergabe an Kreis und Land als Ganzes mit jedem anderen Aufgabenbereich und jeder Aufwandsart ohne Transferaufwendungen. Upstream verglich die Kreisumlage allein; in Hörstel (Kreisumlage 12,5 + Jugendamtsumlage 10,2 + Gewerbesteuerumlage 1,3 Mio. €) läge sie in einzelnen Jahren unter den Sach- und Dienstleistungen, die Weitergabe insgesamt nicht.
- **Jahre in Erklärtexten:** nur als Platzhalter (`jahr.haushaltsjahr`, `jahr.vorjahr`, `jahr.haushaltsjahr_plus_1/2`, `jahr.letztes_jahr`, `jahr.fest_JJJJ`). Verbindlichkeiten und Eigenkapital sind unter dem Vorjahr abgelegt (Stand 31.12. bzw. 01.01. des Haushaltsjahrs); die Texte sagen deshalb „zum Jahresende {{jahr.vorjahr|jahr}}“.
- **`.planning/milestones/v1.0.1-phases/`** bleibt als Archiv im Repo, damit künftige Abgleiche keine Konflikte „geändert/gelöscht“ erzeugen.
