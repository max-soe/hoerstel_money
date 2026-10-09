# Konsistenzbericht Haushalt 2026

Diese Datei wird von `pipeline/06_pruefen.py` und von pytest erzeugt und darf nicht von Hand bearbeitet werden.

Gesamtstatus: grün

## Übersicht

| Regel | Status | Geprüfte Werte | Abweichungen | Lücken | Bekannte Befunde |
| --- | --- | --- | --- | --- | --- |
| Regel 1 – Zeilenformeln | grün | 7332 | 0 | 0 | 2 |
| Regel 2 – Produkte → PG → PB | grün | 8166 | 0 | 0 | 4 |
| Regel 3 – Produktbereiche → Gesamtergebnisplan | grün | 114 | 0 | 0 | 5 |
| Regel 4 – Sollwerte (Anhang B, Satzung § 1-3) | grün | 206 | 0 | 0 | 0 |
| Regel 5 – Manuelle Tabellen → Planzeilen | grün | 101 | 0 | 0 | 5 |
| Regel 6 – Investitionsmaßnahmen → Teil-/Gesamtfinanzplan | grün | 840 | 0 | 0 | 11 |
| Regel 7 – Haushaltsquerschnitte → PG-/PB-Teilpläne | grün | 409 | 0 | 0 | 0 |
| Regel 8 – Vollständigkeit der Produkte | grün | 346 | 0 | 0 | 0 |
| Regel 9 – Eckwerte (Anhang B.6) | grün | 7 | 0 | 0 | 0 |
| Regel 10 – Stellenplan: Stellenübersicht → Teil A/B | grün | 23 | 0 | 0 | 11 |

## Abweichungen

Keine.

## Lücken

Keine.

## Bekannte Befunde

