# Machbarkeit: Pipeline gegen den Haushaltsplan 2026 der Stadt Hörstel

Stand: 08.10.2026. Geprüft wurde `raw_data/haushalt-2026.pdf` (Branch `hoestel-transform`;
die Datei hieß dort `haushalt_2026.pdf` und wurde auf den Pfad aus `jahrgaenge/2026.toml`
umbenannt).

## Kurzfazit

Die Pipeline läuft für Hörstel **nicht**, und das lässt sich nicht allein über
`jahrgaenge/2026.toml` beheben. Das Hörsteler PDF stammt aus einer anderen
Software (Word-Export, Autor „Axians IKVS GmbH“, statt ProFIS+). Seitenaufbau,
Tabellenköpfe, Codesystem und Zahlenformat weichen grundlegend ab.

Wiederverwendbar sind die fachlichen Teile:

- das NKF-Zeilenwörterbuch in `ostbevern/zeilen.py` (Zeilennummern 01–38 sind identisch),
- die Prüflogik in Schritt 06,
- die App-Datenerzeugung in Schritt 07,
- die App selbst.

Die PDF-lesenden Schritte 01–05 und 08 müssen für das neue Layout neu geschrieben
oder stark angepasst werden.

## Umsetzungsstand

**Schritt 1 erledigt: Gesamtpläne im IKVS-Layout**

- `pipeline/jahrgaenge/2026.toml` und `2026_sollwerte.toml` beschreiben jetzt Hörstel. Die Ostbevern-Dateien liegen als Referenz für das ProFIS+-Layout unter `pipeline/jahrgaenge/archiv/`.
- Neuer Schlüssel `software = "ikvs"` in der Jahrgangsdatei (Standard `"profis"`), gelesen über `Jahrgang.software`.
- `pipeline/ostbevern/ikvs.py` liest Gesamtergebnisplan (S. 79) und Gesamtfinanzplan (S. 80–81). Gelöst sind dabei:
  - umbrochene Bezeichnungen mit Beträgen in einer Zwischenzeile,
  - `--` als 0 und Cent-Beträge, kaufmännisch auf Euro gerundet,
  - das abgetrennte Minuszeichen,
  - die ungedruckte Zeile „Änderung des Bestandes an fremden Finanzmitteln“.
  Gedruckte Zeilennummern werden auf die kanonischen Nummern aus `ostbevern/zeilen.py` abgebildet: Finanzplan „40 – Liquide Mittel“ ist kanonisch 41. Die mittelfristigen Jahre („Ansatz 2027“) gehen als Wertart `planung` in die CSVs ein.
- Schritt 02 (`02_plaene_extrahieren.py`) schreibt für IKVS bisher nur die GESAMT-Zeilen. Schritt 01 bricht für IKVS mit einem klaren Hinweis ab, sodass `alle.py` noch nicht durchläuft.
- `pipeline/tests/test_ikvs.py` prüft:
  - alle Zeilen gegen die Sollwerte,
  - Regel 1 (Zeilenformeln): 108 Prüfungen, 0 Abweichungen, auch nach der Rundung,
  - die Haushaltssatzung § 1–2 gegen die Gesamtpläne: 0 Abweichungen. Die VE aus § 3 folgen mit den Investitionsübersichten.
- Die eingecheckten Daten unter `daten/` stammen weiterhin aus dem Ostbevern-Lauf. Sie werden erst neu erzeugt, wenn die Pipeline für Hörstel durchläuft.

**Schritt 2 erledigt: Seitenklassifikation und Teilpläne (Phase 9)**

- `pipeline/ostbevern/ikvs_seiten.py` klassifiziert alle 592 Seiten ohne laufende Kopfzeile: Der Kontext (PB, Produkt) wird über die Trennseiten fortgeschrieben, jeder Plantitel wird dagegen geprüft. Hierarchie: 16 PB, 50 Produktgruppen, 69 Produkte; die PB-Startseiten stimmen mit dem Inhaltsverzeichnis überein.
- Schritt 02 liest alle 85 Teilergebnis- und 85 Teilfinanzpläne. Produktgruppen haben keinen eigenen Teilplan und werden als Summe ihrer Produkte gebildet; ihre Erträge und Aufwendungen 2026 treffen die gedruckten Haushaltsquerschnitte exakt.
- Prüfregeln 1–3: 11 Abweichungen über 1 €, alle im PDF so gedruckt. Neun davon sind Rundungsdifferenzen von 2 € bei den Ist-Werten 2024. Die übrigen betreffen die Transferaufwendungen: Die Teilpläne enthalten 5.800 € (2026) bzw. 4.400 € (2027) weniger als der Gesamtergebnisplan.
- Ostbevern läuft weiterhin unverändert als ProFIS+-Referenz.

