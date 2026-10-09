# Manuell abgeschriebene Daten (Hörstel, Haushalt 2026)

Dieser Ordner enthält die Teile von `raw_data/haushalt-2026.pdf` (Stadt Hörstel, Axians IKVS), die
der Parser nicht liest: Vorberichtstabellen mit Fließtextlayout, Zahlen aus Grafiken und die
Bildseiten ohne Textebene (Stellenplan, Fraktionszuwendungen, Eigenkapital). Die Abschrift ist
**einmalig**: Kein Pipeline-Schritt überschreibt diese Dateien. Tippfehler fängt Regel 5 ab
(Summen und Gesamtplanzeilen), die CI prüft zusätzlich, dass sich der Ordner bei einem erneuten
Pipeline-Lauf nicht ändert. Der Ostbevern-Stand liegt unter `pipeline/referenz/ostbevern/daten/manuell/`.

Grundsatz: Abgeschrieben wird nur, was gedruckt ist. Teilt eine Tabelle ihre Summe nicht
vollständig auf („größere Abweichungen“), steht die Differenz als Posten `uebrige_*` mit
`anmerkung` „berechnet: …“ in der Datei. Tabellen, die Hörstel nicht druckt (Kita-Zuschüsse,
Einzelzuschüsse für laufende Zwecke, Kostenerstattungen im Detail), fehlen; welche Tabellen es
gibt, steht in `pipeline/jahrgaenge/2026.toml` unter `[layout.vorbericht]`.

## Spaltenformat (`VORBERICHT_SPALTEN`, `ostbevern/schema.py`)

| Spalte | Bedeutung |
|---|---|
| `tabelle` | Tabellenname (Dateiname ohne `.csv`, in `weitere_vorberichtstabellen.csv` der Tabellenname) |
| `position` | Gedruckte Reihenfolge (1-basiert); Rest- und Gesamtzeile stehen am Ende |
| `posten` | Schlüssel in Snake-Case ohne Umlaute |
| `posten_name` | Gedruckter Name, wortwörtlich (inkl. Sachkontonummer, wo gedruckt) |
| `ist_gesamt` | `true` für die gedruckte Summenzeile, genau eine je (`tabelle`, `jahr`) |
| `jahr`, `wertart` | 2024 `ergebnis`, 2025/2026 `ansatz`, 2027–2029 `planung` |
| `betrag_teur` | Betrag in T€, exakt wie gedruckt („--“ = 0) |
| `anmerkung` | Herkunft aus einer Grafik, Berechnung, Stichtag oder Fußnote |
| `quelle` | 1-basierte PDF-Seite |

## Dateien

| Datei / Tabelle | Quelle (PDF-Seite) | Jahre | Gegenprobe (Regel 5) |
|---|---|---|---|
| `steuerarten.csv` | 16 | 2024–2029 | GEP Z. 01; „Ausgleichsleistungen“ = Posten `kompensationszahlungen` (Familienleistungsausgleich, S. 20) |
| `zuwendungen.csv` | 15 (Summe), 22 (Schlüsselzuweisungen, Grafik) | 2024–2029 | GEP Z. 02; Rest `uebrige_zuwendungen` |
| `transferaufwendungen.csv` | 33 (Arten 2025/2026), 34/35 (Kreis- und Jugendamtsumlage, Grafik), 27 (Summe) | 2024–2029 | GEP Z. 15; Weitergabe an Kreis und Land = TP 1661101 Z. 15 |
| `investitionszuwendungen.csv` | 61 (Pauschalen), 80 (GFP Z. 18) | 2026 | GFP Z. 18 |
| `weitere_vorberichtstabellen.csv` | 24, 28, 30, 37 | 2025/2026 | GEP Z. 04, 05, 11, 13, 16, 07 |
| `verbindlichkeiten.csv` | 587 | Stand 01.01.2025 (`jahr` 2024), 01.01.2026 (2025), 31.12.2026 (2026) | Summe; Kreditfortschreibung mit GFP Z. 33/35 |
| `eigenkapital.csv` | 588 (Bild), int-Euro, Cent kaufmännisch gerundet | 2024–2029 | Summe; Jahresergebnis = GEP Z. 28; Satzung § 4 |
| `fraktionszuwendungen.csv` | 576/577 (Bild), int-Euro | 2024–2026 | Summe Teil A |
| `ve_uebersicht.csv` | 586 | fällig 2027–2029 | Summe = Satzung § 3 (18.331 T€) |
| `stellenplan.csv`, `stellenuebersicht.csv` | 568–574 (Bild) | 2025/2026 | Schritt 05 und Regel 10 |
| `meta.json` | 5, 7, 8, 12 | – | Regel 9 über die Eckwerte der Sollwertdatei |

### Transferaufwendungen

S. 33 gliedert die Transferaufwendungen 2025/2026 in fünf Arten. Die „Allgemeinen Umlagen“
sind dort die Umlagen an den Kreis Steinfurt; sie stehen hier getrennt als `kreisumlage` und
`jugendamtsumlage` (S. 34; 2025: 11.502 + 9.654 = 21.156 T€). Die „Steuerbeteiligungen“ sind die
Gewerbesteuerumlage (Erläuterungen Produkt 1661101, S. 559). Für 2024 und 2027–2029 stammen
Kreis- und Jugendamtsumlage aus der Grafik auf S. 35. Die Gewerbesteuerumlage ist für diese
Jahre berechnet (TP 1661101 Z. 15 minus Kreis- und Jugendamtsumlage); für 2025/2026 trifft diese
Rechnung die gedruckten Werte exakt. Der Rest bis zur Summe von S. 27 ist
`uebrige_transferaufwendungen`.

### Befunde in den Abschriften

| Tabelle | Jahr | Befund | Seite |
|---|---|---|---|
| leistungsentgelte | 2025 | Σ Posten 10.842 T€, Summe 10.841 T€ (Rundung) | 24 |
| sonstige_aufwendungen | 2026 | Σ Posten 2.369 T€, Summe 2.368 T€ (Rundung) | 37 |
| verbindlichkeiten | 2026 | Σ Posten 56.715 T€, gedruckte Summe 56.535 T€ | 587 |
| verbindlichkeiten | 2026 | Investitionskredite 43.887 T€; 28.345 + Kreditaufnahme 17.527 − Tilgung 2.294 = 43.578 T€ | 587, 81 |

### `meta.json`

Einwohner 20.166 (31.12.2024, Fortschreibung Zensus 2022, S. 5; dieselbe Zahl in der Tabelle
S. 67), Fläche 10.754 ha (S. 5), Hebesätze aus der Satzung § 6 (S. 8) mit Vorjahr aus der
Hebesatztabelle (S. 12), Satzungsbeschluss und Ausfertigung 04.02.2026 (S. 7/8). Hörstel druckt
keine Kreisumlage-Hebesätze und keine Aufteilung der Konzessionsabgaben; der Block
`kreisumlage` fehlt deshalb.

### `texte/`

Die Erklärtexte und das Glossar werden in Plan 11-04 für Hörstel neu geschrieben; bis dahin
stehen hier noch die Ostbevern-Texte.
