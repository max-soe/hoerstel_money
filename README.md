# Hörstel Money

Hörstel Money erklärt dir den Haushalt 2026 der Stadt Hörstel. Die App beantwortet zwei Leitfragen: **Wo kommt das Geld der Stadt her?** und **Wofür wird es ausgegeben?** Jede Zahl, die du hier siehst, hat eine Python-Pipeline aus dem veröffentlichten Haushalts-PDF extrahiert und automatisch gegen die Planwerte geprüft. Dies ist ein **inoffizielles Projekt** und steht in keiner Verbindung zur Stadtverwaltung.

## Stand

Die App ist aus Ostbevern Money entstanden (Phasen 1 bis 7: Pipeline mit Prüfregeln, alle Seiten der App, Quellenbelege, Barrierefreiheit, Browser-Tests, CI mit Veröffentlichung auf GitHub Pages). In den Phasen 8 bis 12 wurde sie auf den Haushalt der Stadt Hörstel umgestellt: Die Pipeline liest jetzt auch das Layout von Axians IKVS, Bildseiten und Vorberichtstabellen sind in `daten/manuell/` abgeschrieben, und alle Prüfregeln laufen für Hörstel grün (belegte Abweichungen in `daten/pruefberichte/befunde.md`). Ostbevern bleibt als ProFIS+-Referenz unter `pipeline/referenz/ostbevern/` erhalten und wird in Tests und CI mitgeprüft. Stand und offene Punkte: [`.planning/ROADMAP.md`](.planning/ROADMAP.md).

Name und Art der Kommune (`[layout.kommune]` in `pipeline/jahrgaenge/2026.toml`) kommen aus den Daten; die App nennt keinen Ortsnamen im Code.

## Aufbau

- `raw_data/` — das Quell-PDF des Haushalts
- `pipeline/` — die Python-Pipeline, die das PDF ausliest und prüft
- `daten/` — von der Pipeline erzeugte und geprüfte Daten
- `app/` — die Vue-3-Webanwendung
- `discussion/SPEZIFIKATION.md` — die fachliche Spezifikation

## Schnellstart

```bash
uv sync --directory pipeline
uv run --directory pipeline pytest
npm --prefix app ci
npm --prefix app run dev
npm --prefix app run build
```

Alle Befehle und Konventionen stehen in [`.claude/CLAUDE.md`](.claude/CLAUDE.md).

### Browser-Tests mit der Schrift der CI

Der Breitentest der Kennzahl-Kacheln (`app/e2e/kacheln.spec.ts`) misst gerenderte Beträge und hängt deshalb von der Systemschrift ab. GitHub Actions läuft auf `ubuntu-24.04` und rendert mit DejaVu Sans; im nackten Playwright-Image wäre es eine andere, schmalere Schrift, und die Messung wäre wertlos. Damit du lokal dieselben Zahlen bekommst, startest du die Browser-Tests über `scripts/e2e-wie-ci.sh`. Das Skript braucht Docker, lädt das Schriftpaket einmal nach `~/.cache/hoerstel-money` (die Prüfsumme ist fest eingetragen) und ändert nichts an der App.

Bereite dafür eine Kopie von `app/` mit Linux-Abhängigkeiten und einem Build vor (`npm ci` und `npm run build-only`). Auf macOS führst du beides im Image `mcr.microsoft.com/playwright:v1.63.0-noble` aus, weil `app/node_modules` dort macOS-Binärdateien enthält. Dann:

```bash
scripts/e2e-wie-ci.sh <Verzeichnis-der-Kopie> --project=ci
```

## Veröffentlichung auf GitHub Pages

Die App ist eine statische Seite ohne Backend. Der Workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) baut sie und veröffentlicht sie auf GitHub Pages, sobald der Stand auf `main` liegt und alle Prüfungen grün sind. Ein Pull Request oder ein anderer Branch veröffentlicht nie etwas. Das Anlegen des Repositories und der erste Push sind bewusst deine Handgriffe, damit nichts ungewollt öffentlich wird:

1. Das Repository liegt unter `max-soe/hoerstel_money`. Für GitHub Pages im kostenlosen Tarif muss es **öffentlich** sein.
2. Bringe den Stand auf `main` (Merge des Arbeitsbranches über einen Pull Request).

3. Öffne im Repository **Settings → Pages** und stelle **Source** auf **„GitHub Actions“**. Kostenlose Organisationen brauchen für Pages ein öffentliches Repository; prüfe in den Einstellungen der Organisation, dass Pages erlaubt ist.
4. Öffne den Reiter **Actions**. Der Workflow „CI“ prüft Pipeline und App, führt den Smoke-Test aus (jede Seite, Konsole, Netzwerk, Barrierefreiheit mit axe) und veröffentlicht erst danach. Ist der Lauf grün, findest du die App unter **https://max-soe.github.io/hoerstel_money/**. Liegt das Repository in einem anderen Account, ersetze `max-soe` durch dessen Namen.

Schlägt eine Prüfung fehl, bleibt die bisherige Seite unverändert online. Du kannst den Workflow auch von Hand starten: **Actions → CI → Run workflow** auf dem Branch `main`.

Die App funktioniert unter jedem Unterpfad: Vite baut mit `base: './'` und die App nutzt den Hash-Router, deshalb ist keine Anpassung nötig, wenn das Repository anders heißt.

## Pflege beim Jahrgangswechsel

Neben der Pipeline-Konfiguration (`pipeline/jahrgaenge/{jahr}.toml`) prüfst du bei einem neuen Haushaltsjahr diese Stellen von Hand:

- **Link auf das Original-PDF:** `ORIGINAL_PDF_URL` in `app/src/config.ts` zeigt auf eine Datei der Stadt. Ersetzt die Stadt die Datei (Korrektur, Nachtragshaushalt), liefert der alte Link 404, und alle Links „Seite n im Original-PDF öffnen“ laufen ins Leere, ohne dass ein Test es merkt. Öffne die URL deshalb vor jeder Veröffentlichung einmal und trage bei einem neuen Jahrgang die neue Adresse ein.
- **Name der Kommune und Texte:** `[layout.kommune]` im Jahrgang sowie die Erklärtexte und das Glossar in `daten/manuell/texte/` (darunter die Leitsätze `nicht_im_haushalt_*`, was außerhalb des Haushalts steht).
- **Impressum und Kontakt:** `KONTAKT_EMAIL`, `IMPRESSUM_NAME` und `IMPRESSUM_ANSCHRIFT` in `app/src/config.ts`.
- **Breite der Kennzahl-Kacheln:** Die Mindestspur `--om-kachel-mindestbreite` in `app/src/styles/basis.css` ist an die breitesten Beträge des Jahrgangs 2026 und an die CI-Schrift gekoppelt. Der Breitentest (`app/e2e/kacheln.spec.ts`) schlägt nur bei Überlauf an und protokolliert die Reserve; bei einem Jahrgang mit breiteren Beträgen liest du das Protokoll und hebst den Wert bei Bedarf an.

## Lizenz

MIT, siehe [`LICENSE`](LICENSE).

## Dank

Inspiriert von [Münster Money (Code for Münster)](https://github.com/codeformuenster/haushalt-muenster-2026). Es wurde kein Code übernommen — die Komponentennamen folgen nur der Vorlage.
Dies ist ein Fork von https://github.com/bitwerkstatt/ostbevern_money. Der Code wurde für die Stadt Hörstel angepasst.

Die selbst gehosteten Icons stammen von Font Awesome Free (CC BY 4.0).