**Nächste Schritte:** Produktinformationen (ohne Personennamen), Erläuterungen, Investitionsübersichten mit VE und Haushaltsquerschnitte als Kontrollquelle (Phase 10).

## Was getestet wurde

| Test | Ergebnis |
|---|---|
| `alle.py --jahr 2026` mit unveränderter TOML | Abbruch: „PDF hat 592 Seiten, Jahrgangsdatei erwartet 400“ |
| Schritt 01 mit provisorischer TOML (Seitenbereiche, 592 Seiten, 16 PB, 69 Produkte, Produktmuster `\d{7}`) | Abbruch: „0 Produkte gefunden, erwartet 69“ |
| `plaene.lies_plantabelle` direkt auf Gesamtergebnisplan S. 79 / Gesamtfinanzplan S. 80 | Abbruch: „keine Kopfzeile mit 'Nr.' gefunden“ |
| `zahlen.lies_betrag` auf Hörsteler Werte | `--` und `32.813.040,08` werden abgelehnt |
| `pytest` | 509 bestanden, 86 fehlgeschlagen, 50 Fehler. Die Fehlschläge betreffen die Tests, die Ostbevern-Seiten und -Sollwerte aus dem PDF lesen. Erwartet, da das PDF ausgetauscht ist. |

Die provisorische TOML wurde nach dem Test wieder zurückgesetzt.

## Strukturvergleich

| Merkmal | Ostbevern (ProFIS+) | Hörstel (IKVS/Word) | Folge |
|---|---|---|---|
| Seiten | 400, alle Hochformat | 592, Querschnitte und Stellenplan teils Querformat | TOML |
| Produktbereiche | 15 | 16 (inkl. 16 Allgemeine Finanzwirtschaft) | TOML, Sollwerte |
| Produktcode | 6-stellig (`150102`) | 7-stellig (`0111102`) | Code: `konfiguration.py` (`_SECHSSTELLIGER_PRODUKTCODE_MUSTER`), `seiten.py`, `quellen.py` |
| Produktgruppe | 4-stellig, eigene Kopfzeile | 5-stellig (`01111`), nur als Feld in den Produktinformationen, keine Kopfzeile | Code: `seiten.py` (`[:4]`), `querschnitte.py` |
| Kopfzeile je Seite | „Produktbereich NN …“ auf jeder Seite, darunter PG/Produkt | Keine laufende Kopfzeile. Nur auf Trennseiten „Produkt“ / „0111102 Name“ (zwei Zeilen) und im Tabellentitel „Teilergebnisplan 0111102 - Name“ | Code: `seiten._lies_kopfzeile` muss den Kontext von Seite zu Seite fortschreiben statt ihn je Seite zu lesen |
| Tabellenkopf Pläne | Zeile „Nr. … C Ergebnis Ansatz …“ + Jahreszeile | Kein „Nr.“, kein „C“. „Ergebnis 2024 Ansatz 2025 … Plan 2027“ (Teilpläne) bzw. „Ergebnis/Ansatz“ über „2024/2025“ (Gesamtpläne) | Code: `plaene._finde_kopfzeile`, `_lies_spaltenkoepfe` |
| Zeilenkennung | Nummer in eigener Spalte, Operator `+ - =` | „01 - Bezeichnung“ ohne Operator. In Teilplänen ist die Bezeichnung in einer schmalen Spalte umbrochen, die Beträge stehen in einer mittleren Umbruchzeile. | Code: `plaene.lies_plantabelle` (Zeilenzusammenbau) |
| Leere Werte | `0` / leer | `--` | Code: `zahlen.py` |
| Ergebnis 2024 | ganze Euro | mit Cent (`32.813.040,08`) in Gesamtplänen und Investitionsübersichten | Code: `zahlen.py` und Rundungsregel. Prüfregel „> 1 € Abweichung“ neu bewerten. |
| Teilpläne | alle Zeilen | nur belegte Zeilen und Summen | Code: Prüfregeln in `pruefung.py` müssen fehlende Zeilen als 0 werten |
| Spalten | „Planung 2027“, Finanzplan mit „VE 2026“ | „Plan 2027“ (Teilpläne) bzw. „Ansatz 2027“ (Gesamtpläne), VE nur in Investitionsübersicht | TOML |
| Investitionen | „Investitionsmaßnahmen (in C)“ | „Investitionsübersicht B 0111102 - …“, Maßnahmennummern `111.02-004`, Zeilen „Einzahlung/Auszahlung“ | Code: `investitionen.py` neu |
| Produktinformationen | Fachbereich, Verantwortliche/r, Ziele, Leistungen … | Produktbereich, Produktgruppe, Produktverantwortlicher, Beschreibung, Auftragsgrundlage, Zielgruppe, Stellenplan (VZÄ), Kennzahlen | TOML-Labels und `produkte.py`. Datenschutz: Produktverantwortlicher ist ein Personenname und muss verworfen werden. |
| Haushaltsquerschnitt | je PB eine Tabelle, PG 4-stellig | je PG (5-stellig) eine Querformatseite (S. 85–110), Gesamthaushalt S. 110 | Code: `querschnitte.py` neu |
| Stellenplan | Text, S. 284–290 | **Rastergrafik ohne Textebene** (S. 568–574) | Nicht mit pdfplumber lesbar. OCR nötig (tesseract fehlt im Container) oder manuelle Erfassung unter `daten/manuell/`. |
| Zuwendungen an Fraktionen, Eigenkapitalentwicklung | Text | ebenfalls Bilder (S. 576/577, 588) | wie Stellenplan |

