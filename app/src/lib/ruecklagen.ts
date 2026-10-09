// Rücklagen und „Wie lange reicht das Polster?“ (ENTW-03, D-14). Alle Werte kommen aus
// `haushalt.eigenkapital` (Vorbericht S. 311) und `haushalt.meta.vorbericht_werte` (S. 23); die Jahre
// stehen nie im Quelltext. Fehlt ein Schlüssel in den Daten, wirft die Funktion mit dem Namen des
// Schlüssels statt still auf 0 zu fallen.
//
// Lesart der Spalten (Vorbericht S. 311, Research Pattern 3): Die Rücklagenzeilen sind der Bestand zu
// JAHRESBEGINN, `jahresergebnis` ist das Ergebnis des Jahres derselben Spalte, die gedruckte Summe
// ist das Eigenkapital am Jahresende. Je Spalte gilt: allgemeine Rücklage + Verrechnung +
// Ausgleichsrücklage + Jahresergebnis = Summe.
//
// Rückgang (Vorbericht S. 23 „Entwicklung aus Sicht des Haushaltes“, S. 24): Der Abbau der
// allgemeinen Rücklage im Jahr t ist das Defizit des Jahres, soweit die Ausgleichsrücklage es nicht
// deckt, zuzüglich der Verrechnung der Bilanzierungshilfe (im Druck negativ gebucht). Er gehört zu
// dem Jahr, dessen Spalte ihn berechnet, und wird auf den Bestand zu Jahresbeginn bezogen. Die
// Regel ist dieselbe wie `_allgemeine_ruecklage_abbau` in `pipeline/ostbevern/texte.py`.
// `rueckgangFormelText()` beschreibt diese Regel für die Fußnote auf /entwicklung aus denselben Konstanten.
//
// Hörstel (`haushalt.eigenkapital_stand` = "jahresende_vor_verrechnung", S. 588): Die Spalten sind
// der Stand zum 31.12. vor Verrechnung des Jahresergebnisses derselben Spalte; die Rücklagen sind
// also ebenfalls der Bestand, auf den das Jahresergebnis noch trifft. Abbau und Rückgang rechnen
// deshalb gleich. Eine Zeile zur Bilanzierungshilfe gibt es dort nicht (Verrechnung 0), und der
// Vorbericht druckt keine Schwellen der Haushaltssicherung (`hskSchwellen()` ist dann `null`).

import { haushalt } from '@/data/daten'
import type { Meta, VorberichtTabelle } from '@/data/typen'

/** Posten-Schlüssel der Eigenkapitalübersicht (S. 311). */
const ALLGEMEINE = 'allgemeine_ruecklage'
const AUSGLEICH = 'ausgleichsruecklage'
const VERRECHNUNG = 'verrechnung_bilanzierungshilfe'
const ERGEBNIS = 'jahresergebnis'

/** Stände der Eigenkapitalspalten, wie `[layout.eigenkapital].stand` sie nennt. */
export const STAND_JAHRESBEGINN = 'jahresbeginn'
export const STAND_VOR_VERRECHNUNG = 'jahresende_vor_verrechnung'

/**
 * Wie die Rücklagenspalten zu lesen sind, für Spaltenköpfe und Beschreibungen: „Bestand zu
 * Jahresbeginn“ (Ostbevern) oder „Bestand vor Verrechnung des Jahresergebnisses“ (Hörstel).
 */
export function bestandText(stand: string = haushalt.eigenkapital_stand): string {
  if (stand === STAND_JAHRESBEGINN) {
    return 'Bestand zu Jahresbeginn'
  }
  if (stand === STAND_VOR_VERRECHNUNG) {
    return 'Bestand vor Verrechnung des Jahresergebnisses'
  }
  throw new Error(`haushalt.eigenkapital_stand „${stand}“ ist unbekannt`)
}

/** Schlüssel der Schwellen in `meta.vorbericht_werte` (S. 23, § 76 GO NRW laut Vorbericht). */
const SCHWELLE_EIN_JAHR = 'hsk_schwelle_ein_jahr'
const SCHWELLE_ZWEI_JAHRE = 'hsk_schwelle_zwei_jahre'

/** Eine Spalte der Eigenkapitalübersicht: die beiden gestapelten Rücklagen. */
export interface Ruecklagenzeile {
  jahr: number
  /** `ergebnis`, `ansatz` oder `planung` (aus `haushalt.wertarten`). */
  wertart: string
  /** Allgemeine Rücklage, Bestand zu Jahresbeginn; `null` ohne Wert (nie 0). */
  allgemeine: number | null
  /** Ausgleichsrücklage, Bestand zu Jahresbeginn; `null` ohne Wert, eine echte 0 bleibt 0. */
  ausgleich: number | null
  /** Summe der beiden Rücklagen (Wert über der Säule); `null`, wenn eine der beiden Rücklagen fehlt; nie eine Teilsumme (WR-04). */
  summe: number | null
}

