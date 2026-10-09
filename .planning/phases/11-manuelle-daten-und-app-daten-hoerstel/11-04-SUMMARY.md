---
phase: 11-manuelle-daten-und-app-daten-hoerstel
plan: 04
subsystem: pipeline
tags: [hoerstel, texte, glossar, ve, app-daten]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 11-manuelle-daten-und-app-daten-hoerstel
    provides: "11-03: Hörsteler Vorberichtsdaten, meta.json, Eigenkapital"
provides:
  - "daten/manuell/texte/erklaerungen.md: 21 Erklärtexte für Hörstel (gleiche Schlüssel wie die App)"
  - "daten/manuell/texte/glossar.md: 27 Begriffe (GLOSSAR_SCHLUESSEL)"
  - "texte.py: Formeln ausgleichsruecklage_aufgebraucht_jahr_vor_verrechnung, allgemeine_ruecklage_ende_letztes_jahr_vor_verrechnung, schluesselzuweisung_anstieg_haushaltsjahr; Kreisumlage-Block in meta optional"
  - "ikvs_investitionen.ve_faelligkeiten_aus_uebersicht: Schritt 04 schreibt im IKVS-Layout ve_faelligkeiten.csv aus der VE-Übersicht (S. 586), Maßnahmen über die VE zugeordnet"
  - "app_daten.py: Maßnahmen ohne Sachkonto (IKVS) werden gruppiert"
  - "tests/test_hoerstel_texte.py (6 Tests), 2 VE-Tests in test_hoerstel_manuell.py"
affects: [11-05, 12-app-auf-hoerstel-umstellen]
---

# 11-04: Erklärtexte und Glossar Hörstel

## Ergebnis

- Alle Texte beschreiben Hörstel (Kreis Steinfurt, Kreis- und Jugendamtsumlage, Hebesatzerhöhung 2026, Ausgleichsrücklage bis 2029, Beteiligungen Hörsteler Energie GmbH und Stadtmarketing Hörstel UG, Abwassergebühren nach KAG als Grund für den Überschuss in PB 11). Jede Aussage hat einen Seitenbeleg im Hörsteler PDF; Zahlen stehen ausschließlich als Platzhalter.
- Schritt 07 läuft gegen die Hörsteler Daten (Scratch-Lauf der Schritte 01–05) vollständig durch; alle Platzhalter lösen auf. Plausibilität geprüft, z. B. Schulden pro Kopf 1.405 € (28.345.000 € / 20.166), Ausgleichsrücklage aufgebraucht 2029 (wie S. 72), allgemeine Rücklage Ende 2029 50,17 Mio. € (= Summe Eigenkapital S. 588).

## Entscheidungen

- **Gleiche Schlüssel, neuer Inhalt:** Die App fragt die Texte per Schlüssel an; Ostbevern-Themen ohne Hörsteler Entsprechung (Bilanzierungshilfe, NRW.Bank, HSK-Schwellen, Bindungsgrad je Produkt) werden sachlich umgedeutet, etwa „Pflicht oder freiwillig?“ mit der Auftragsgrundlage statt eines Bindungsgrads.
- **Eigene Formeln statt Umschalter:** Die Eigenkapitalübersicht Hörstels zeigt Stände zum 31.12. vor Ergebnisverrechnung, Ostbeverns Stände zu Jahresbeginn. Neue, benannte Formeln lassen die Ostbevern-Texte unverändert.
- **VE-Fälligkeiten aus der VE-Übersicht:** Das IKVS-Layout druckt keine Fälligkeiten je Maßnahme. Schritt 04 leitet sie aus der geprüften Abschrift ab (wie der Stellenplan); 14 von 15 VE werden über den Betrag einer Maßnahme zugeordnet, der Neubau des Verwaltungsgebäudes (5.100 T€) hat keine Maßnahme (Befund, siehe 10-01).

## Offene Punkte

- App-Anzeige der Texte und der fehlenden Ostbevern-Tabellen → Phase 12.