## Provisorische Seitenbereiche für `jahrgaenge/2026.toml`

```toml
[anzahlen]
pdf_seiten = 592
produktbereiche = 16
produkte = 69          # 85 Teilergebnispläne = 69 Produkte + 16 PB-Summen

[seitenbereiche]
inhaltsverzeichnis = { von = 2, bis = 3 }
statistik = { von = 4, bis = 6 }
haushaltssatzung = { von = 7, bis = 8 }
vorbericht = { von = 9, bis = 78 }      # inkl. Erläuterung der Planpositionen S. 73–78
gesamtergebnisplan = { von = 79, bis = 79 }
gesamtfinanzplan = { von = 80, bis = 81 }
querschnitte = { von = 82, bis = 110 }  # 82–84 Produktübersicht, 85–110 Querschnitte je PG
teilplaene = { von = 111, bis = 566 }
stellenplan = { von = 567, bis = 574 }  # Bilder
zuwendungen_fraktionen = { von = 575, bis = 577 }
jahresabschluss = { von = 578, bis = 585 }  # Ergebnis-/Finanzrechnung 2024, Bilanz
verpflichtungen_schulden = { von = 586, bis = 588 }
wirtschaftsplaene = { von = 589, bis = 592 }  # Beteiligungen, Mitgliedschaften
```

Es gibt kein Leitbild-Kapitel. `leitbild` und `kostenstellen_budgets` entfallen.

## Schritt für Schritt

| Schritt | Einschätzung |
|---|---|
| 01 Seiten klassifizieren | **Umbau.** Neues Kopfzeilenmodell: Kontext fortschreiben, Produktcode aus Tabellentiteln lesen, 2/5/7-stellige Hierarchie. |
| 02 Pläne extrahieren | **Umbau.** Tabellenkopf, Zeilenzusammenbau bei umbrochenen Bezeichnungen, `--`, Cent-Beträge. Das Zeilenwörterbuch ist wiederverwendbar. |
| 03 Produktinfos/Erläuterungen | **Umbau.** Andere Felder. Erläuterungen haben die Form „Bezeichnung / Ansatz 2025 = X €, Ansatz 2026 = Y € / Text“ statt „Nr. NN“. |
| 04 Investitionen | **Neu.** Investitionsübersicht B mit anderem Aufbau. |
| Querschnitte | **Neu** (je PG statt je PB). |
| 05 Stellenplan | **Nicht automatisierbar ohne OCR.** Manuelle Erfassung empfohlen. |
| 06 Prüfen | Logik weitgehend wiederverwendbar. Muss mit fehlenden Teilplanzeilen umgehen. Sollwerte (`2026_sollwerte.toml`) komplett neu aus Satzung S. 7/8 und Gesamtplänen S. 79–81. |
| 07 App-Daten | Wiederverwendbar, sobald die CSVs in `daten/aufbereitet/` dasselbe Schema haben. `daten/manuell/` (Vorberichtstabellen, Einwohner in `meta.json`: Hörstel ≈ 21.000 laut S. 5) neu erfassen. |
| 08 Quellenbelege | Weitgehend wiederverwendbar. Schwärzliste (`pruefwoerter`) für Hörsteler Namen neu. |

## Empfohlenes Vorgehen

1. Eine eigene Leselogik je Software-Layout einführen: `ostbevern/` bleibt das ProFIS+-Layout, ein neues Modul übernimmt IKVS. So bleibt Ostbevern lauffähig und testbar. Dafür bräuchte die Jahrgangsdatei ein Feld wie `layout = "ikvs"`.
2. Mit Schritt 02 für die Gesamtpläne (S. 79–81) und der Satzung beginnen. Damit beantwortet die App bereits „Woher? / Wofür?“ auf Gesamtebene.
3. Danach die Teilpläne lesen (Schritte 01/02), dann Produktinfos, Investitionen und Querschnitte.
4. Stellenplan, Fraktionszuwendungen und Eigenkapital manuell als CSV erfassen.