/** Werte eines Postens je Jahr; ein fehlender Posten ist ein Datenfehler und nennt seinen Schlüssel. */
function postenWerte(tabelle: VorberichtTabelle, schluessel: string): readonly (number | null)[] {
  const eintrag = tabelle.posten.find((kandidat) => kandidat.posten === schluessel)
  if (eintrag === undefined) {
    throw new Error(`eigenkapital.posten.${schluessel} fehlt in haushalt.json`)
  }
  return eintrag.werte
}

function wertAn(tabelle: VorberichtTabelle, schluessel: string, index: number): number | null {
  return postenWerte(tabelle, schluessel)[index] ?? null
}

function hatPosten(tabelle: VorberichtTabelle, schluessel: string): boolean {
  return tabelle.posten.some((kandidat) => kandidat.posten === schluessel)
}

/** Die Verrechnung der Bilanzierungshilfe; ohne diese Zeile in der Übersicht (Hörstel) 0. */
function verrechnungAn(tabelle: VorberichtTabelle, index: number): number | null {
  return hatPosten(tabelle, VERRECHNUNG) ? wertAn(tabelle, VERRECHNUNG, index) : 0
}

function pruefeIndex(index: number): void {
  if (!Number.isInteger(index) || index < 0 || index >= haushalt.jahre.length) {
    throw new Error(`Index ${String(index)} liegt außerhalb von haushalt.jahre`)
  }
}

/** Wertart je Jahr aus `haushalt.wertarten`; ein fehlender Eintrag ist ein Datenfehler. */
function wertartAn(index: number): string {
  const wertart = haushalt.wertarten[index]
  if (wertart === undefined) {
    throw new Error(`haushalt.wertarten hat keinen Eintrag für den Jahresindex ${String(index)}`)
  }
  return wertart
}

/** Eine Zeile je Jahr aus `haushalt.jahre` mit beiden Rücklagen und ihrer Summe (S. 311). */
export function baueRuecklagen(
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
): Ruecklagenzeile[] {
  return haushalt.jahre.map((jahr, index) => {
    const allgemeine = wertAn(tabelle, ALLGEMEINE, index)
    const ausgleich = wertAn(tabelle, AUSGLEICH, index)
    return {
      jahr,
      wertart: wertartAn(index),
      allgemeine,
      ausgleich,
      summe: allgemeine === null || ausgleich === null ? null : allgemeine + ausgleich,
    }
  })
}

/**
 * Abbau der allgemeinen Rücklage im Jahr `index` in Euro (S. 23): das Defizit des Jahres, soweit die
 * Ausgleichsrücklage es nicht deckt, plus die Verrechnung der Bilanzierungshilfe. `null`, wenn ein
 * Eingangswert fehlt.
 */
export function abbau(
  index: number,
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
): number | null {
  pruefeIndex(index)
  const ausgleich = wertAn(tabelle, AUSGLEICH, index)
  const verrechnung = verrechnungAn(tabelle, index)
  const ergebnis = wertAn(tabelle, ERGEBNIS, index)
  if (ausgleich === null || verrechnung === null || ergebnis === null) {
    return null
  }
  // Die Verrechnung steht im Druck negativ; ihr Abzug erhöht den Abbau.
  return Math.max(0, -ergebnis - ausgleich) - verrechnung
}

/**
 * Anteil (0–1), um den die allgemeine Rücklage im Jahr `index` sinkt, bezogen auf ihren Bestand zu
 * Jahresbeginn (S. 23). `null`, wenn ein Eingangswert fehlt oder der Bestand 0 ist (nie NaN, nie ∞).
 */
export function rueckgang(
  index: number,
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
): number | null {
  const bestand = wertAn(tabelle, ALLGEMEINE, index)
  const verlust = abbau(index, tabelle)
  if (bestand === null || bestand === 0 || verlust === null) {
    return null
  }
  return verlust / bestand
}

/** Gedruckter Name eines Postens; ein fehlender Posten ist ein Datenfehler und nennt seinen Schlüssel. */
function postenName(tabelle: VorberichtTabelle, schluessel: string): string {
  const eintrag = tabelle.posten.find((kandidat) => kandidat.posten === schluessel)
  if (eintrag === undefined) {
    throw new Error(`eigenkapital.posten.${schluessel} fehlt in haushalt.json`)
  }
  return eintrag.name
}

