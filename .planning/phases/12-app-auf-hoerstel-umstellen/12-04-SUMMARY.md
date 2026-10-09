---
phase: 12-app-auf-hoerstel-umstellen
plan: 04
subsystem: app, e2e
tags: [hoerstel, playwright, axe, kacheln, sichtpruefung, sankey, barrierefreiheit]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 12-app-auf-hoerstel-umstellen
    provides: "12-03"
provides:
  - "Browser-Tests auf Hörstel: Projekt ci 81/81 (Smoke mit axe WCAG 2.0/2.1 A/AA auf allen Routen, Interaktion, Quellen-Seitenleiste, Kachelbreiten mit DejaVu Sans), Projekt mobil 13/14 (ein Fall datenabhängig übersprungen), Projekt texte grün"
  - "e2e: Seitenformat und Markierung der Stellenplan-Belege aus quellen.json statt Ostbevern-Querformat; Titel aus haushalt.kommune"
  - "geldfluss.ts: sankeyHoehe() und beschriftbareKnoten() (Beschriftungen nach Betrag, ohne Überlappung)"
  - "balken.ts: Achsennamen höchstens zweizeilig; StellenNachTeil ohne unrundes Achsenmaximum; RueckgangBalken ohne Schwellen mit rundem Maximum"
  - "ProduktPage: Auftragsgrundlage und Zielgruppe unter „Auf einen Blick“, Abschnitt nur mit Inhalt; Zurück-Schaltfläche bricht um (360 px)"
  - "RatEntscheidetPage/NichtBeeinflussbarBlock: Texte ohne Bezug auf einen Balken, wenn es keinen gibt"
affects: []
---

# 12-04: Browser-Tests und Sichtprüfung

## Ergebnis

- Alle Browser-Tests laufen mit den Hörsteler Daten. Lokal mit dem vorinstallierten Chromium (Playwright 1.63 erwartet eine neuere Revision; Zusatzkonfiguration nur für den Lauf, nicht eingecheckt) und einer Fontconfig nur mit DejaVu Sans wie in der CI.
- Sichtprüfung aller Routen bei 1280 px und /geldfluss, /produkt bei 360 px. Gefunden und behoben:
  1. /produkt bei 360 px scrollte waagerecht (Zurück-Schaltfläche mit langem PG-Namen, 438 px).
  2. Sankey: Beschriftungen der kleinen Aufgabenbereiche lagen übereinander (Hörstel hat mehr kleine PB); `hideOverlap` wirkt beim Sankey nicht. Jetzt wächst die Höhe mit der Knotenzahl, und Beschriftungen werden nach Betrag vergeben, nur ohne Überdeckung.
  3. Lange Maßnahmen- und Ertragsnamen an Balkenachsen überlappten (jetzt höchstens zwei Zeilen).
  4. Rückgangsdiagramm ohne HSK-Schwelle: überlappende oberste Achsenwerte; Stellen nach Teil: unrundes Achsenmaximum „116,39“.
  5. Rat-Seite: ungrammatischer Satz mit dem Hörsteler Produktnamen „Steuern, allg. Zuweisungen u. allg. Umlagen“, Verweise auf einen Balken, den es ohne Bindungsgrad nicht gibt (auch im Erklärtext ueberschuss_produkte).
  6. Produktseite: leere Überschrift „Auf einen Blick“ (Hörstel druckt keine Kopffelder); die gedruckte Auftragsgrundlage und Zielgruppe fehlten.
- vitest 2.069/2.069, Typprüfung, Lint, Format, Build grün.

## Offen

- Lighthouse-a11y (≥ 95, `scripts/lighthouse-a11y.sh`) braucht Docker und eine Paketprüfung durch den Nutzer; hier nicht gelaufen. axe ist auf allen Routen grün.
- Der mobile Test „Querformatseite scrollt nur im eigenen Rahmen“ ist für Hörstel übersprungen: Die Stellenübersicht im Querformat (S. 570–574) ist nur per Fußnote belegt, kein Quelle-Knopf führt dorthin.
- PDF-Link auf hoerstel.de (Download-Token) und `#page=n` im Browser von Hand prüfen; aus der Cloud-Umgebung nicht erreichbar.