| regel | plan | ebene | code | zeile | jahr | wertart | abweichung | pdf_seite | begruendung |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | teilergebnisplan | P | 0212601 | 10 | 2024 | ergebnis | -2 | 206 | Teilergebnisplan Produkt 0212601, Zeile 10 Ergebnis 2024 (S. 206): Summe der gedruckten Ertragszeilen gegen die gedruckte Zeile 10. Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 1 | teilergebnisplan | PG | 02126 | 10 | 2024 | ergebnis | -2 | 205 | Synthetische PG 02126 = Produkt 0212601 (einziges Produkt). Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 2 | teilergebnisplan | PB | 05 | 29 | 2024 | ergebnis | -2 | 275 | Teilergebnisplan PB 05 (S. 275) gegen die Summe seiner Produkte, Ergebnis 2024. Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 2 | teilergebnisplan | PB | 05 | 31 | 2024 | ergebnis | -2 | 275 | Teilergebnisplan PB 05 (S. 275) gegen die Summe seiner Produkte, Ergebnis 2024. Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 2 | teilergebnisplan | PB | 12 | 29 | 2024 | ergebnis | -2 | 443 | Teilergebnisplan PB 12 (S. 443) gegen die Summe seiner Produkte, Ergebnis 2024. Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 2 | teilergebnisplan | PB | 12 | 31 | 2024 | ergebnis | -2 | 443 | Teilergebnisplan PB 12 (S. 443) gegen die Summe seiner Produkte, Ergebnis 2024. Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 3 | gesamtergebnisplan | GESAMT |  | 10 | 2024 | ergebnis | -2 | 79 | Gesamtergebnisplan Zeile 10 Ergebnis 2024 (S. 79) gegen die Summe der 16 PB. Ist-Ergebnisse 2024 sind mit Cent gedruckt und werden je Wert kaufmännisch auf Euro gerundet; die Summe der gerundeten Zeilen weicht um -2 € von der gerundeten Summenzeile ab. Wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 3 | gesamtergebnisplan | GESAMT |  | 15 | 2026 | ansatz | -5800 | 79 | Gesamtergebnisplan (S. 79) Zeile 15 Transferaufwendungen gegen die Summe der 16 PB-Teilpläne: die Teilpläne enthalten 5800 € weniger als der Gesamtplan. Auch die Summe der Haushaltsquerschnitte je PG (S. 85-109) erreicht den Querschnitt Gesamthaushalt (S. 110) nicht; die Differenz steht so im PDF. |
| 3 | gesamtergebnisplan | GESAMT |  | 15 | 2027 | planung | -4400 | 79 | Gesamtergebnisplan (S. 79) Zeile 15 Transferaufwendungen gegen die Summe der 16 PB-Teilpläne: die Teilpläne enthalten 4400 € weniger als der Gesamtplan. Auch die Summe der Haushaltsquerschnitte je PG (S. 85-109) erreicht den Querschnitt Gesamthaushalt (S. 110) nicht; die Differenz steht so im PDF. |
| 3 | gesamtergebnisplan | GESAMT |  | 17 | 2026 | ansatz | -5800 | 79 | Folge der Differenz in Zeile 15 (siehe dort): Zeile 17 Ordentliche Aufwendungen weicht um denselben Betrag ab. |
| 3 | gesamtergebnisplan | GESAMT |  | 17 | 2027 | planung | -4400 | 79 | Folge der Differenz in Zeile 15 (siehe dort): Zeile 17 Ordentliche Aufwendungen weicht um denselben Betrag ab. |
| 5 | ve_uebersicht | GESAMT |  | summe_investitionen_ve | 2026 | ve | 5100000 | 586 | VE-Übersicht (S. 586) und Satzung § 3 (S. 7): 18.331 T€. Die Investitionsübersichten enthalten 13.231 T€; die VE „Neubau eines Verwaltungsgebäudes Hörstel“ über 5.100 T€ steht nur in der VE-Übersicht (Maßnahme 111.02-004 auf S. 124 druckt 250.000 € VE). |
| 5 | verbindlichkeiten | GESAMT |  | kredite_fortschreibung | 2026 | ansatz | -308842 | 587 | Übersicht über die Verbindlichkeiten (S. 587): Investitionskredite 01.01.2026 28.345 T€ + Kreditaufnahme 2026 17.527.000 € − Tilgung 2.293.842 € (Gesamtfinanzplan S. 81) = 43.578.158 €; gedruckt sind 43.887 T€ zum 31.12.2026. |
| 5 | vorbericht_leistungsentgelte | GESAMT |  | summe_posten | 2025 | ansatz | 1000 | 24 | Vorbericht S. 24, öffentlich-rechtliche Leistungsentgelte Plan 2025: Summe der vier Posten 10.842 T€, gedruckte Summe 10.841 T€ (Rundung). |
| 5 | vorbericht_sonstige_aufwendungen | GESAMT |  | summe_posten | 2026 | ansatz | 1000 | 37 | Vorbericht S. 37, sonstige ordentliche Aufwendungen Plan 2026: Summe der Posten 2.369 T€, gedruckte Summe 2.368 T€ (Rundung). |
| 5 | vorbericht_verbindlichkeiten | GESAMT |  | summe_posten | 2026 | ansatz | 180000 | 587 | Übersicht über die Verbindlichkeiten (S. 587), Stand 31.12.2026: die Zeilen 1-8 ergeben 56.715 T€, Zeile 9 druckt 56.535 T€. Wie gedruckt abgeschrieben. |
| 6 | investitionen_gesamt | GESAMT |  | 23 | 2024 | ergebnis | 2 | 80 | Folge der Produktbefunde 0212201 und 1557302 (siehe dort) im Gesamtfinanzplan (S. 80); 2024 zusätzlich Cent-Rundung der Ist-Ergebnisse. |
| 6 | investitionen_gesamt | GESAMT |  | 23 | 2025 | ansatz | -62333 | 80 | Folge der Produktbefunde 0212201 und 1557302 (siehe dort) im Gesamtfinanzplan (S. 80); 2024 zusätzlich Cent-Rundung der Ist-Ergebnisse. |
| 6 | investitionen_gesamt | GESAMT |  | 30 | 2026 | ansatz | -3125 | 80 | Folge der Produktbefunde 0212201 und 1557302 (siehe dort) im Gesamtfinanzplan (S. 80); 2024 zusätzlich Cent-Rundung der Ist-Ergebnisse. |
| 6 | investitionen_gesamt | GESAMT |  | 30 | 2027 | planung | -3125 | 80 | Folge der Produktbefunde 0212201 und 1557302 (siehe dort) im Gesamtfinanzplan (S. 80); 2024 zusätzlich Cent-Rundung der Ist-Ergebnisse. |
| 6 | investitionen_gesamt | GESAMT |  | 30 | 2028 | planung | -3125 | 80 | Folge der Produktbefunde 0212201 und 1557302 (siehe dort) im Gesamtfinanzplan (S. 80); 2024 zusätzlich Cent-Rundung der Ist-Ergebnisse. |
| 6 | investitionen_gesamt | GESAMT |  | 30 | 2029 | planung | -3125 | 80 | Folge der Produktbefunde 0212201 und 1557302 (siehe dort) im Gesamtfinanzplan (S. 80); 2024 zusätzlich Cent-Rundung der Ist-Ergebnisse. |
| 6 | investitionen_produkt | P | 0212201 | 30 | 2026 | ansatz | -3125 | 196 | Produkt 0212201 (S. 196): die Investitionsübersicht druckt 105.000 € (2026) bzw. keine Auszahlung (2027-2029), der Teilfinanzplan Zeile 30 108.125 € bzw. 3.125 € je Jahr. |
| 6 | investitionen_produkt | P | 0212201 | 30 | 2027 | planung | -3125 | 196 | Produkt 0212201 (S. 196): die Investitionsübersicht druckt 105.000 € (2026) bzw. keine Auszahlung (2027-2029), der Teilfinanzplan Zeile 30 108.125 € bzw. 3.125 € je Jahr. |
| 6 | investitionen_produkt | P | 0212201 | 30 | 2028 | planung | -3125 | 196 | Produkt 0212201 (S. 196): die Investitionsübersicht druckt 105.000 € (2026) bzw. keine Auszahlung (2027-2029), der Teilfinanzplan Zeile 30 108.125 € bzw. 3.125 € je Jahr. |
| 6 | investitionen_produkt | P | 0212201 | 30 | 2029 | planung | -3125 | 196 | Produkt 0212201 (S. 196): die Investitionsübersicht druckt 105.000 € (2026) bzw. keine Auszahlung (2027-2029), der Teilfinanzplan Zeile 30 108.125 € bzw. 3.125 € je Jahr. |
| 6 | investitionen_produkt | P | 1557302 | 23 | 2025 | ansatz | -62333 | 543 | Produkt 1557302 (S. 542/543): der Teilfinanzplan druckt in Zeile 23 für 2025 62.333 €, die Investitionsübersicht keine Einzahlung. |
| 10 | stellenuebersicht_beamte | GESAMT |  | A10 | 2026 | ansatz | 1 | 570 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 1 Hundertstel ab. |
| 10 | stellenuebersicht_beamte | GESAMT |  | A11 | 2026 | ansatz | 1 | 570 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 1 Hundertstel ab. |
| 10 | stellenuebersicht_beamte | GESAMT |  | A12 | 2026 | ansatz | 2 | 570 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 2 Hundertstel ab. |
| 10 | stellenuebersicht_beamte | GESAMT |  | A14 | 2026 | ansatz | 4 | 570 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 4 Hundertstel ab. |
| 10 | stellenuebersicht_beamte | GESAMT |  | A9Z | 2026 | ansatz | 2 | 570 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 2 Hundertstel ab. |
| 10 | stellenuebersicht_tarif | GESAMT |  | 05 | 2026 | ansatz | 1 | 572 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 1 Hundertstel ab. |
| 10 | stellenuebersicht_tarif | GESAMT |  | 06 | 2026 | ansatz | 1 | 572 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 1 Hundertstel ab. |
| 10 | stellenuebersicht_tarif | GESAMT |  | 07 | 2026 | ansatz | 1 | 572 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 1 Hundertstel ab. |
| 10 | stellenuebersicht_tarif | GESAMT |  | 08 | 2026 | ansatz | -1 | 572 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um -1 Hundertstel ab. |
| 10 | stellenuebersicht_tarif | GESAMT |  | 09b | 2026 | ansatz | 2 | 572 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um 2 Hundertstel ab. |
| 10 | stellenuebersicht_tarif | GESAMT |  | 09c | 2026 | ansatz | -2 | 572 | Stellenübersicht (S. 570-573): die Zellen je Produkt sind auf Hundertstel gerundet, die gedruckte Spaltensumme (= Teil A/B, S. 568/569) offenbar aus ungerundeten Anteilen gebildet. Die Summe der gerundeten Zellen weicht um -2 Hundertstel ab. |

## Veraltete Befunde

Keine.

## Seiten mit typ=unbekannt

Keine.