/** Wahr, wenn mindestens ein Jahr eine Verrechnung der Bilanzierungshilfe ungleich 0 trägt. */
function hatVerrechnung(tabelle: VorberichtTabelle): boolean {
  if (!hatPosten(tabelle, VERRECHNUNG)) {
    return false
  }
  return postenWerte(tabelle, VERRECHNUNG).some((wert) => wert !== null && wert !== 0)
}

/**
 * Die Beschreibung von `abbau()` und `rueckgang()` für die Fußnote der Rücklagentabelle (CR-01, S. 23,
 * S. 311): ein Satzteil ohne Zahlen, der jeden Term der Formel nennt. Er entsteht neben der Formel
 * aus denselben Posten-Konstanten, damit Text und Rechnung nicht auseinanderlaufen. Die Verrechnung
 * erscheint genau dann, wenn die Daten sie in mindestens einem Jahr ungleich 0 führen, und mit dem
 * gedruckten Postennamen der Eigenkapitalübersicht.
 */
export function rueckgangFormelText(
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
  stand: string = haushalt.eigenkapital_stand,
): string {
  const verrechnung = hatVerrechnung(tabelle)
    ? `, zuzüglich der Verrechnung aus der Zeile „${postenName(tabelle, VERRECHNUNG)}“`
    : ''
  const bezug =
    stand === STAND_JAHRESBEGINN
      ? 'die allgemeine Rücklage zu Jahresbeginn'
      : 'die allgemeine Rücklage vor Verrechnung des Jahresergebnisses'
  return `der Fehlbetrag des Jahres, soweit die Ausgleichsrücklage ihn nicht deckt${verrechnung}, geteilt durch ${bezug}.`
}

export interface HskSchwellen {
  /** Rückgang der allgemeinen Rücklage in einem Jahr (Anteil 0–1). */
  einJahr: number
  /** Rückgang in zwei aufeinanderfolgenden Jahren (Anteil 0–1). */
  zweiJahre: number
  /** 1-basierte PDF-Seite, auf der der Vorbericht die Schwellen nennt. */
  pdfSeite: number
}

function schwelle(meta: Meta, schluessel: string): { anteil: number; seite: number } {
  const eintrag = meta.vorbericht_werte[schluessel]
  if (eintrag === undefined) {
    throw new Error(`meta.vorbericht_werte.${schluessel} fehlt in haushalt.json`)
  }
  if (typeof eintrag.wert !== 'number' || !Number.isFinite(eintrag.wert)) {
    throw new Error(`meta.vorbericht_werte.${schluessel}.wert ist keine Zahl`)
  }
  return { anteil: eintrag.wert / 100, seite: eintrag.quelle }
}

/**
 * Die beiden Schwellen der Haushaltssicherung, wie der Vorbericht sie nennt (S. 23, ganze
 * Prozentpunkte in den Daten, hier als Anteil). Die App gibt sie nur wieder und bewertet nichts.
 * Nennt der Vorbericht keine Schwellen (Hörstel), fehlen beide und das Ergebnis ist `null`; fehlt
 * nur eine, ist das ein Datenfehler.
 */
export function hskSchwellen(meta: Meta = haushalt.meta): HskSchwellen | null {
  const werte = meta.vorbericht_werte
  if (werte[SCHWELLE_EIN_JAHR] === undefined && werte[SCHWELLE_ZWEI_JAHRE] === undefined) {
    return null
  }
  const ein = schwelle(meta, SCHWELLE_EIN_JAHR)
  const zwei = schwelle(meta, SCHWELLE_ZWEI_JAHRE)
  if (ein.seite !== zwei.seite) {
    throw new Error('meta.vorbericht_werte: die beiden Schwellen nennen verschiedene Quellseiten')
  }
  return { einJahr: ein.anteil, zweiJahre: zwei.anteil, pdfSeite: zwei.seite }
}

/**
 * Das Jahr, an dessen Ende die Ausgleichsrücklage aufgebraucht ist: die erste Spalte nach dem
 * Haushaltsjahr mit Ausgleichsrücklage 0 ist der Stand zu Beginn jenes Jahres, aufgebraucht ist sie
 * also am Ende des Jahres davor (S. 311). Dieselbe Regel wie `_ausgleichsruecklage_aufgebraucht_jahr`
 * in `pipeline/ostbevern/texte.py`. `null`, wenn keine Spalte den Stand 0 hat; eine fehlende Spalte
 * zählt nicht als 0.
 */
