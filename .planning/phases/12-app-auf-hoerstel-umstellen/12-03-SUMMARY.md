---
phase: 12-app-auf-hoerstel-umstellen
plan: 03
subsystem: app, pipeline, docs
tags: [hoerstel, kommune, texte, impressum, readme, deployment]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 12-app-auf-hoerstel-umstellen
    provides: "12-02"
provides:
  - "[layout.kommune] im Jahrgang → haushalt.kommune → app/src/lib/kommune.ts (KOMMUNE_NAME, KOMMUNE_ART, KOMMUNE_VOLL, SEITENNAME)"
  - "vite.config.ts: index.html-Titel und -Beschreibung aus haushalt.json (%OM_SEITENNAME%, %OM_KOMMUNE%)"
  - "Erklärtexte nicht_im_haushalt_{ausgaben,einnahmen,kurz} je Kommune; HinweisNichtImHaushalt ohne festen Wortlaut"
  - "config.ts: Impressum und Kontakt Max Soest (Hörstel), ORIGINAL_PDF_URL auf hoerstel.de"
  - "Wächtertest: kein Ortsname und kein festes „der Gemeinde/Stadt“ im App-Code (außer kommune.ts, config.ts)"
  - "README, CI-Kommentare, Skripte auf Hörstel und max-soe/hoerstel_money"
affects: [12-04]
---

# 12-03: Texte, Namen, Links, README, Deployment

## Ergebnis

- App heißt „Hörstel Money“; alle Texte nennen „die Stadt“ bzw. „der Stadt Hörstel“ aus den Daten. Die Ostbevern-Referenz trägt „Gemeinde Ostbevern“.
- Die Ostbevern-Leitsätze „Was nicht im Haushalt steht“ (Hallenbad BBO, Abwasser TEO) wären für Hörstel falsch gewesen: Abwasserbeseitigung (1153801) und Hallenbad Riesenbeck (0842403) stehen im Hörsteler Haushalt. Die Leitsätze sind jetzt geprüfte Texte je Kommune (Hörsteler Energie GmbH, Stadtmarketing Hörstel UG, S. 25, 590, 591).
- Deployment unverändert (ci.yml, `base: './'`); Pages-Adresse laut README https://max-soe.github.io/hoerstel_money/.
- vitest 2.068/2.068, Typprüfung, Lint, Format, Build grün.

## Offen

- Der PDF-Link (hoerstel.de, Download-Token) konnte aus der Cloud-Umgebung nicht geprüft werden (Proxy 403). Ob `#page=n` springt, hängt davon ab, ob der Server das PDF inline ausliefert → Sichtprüfung in 12-04.
