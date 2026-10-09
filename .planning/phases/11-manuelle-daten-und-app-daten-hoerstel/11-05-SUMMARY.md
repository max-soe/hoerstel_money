---
phase: 11-manuelle-daten-und-app-daten-hoerstel
plan: 05
subsystem: pipeline, ci
tags: [hoerstel, befunde, pruefung, quellenbelege, datenschutz, alle-py, ci]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 11-manuelle-daten-und-app-daten-hoerstel
    provides: "11-02 bis 11-04: Stellenplan, Vorberichtsdaten, Texte, VE-Fälligkeiten"
provides:
  - "daten/pruefberichte/befunde.md (Hörstel): 38 belegte Abweichungen, Hinweise zu Erläuterungsansätzen"
  - "pruefung.py: Regel 4 (Satzung § 3) und VE-Übersicht im IKVS-Layout ohne VE-Spalte im Gesamtfinanzplan"
  - "produkte.py: Schwärzung des Produktverantwortlichen im IKVS-Layout (_ikvs_personenfeld_rechtecke)"
  - "quellen.py: IKVS-Planzeilen (umbrochene Blöcke), IKVS-Maßnahmen, berechnete Zeilen/Posten, Produktkopf; Belegschlüssel mit leerem Konto"
  - "jahrgaenge/2026.toml: [layout.quellenbelege]"
  - "daten/, app/src/data/, app/public/quellen/ (374 Belegseiten) aus Hörstel"
  - ".github/workflows/ci.yml: Reproduzierbarkeit Hörstel plus Ostbevern-Referenz"
affects: [12-app-auf-hoerstel-umstellen]
---

# 11-05: Prüfung, App-Daten, Quellenbelege und CI für Hörstel

## Ergebnis

- `alle.py` läuft für Hörstel vollständig: Schritte 01–08, alle 10 Prüfregeln grün (Regel 1: 7.332, Regel 2: 8.166, Regel 3: 114, Regel 4: 206, Regel 5: 101, Regel 6: 840, Regel 7: 409, Regel 8: 346, Regel 9: 7, Regel 10: 23 Werte), 38 belegte Befunde, keine veralteten Befunde.
- Zweiter Lauf ohne Diff in `daten/` und `app/src/data/` und ohne neue Belegbilder (Reproduzierbarkeit wie in der CI).
- Quellenbelege: 2.768 Belege auf 374 Seiten; 899 ohne Markierung (597 berechnete Produktgruppen-Zeilen, 171 Stellenplanwerte auf Bildseiten, 15 VE nur in der Übersicht, Rest Vorberichtsgrafiken und umbrochene Tabellenzeilen). Der Name unter „Produktverantwortlicher“ ist auf allen 69 Produktseiten geschwärzt (Sichtprüfung S. 116); die Datenschutz-Prüfliste zeigt sonst nur Sachbegriffe und die Unterschrift des Bürgermeisters unter der Satzung (wie bei Ostbevern ungeschwärzt).

## Befunde (Schlüsseltabelle)

| Regel | Anzahl | Inhalt |
|---|---|---|
| 1 | 2 | Cent-Rundung Produkt 0212601/PG 02126, Z. 10 2024 |
| 2 | 4 | Cent-Rundung PB 05 und PB 12, Z. 29/31 2024 |
| 3 | 5 | Cent-Rundung GEP Z. 10 2024; Transferaufwendungen der Teilpläne 5.800 € (2026) bzw. 4.400 € (2027) unter dem Gesamtplan (Z. 15/17) |
| 5 | 5 | zwei Rundungen von 1 T€, Summe der Verbindlichkeiten (180 T€), Kreditfortschreibung (309 T€), VE 5.100 T€ nur in der VE-Übersicht |
| 6 | 11 | Investitionsübersicht ≠ Teilfinanzplan bei 0212201 und 1557302, Folgen im Gesamtfinanzplan |
| 10 | 11 | gerundete Zellen der Stellenübersicht |

## Entscheidungen

- **VE im IKVS-Layout:** Satzung § 3 wird gegen den Gesamtbetrag der VE-Übersicht geprüft, die VE-Übersicht gegen die Summe der VE der Investitionsübersichten (Zeile `summe_investitionen_ve`); der Gesamtfinanzplan hat keine VE-Spalte.
- **Schwärzung über das Personenfeld:** wie bei Ostbevern im Produktcode (Abbruch, wenn das Feld fehlt), nicht über `schwaerzen_nach`.
- **Belegmarkierung best effort:** Was nicht als Zeile auffindbar ist, zeigt die Seite ohne Markierung; berechnete Werte sind als „berechnet“ gekennzeichnet statt als „nicht gefunden“.
- **CI:** Der Reproduzierbarkeitsschritt prüft jetzt Hörstel; ein zweiter Schritt prüft weiter die Ostbevern-Referenz.

## Offene Punkte (Phase 12)

- Die App ist noch auf Ostbevern zugeschnitten: Typprüfung und 242 von 1.640 vitest-Tests schlagen mit den Hörsteler Daten fehl (u. a. `meta.kreisumlage` fehlt, `konto`/`fachbereich` null, Ostbevern-Werte in Tests). Die CI läuft nur für `main` und Pull Requests; ein Pull Request sollte erst nach Phase 12 geöffnet werden.
- Belegschlüssel mit leerem Konto: die App muss `konto ?? ''` verwenden (`inv:{produkt}:{massnahme}::{richtung}`).