export function ausgleichsruecklageAufgebrauchtJahr(
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
  stand: string = haushalt.eigenkapital_stand,
): number | null {
  const start = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  const ausgleich = postenWerte(tabelle, AUSGLEICH)
  if (stand === STAND_VOR_VERRECHNUNG) {
    // Stand vor Verrechnung: aufgebraucht im ersten Jahr ab dem Haushaltsjahr, dessen Fehlbetrag
    // die Ausgleichsrücklage der Spalte erreicht (wie `_vor_verrechnung` in texte.py).
    const ergebnis = postenWerte(tabelle, ERGEBNIS)
    for (let index = start; index < haushalt.jahre.length; index += 1) {
      const rest = ausgleich[index] ?? null
      const jahresergebnis = ergebnis[index] ?? null
      if (rest === null || jahresergebnis === null) {
        continue
      }
      if (rest + jahresergebnis <= 0) {
        return haushalt.jahre[index] ?? null
      }
    }
    return null
  }
  for (let index = start + 1; index < haushalt.jahre.length; index += 1) {
    if (ausgleich[index] === 0) {
      const jahr = haushalt.jahre[index]
      return jahr === undefined ? null : jahr - 1
    }
  }
  return null
}

/** Ein Planjahr des Rückgang-Diagramms (S. 23): ab dem Haushaltsjahr, je Jahr der eigenen Spalte. */
export interface Rueckgangsjahr {
  jahr: number
  /** `ergebnis`, `ansatz` oder `planung` (aus `haushalt.wertarten`). */
  wertart: string
  /** Rückgang der allgemeinen Rücklage als Anteil (0–1); `null`, wenn ein Eingangswert fehlt. */
  anteil: number | null
}

/** Index des Haushaltsjahres in `haushalt.jahre`; fehlt es, ist das ein Datenfehler. */
function haushaltsjahrIndex(): number {
  const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  if (index < 0) {
    throw new Error('haushalt.haushaltsjahr steht nicht in haushalt.jahre')
  }
  return index
}

/**
 * Der Rückgang je Planjahr: ein Eintrag für jedes Jahr vom Haushaltsjahr an (wie S. 23). Die Jahre
 * davor tragen keinen Abbau und erscheinen nicht, ebenso keine Jahre nach dem letzten Planjahr.
 */
export function rueckgangPlanjahre(
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
): Rueckgangsjahr[] {
  const start = haushaltsjahrIndex()
  return haushalt.jahre.slice(start).map((jahr, versatz) => ({
    jahr,
    wertart: wertartAn(start + versatz),
    anteil: rueckgang(start + versatz, tabelle),
  }))
}

/** Luft über dem höchsten Wert der Rückgang-Achse (UI-SPEC: y-Achse bis max × 1,2). */
const ACHSEN_FAKTOR = 1.2

/**
 * Obergrenze der y-Achse des Rückgang-Diagramms: das 1,2-Fache des größeren aus allen Werten und der
 * Schwelle, damit Schwellenlinie und ihre Beschriftung innerhalb des Diagramms bleiben.
 */
export function rueckgangAchsenMaximum(anteile: readonly number[], schwelle: number): number {
  return Math.max(...anteile, schwelle) * ACHSEN_FAKTOR
}

/** Eine Zeile der Rücklagentabelle: beide Bestände zu Jahresbeginn und der Rückgang im Jahr. */
export interface Ruecklagentabellenzeile {
  jahr: number
  wertart: string
  allgemeine: number | null
  ausgleich: number | null
  /** Rückgang der allgemeinen Rücklage im Jahr (Anteil 0–1, berechnet); `null` vor dem Haushaltsjahr. */
  rueckgang: number | null
}

/**
 * Eine Zeile je Jahr aus `haushalt.jahre`. Der Rückgang gehört zu dem Jahr der eigenen Spalte und
 * steht erst ab dem Haushaltsjahr (davor `null`), nie als Differenz zur Vorspalte.
 */
export function ruecklagenTabelle(
  tabelle: VorberichtTabelle = haushalt.eigenkapital,
): Ruecklagentabellenzeile[] {
  const start = haushaltsjahrIndex()
  return baueRuecklagen(tabelle).map((zeile, index) => ({
    jahr: zeile.jahr,
    wertart: zeile.wertart,
    allgemeine: zeile.allgemeine,
    ausgleich: zeile.ausgleich,
    rueckgang: index < start ? null : rueckgang(index, tabelle),
  }))
}
