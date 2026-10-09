import { describe, expect, it } from 'vitest'

import { haushalt, texte } from '@/data/daten'
import type { Meta, VorberichtPosten, VorberichtTabelle } from '@/data/typen'
import {
  STAND_JAHRESBEGINN,
  STAND_VOR_VERRECHNUNG,
  abbau,
  ausgleichsruecklageAufgebrauchtJahr,
  baueRuecklagen,
  bestandText,
  hskSchwellen,
  rueckgang,
  rueckgangAchsenMaximum,
  rueckgangFormelText,
  rueckgangPlanjahre,
  ruecklagenTabelle,
} from '@/lib/ruecklagen'

// Der Quelltext der Seite (wie in `menue.test.ts` über `?raw`): die Formelprosa der Fußnote darf nur
// in `ruecklagen.ts` stehen, die Seite ruft `rueckgangFormelText()` auf.
const seitenQuelltexte = import.meta.glob<string>('/src/pages/EntwicklungPage.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})
const seitenQuelltext = seitenQuelltexte['/src/pages/EntwicklungPage.vue'] ?? ''

const EIGENKAPITAL = haushalt.eigenkapital
const LETZTER_INDEX = haushalt.jahre.length - 1
const START_INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
const VERRECHNUNG = 'verrechnung_bilanzierungshilfe'

function postenAus(tabelle: VorberichtTabelle, schluessel: string): (number | null)[] {
  const eintrag = tabelle.posten.find((kandidat) => kandidat.posten === schluessel)
  if (eintrag === undefined) {
    throw new Error(`Posten ${schluessel} fehlt in den Testdaten`)
  }
  return eintrag.werte
}

function posten(schluessel: string): (number | null)[] {
  return postenAus(EIGENKAPITAL, schluessel)
}

/** Eine Kopie der Tabelle mit einem veränderten Posten, für Randfälle. */
function mitPosten(
  schluessel: string,
  werte: (number | null)[],
  basis: VorberichtTabelle = EIGENKAPITAL,
): VorberichtTabelle {
  return {
    ...basis,
    posten: basis.posten.map((eintrag) =>
      eintrag.posten === schluessel ? { ...eintrag, werte } : eintrag,
    ),
  }
}

function eintrag(schluessel: string, name: string, werte: (number | null)[]): VorberichtPosten {
  return {
    posten: schluessel,
    name,
    werte,
    gerundet: true,
    berechnet: false,
    quelle: 311,
    anmerkung: null,
  }
}

/** Eine Kopie der Tabelle mit zusätzlicher Zeile der Bilanzierungshilfe (Ostbevern-Muster). */
function mitVerrechnung(
  werte: (number | null)[],
  basis: VorberichtTabelle = EIGENKAPITAL,
): VorberichtTabelle {
  return {
    ...basis,
    posten: [
      ...basis.posten.filter((kandidat) => kandidat.posten !== VERRECHNUNG),
      eintrag(VERRECHNUNG, 'Einmalige Verrechnung Bilanzierungshilfe', werte),
    ],
  }
}

/**
 * Die Eigenkapitalübersicht des Ostbeverner Haushalts 2026 (Vorbericht S. 311, Stand zu
 * Jahresbeginn), als synthetische Tabelle für die Logik, die Hörstel nicht nutzt: Verrechnung der
 * Bilanzierungshilfe und Ausgleichsrücklage 0 in einer späteren Spalte.
 */
const OSTBEVERN: VorberichtTabelle = {
  ...EIGENKAPITAL,
  gesamt_vorbericht: {
    werte: [41655204, 41655204, 38825371, 37182843, 35424016, 31866316],
    gerundet: true,
    quelle: 311,
  },
  posten: [
    eintrag(
      'allgemeine_ruecklage',
      'Allgemeine Rücklage',
      [39522991, 39522991, 39522991, 38825371, 37182843, 35424016],
    ),
    eintrag(VERRECHNUNG, 'Einmalige Verrechnung Bilanzierungshilfe', [0, 0, -476327, 0, 0, 0]),
    eintrag('ausgleichsruecklage', 'Ausgleichsrücklage', [1940223, 2132213, 2132213, 0, 0, 0]),
    eintrag(
      'jahresergebnis',
      'Jahresergebnis',
      [191990, 0, -2353506, -1642528, -1758827, -3557700],
    ),
  ],
}
const OSTBEVERN_JAHRE = 6
const OSTBEVERN_START = 2

describe('Testdaten', () => {
  it('die synthetische Ostbevern-Tabelle passt auf die Jahre der Haushaltsdaten', () => {
    expect(haushalt.jahre).toHaveLength(OSTBEVERN_JAHRE)
    expect(START_INDEX).toBe(OSTBEVERN_START)
  })
})

describe('bestandText', () => {
  it('liest die Spalten je nach Stand der Eigenkapitalübersicht', () => {
    expect(bestandText(STAND_JAHRESBEGINN)).toBe('Bestand zu Jahresbeginn')
    expect(bestandText(STAND_VOR_VERRECHNUNG)).toBe('Bestand vor Verrechnung des Jahresergebnisses')
  })

  it('nutzt ohne Argument den Stand der Haushaltsdaten', () => {
    expect(bestandText()).toBe(bestandText(haushalt.eigenkapital_stand))
  })

  it('wirft bei einem unbekannten Stand und nennt ihn', () => {
    expect(() => bestandText('jahresmitte')).toThrow(/jahresmitte/)
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Hörstel führt den Stand zum 31.12. vor Ergebnisverrechnung (S. 588, Fußnote 1)', () => {
      expect(haushalt.eigenkapital_stand).toBe(STAND_VOR_VERRECHNUNG)
      expect(bestandText()).toBe('Bestand vor Verrechnung des Jahresergebnisses')
    })
  })
})

describe('baueRuecklagen (ENTW-03, Eigenkapitalübersicht)', () => {
  const zeilen = baueRuecklagen()

  it('liefert je Jahr aus haushalt.jahre genau eine Zeile mit der Wertart aus den Daten', () => {
    expect(zeilen.map((zeile) => zeile.jahr)).toEqual(haushalt.jahre)
    expect(zeilen.map((zeile) => zeile.wertart)).toEqual(haushalt.wertarten)
  })

  it('übernimmt allgemeine Rücklage und Ausgleichsrücklage unverändert aus eigenkapital.posten', () => {
    expect(zeilen.map((zeile) => zeile.allgemeine)).toEqual(posten('allgemeine_ruecklage'))
    expect(zeilen.map((zeile) => zeile.ausgleich)).toEqual(posten('ausgleichsruecklage'))
  })

  it('summiert die beiden Rücklagen je Spalte zum Wert über der Säule', () => {
    for (const zeile of zeilen) {
      expect(zeile.allgemeine).not.toBeNull()
      expect(zeile.ausgleich).not.toBeNull()
      expect(zeile.summe).toBe((zeile.allgemeine as number) + (zeile.ausgleich as number))
    }
  })

  it('lässt einen fehlenden Wert null und eine echte 0 eine 0 bleiben', () => {
    const tabelle = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map((_jahr, index) => (index === 0 ? null : 0)),
    )
    const geprueft = baueRuecklagen(tabelle)
    expect(geprueft[0]?.ausgleich).toBeNull()
    expect(geprueft[0]?.summe).toBeNull()
    expect(geprueft[1]?.ausgleich).toBe(0)
    expect(geprueft[1]?.summe).toBe(geprueft[1]?.allgemeine)
  })

  it('zeigt ohne eine der beiden Rücklagen keine Teilsumme als Summe (WR-04)', () => {
    const allgemeine = posten('allgemeine_ruecklage')
    const tabelle = mitPosten(
      'allgemeine_ruecklage',
      allgemeine.map((wert, index) => (index === 0 ? null : wert)),
    )
    const geprueft = baueRuecklagen(tabelle)
    expect(geprueft[0]?.allgemeine).toBeNull()
    expect(geprueft[0]?.summe).toBeNull()
    geprueft.slice(1).forEach((zeile, versatz) => {
      expect(zeile.summe).toBe((allgemeine[versatz + 1] ?? Number.NaN) + (zeile.ausgleich ?? 0))
    })
  })

  it('hat ohne beide Werte keine Summe', () => {
    const ohneAusgleich = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map(() => null),
    )
    const ohneBeide = mitPosten(
      'allgemeine_ruecklage',
      haushalt.jahre.map(() => null),
      ohneAusgleich,
    )
    expect(baueRuecklagen(ohneBeide).every((zeile) => zeile.summe === null)).toBe(true)
  })

  it('nennt einen fehlenden Posten beim Namen', () => {
    const ohne: VorberichtTabelle = {
      ...EIGENKAPITAL,
      posten: EIGENKAPITAL.posten.filter((kandidat) => kandidat.posten !== 'ausgleichsruecklage'),
    }
    expect(() => baueRuecklagen(ohne)).toThrow(/ausgleichsruecklage/)
  })

  it('erfüllt die Arithmetik der Übersicht je Spalte: Σ der Posten = gedruckte Summe (±1 € Cent-Rundung)', () => {
    for (const tabelle of [EIGENKAPITAL, OSTBEVERN]) {
      const summen = tabelle.gesamt_vorbericht.werte
      haushalt.jahre.forEach((_jahr, index) => {
        const gesamt = tabelle.posten.reduce(
          (summe, kandidat) => summe + (kandidat.werte[index] ?? 0),
          0,
        )
        expect(Math.abs(gesamt - (summen[index] ?? Number.NaN))).toBeLessThanOrEqual(1)
      })
    }
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026 (S. 588)', () => {
    it('Hörstel führt keine Zeile zur Bilanzierungshilfe', () => {
      expect(EIGENKAPITAL.posten.map((kandidat) => kandidat.posten)).not.toContain(VERRECHNUNG)
      expect(EIGENKAPITAL.gesamt_vorbericht.quelle).toBe(588)
    })

    it('Rücklagen 2026: allgemeine 50.844.885 €, Ausgleichsrücklage 12.243.578 €', () => {
      const zeile = zeilen[START_INDEX]
      expect(zeile?.allgemeine).toBe(50844885)
      expect(zeile?.ausgleich).toBe(12243578)
      expect(zeile?.summe).toBe(63088463)
    })
  })
})

describe('abbau und rueckgang (ENTW-03)', () => {
  it('Ostbevern (Stand zu Jahresbeginn): der Abbau ist das Gefälle zum Bestand des Folgejahres', () => {
    const allgemeine = postenAus(OSTBEVERN, 'allgemeine_ruecklage')
    for (let index = 0; index < LETZTER_INDEX; index += 1) {
      expect(abbau(index, OSTBEVERN)).toBe((allgemeine[index] ?? 0) - (allgemeine[index + 1] ?? 0))
    }
  })

  it('Planjahre der Daten: der Abbau ist das Gefälle der allgemeinen Rücklage zur Folgespalte', () => {
    const allgemeine = posten('allgemeine_ruecklage')
    for (let index = START_INDEX; index < LETZTER_INDEX; index += 1) {
      const jetzt = allgemeine[index]
      const spaeter = allgemeine[index + 1]
      expect(jetzt).not.toBeNull()
      expect(spaeter).not.toBeNull()
      expect(abbau(index)).toBe((jetzt ?? 0) - (spaeter ?? 0))
    }
  })

  it('ohne Zeile zur Bilanzierungshilfe rechnet der Abbau mit Verrechnung 0', () => {
    const nullzeile = mitVerrechnung(haushalt.jahre.map(() => 0))
    for (let index = 0; index <= LETZTER_INDEX; index += 1) {
      expect(abbau(index)).toBe(abbau(index, nullzeile))
    }
  })

  it('zieht eine (im Druck negative) Verrechnung vom Abbau ab, erhöht ihn also', () => {
    const tabelle = mitVerrechnung(haushalt.jahre.map((_jahr, index) => (index === 0 ? -5 : 0)))
    expect(abbau(0, tabelle)).toBe((abbau(0) ?? Number.NaN) + 5)
  })

  it('hat ohne Verrechnungswert keinen Abbau', () => {
    const tabelle = mitVerrechnung(haushalt.jahre.map(() => null))
    expect(abbau(START_INDEX, tabelle)).toBeNull()
  })

  it('teilt den Abbau durch den Bestand der eigenen Spalte', () => {
    const allgemeine = posten('allgemeine_ruecklage')
    for (let index = 0; index <= LETZTER_INDEX; index += 1) {
      expect(rueckgang(index)).toBeCloseTo((abbau(index) ?? 0) / (allgemeine[index] ?? 1), 12)
    }
  })

  it('gehört zu dem Jahr, dessen Spalte es berechnet (kein Versatz um ein Jahr, Pitfall 1)', () => {
    // Ostbevern: Die Spalte des Haushaltsjahres trägt den ersten echten Rückgang; die Spalte davor keinen.
    expect(rueckgang(START_INDEX - 1, OSTBEVERN)).toBe(0)
    expect(rueckgang(START_INDEX, OSTBEVERN) ?? 0).toBeGreaterThan(0)
    // Das letzte Planjahr ist nicht ausgelassen.
    expect(rueckgang(LETZTER_INDEX, OSTBEVERN) ?? 0).toBeGreaterThan(0)
    expect(rueckgang(LETZTER_INDEX) ?? 0).toBeGreaterThan(0)
  })

  it('hat ohne Bestand oder ohne Eingangswert keinen Rückgang statt NaN', () => {
    const ohneBestand = mitPosten(
      'allgemeine_ruecklage',
      haushalt.jahre.map(() => 0),
    )
    expect(rueckgang(START_INDEX, ohneBestand)).toBeNull()
    const ohneErgebnis = mitPosten(
      'jahresergebnis',
      haushalt.jahre.map(() => null),
    )
    expect(rueckgang(START_INDEX, ohneErgebnis)).toBeNull()
  })

  it('wirft für einen Index außerhalb der Jahre', () => {
    expect(() => rueckgang(haushalt.jahre.length)).toThrow(/Index/)
    expect(() => rueckgang(-1)).toThrow(/Index/)
  })

  it('Ostbevern: reproduziert die gedruckten 1,77 / 4,23 / 4,73 / 10,04 % (S. 23)', () => {
    const geprueft = haushalt.jahre
      .slice(START_INDEX)
      .map(
        (_jahr, versatz) =>
          Math.round((rueckgang(START_INDEX + versatz, OSTBEVERN) ?? Number.NaN) * 10000) / 100,
      )
    expect(geprueft).toEqual([1.77, 4.23, 4.73, 10.04])
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026 (S. 588)', () => {
    it('die Ausgleichsrücklage deckt die Fehlbeträge 2026 bis 2028, erst 2029 sinkt die allgemeine Rücklage', () => {
      const geprueft = haushalt.jahre
        .slice(START_INDEX)
        .map(
          (_jahr, versatz) =>
            Math.round((rueckgang(START_INDEX + versatz) ?? Number.NaN) * 10000) / 100,
        )
      expect(geprueft).toEqual([0, 0, 0, 1.33])
    })

    it('Abbau 2029: Fehlbetrag 5.014.196 € abzüglich Ausgleichsrücklage 4.339.938 € = 674.258 €', () => {
      expect(abbau(LETZTER_INDEX)).toBe(5014196 - 4339938)
    })

    it('stimmt mit der allgemeinen Rücklage Ende des letzten Planjahrs aus texte.werte überein', () => {
      const wert = texte.werte['abgeleitet.allgemeine_ruecklage_ende_letztes_jahr_vor_verrechnung']
      expect(wert).toBe(50170627)
      expect(
        (posten('allgemeine_ruecklage')[LETZTER_INDEX] ?? 0) - (abbau(LETZTER_INDEX) ?? 0),
      ).toBe(wert)
    })
  })
})

describe('rueckgangFormelText (CR-01)', () => {
  const datenHabenVerrechnung = EIGENKAPITAL.posten.some(
    (kandidat) =>
      kandidat.posten === VERRECHNUNG && kandidat.werte.some((wert) => wert !== null && wert !== 0),
  )

  const ohneVerrechnung = mitVerrechnung(haushalt.jahre.map(() => 0))
  const verrechnungNull = mitVerrechnung(haushalt.jahre.map(() => null))
  const nurErsteSpalte = mitVerrechnung(
    haushalt.jahre.map((_jahr, index) => (index === 0 ? -5 : 0)),
  )

  /**
   * Rückgang, nachgerechnet allein aus den Termen, die der Text nennt: das Defizit, soweit die
   * Ausgleichsrücklage es nicht deckt, plus (nur wenn der Text sie nennt) die Verrechnung, geteilt durch
   * die allgemeine Rücklage der Spalte.
   */
  function nachgerechnet(tabelle: VorberichtTabelle, text: string, index: number): number {
    const wert = (schluessel: string): number => {
      const kandidat = tabelle.posten.find((p) => p.posten === schluessel)
      const einzel = kandidat?.werte[index]
      if (einzel === null || einzel === undefined) {
        throw new Error(`Testdaten: ${schluessel} ohne Wert an Index ${String(index)}`)
      }
      return einzel
    }
    const nenntVerrechnung = text.includes('Verrechnung aus der Zeile')
    const abbauWert =
      Math.max(0, -wert('jahresergebnis') - wert('ausgleichsruecklage')) -
      (nenntVerrechnung ? wert(VERRECHNUNG) : 0)
    return abbauWert / wert('allgemeine_ruecklage')
  }

  it('nennt die Verrechnung samt Postenname aus den Daten genau dann, wenn ein Jahr sie ungleich 0 hat', () => {
    expect(rueckgangFormelText().includes('Verrechnung aus der Zeile')).toBe(datenHabenVerrechnung)
    expect(rueckgangFormelText(OSTBEVERN)).toContain(
      'Verrechnung aus der Zeile „Einmalige Verrechnung Bilanzierungshilfe“',
    )
  })

  it('bezieht sich je nach Stand auf die allgemeine Rücklage zu Jahresbeginn oder vor Verrechnung', () => {
    expect(rueckgangFormelText(OSTBEVERN, STAND_JAHRESBEGINN)).toContain(
      'geteilt durch die allgemeine Rücklage zu Jahresbeginn.',
    )
    expect(rueckgangFormelText(EIGENKAPITAL, STAND_VOR_VERRECHNUNG)).toContain(
      'geteilt durch die allgemeine Rücklage vor Verrechnung des Jahresergebnisses.',
    )
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Hörstel: ohne Bilanzierungshilfe keine Verrechnung, Bezug vor Verrechnung des Jahresergebnisses', () => {
      expect(datenHabenVerrechnung).toBe(false)
      expect(rueckgangFormelText()).toBe(
        'der Fehlbetrag des Jahres, soweit die Ausgleichsrücklage ihn nicht deckt, geteilt durch die allgemeine Rücklage vor Verrechnung des Jahresergebnisses.',
      )
    })
  })

  it('Ostbevern: ergäbe ohne den Verrechnungs-Term 0,56 % statt der gezeigten 1,77 % (Regressionsschutz CR-01)', () => {
    const ohneTerm = nachgerechnet(OSTBEVERN, '', START_INDEX)
    const gezeigt = Math.round((rueckgang(START_INDEX, OSTBEVERN) ?? Number.NaN) * 10000) / 100
    expect(Math.round(ohneTerm * 10000) / 100).toBe(0.56)
    expect(gezeigt).toBe(1.77)
  })

  it('nennt die Verrechnung nicht, wenn alle Werte 0 sind', () => {
    expect(rueckgangFormelText(ohneVerrechnung)).not.toContain('Verrechnung aus der Zeile')
  })

  it('nennt die Verrechnung nicht, wenn alle Werte fehlen', () => {
    expect(rueckgangFormelText(verrechnungNull)).not.toContain('Verrechnung aus der Zeile')
  })

  it('nennt die Verrechnung auch, wenn nur eine Spalte vor dem Haushaltsjahr sie hat', () => {
    expect(rueckgangFormelText(nurErsteSpalte)).toContain('Verrechnung aus der Zeile')
  })

  it('rechnet jedes Planjahr aus den im Text genannten Termen auf rueckgang() zurück', () => {
    for (const tabelle of [EIGENKAPITAL, OSTBEVERN, ohneVerrechnung]) {
      const text = rueckgangFormelText(tabelle)
      for (let index = START_INDEX; index <= LETZTER_INDEX; index += 1) {
        expect(nachgerechnet(tabelle, text, index)).toBeCloseTo(
          rueckgang(index, tabelle) ?? Number.NaN,
          12,
        )
      }
    }
  })

  it('enthält keine Ziffer und endet mit einem Punkt', () => {
    for (const tabelle of [
      EIGENKAPITAL,
      OSTBEVERN,
      ohneVerrechnung,
      verrechnungNull,
      nurErsteSpalte,
    ]) {
      for (const stand of [STAND_JAHRESBEGINN, STAND_VOR_VERRECHNUNG]) {
        const text = rueckgangFormelText(tabelle, stand)
        expect(text).not.toMatch(/\d/)
        expect(text.endsWith('.')).toBe(true)
      }
    }
  })

  it('kommt ohne den Posten der Bilanzierungshilfe aus und nennt dann keine Verrechnung', () => {
    const ohne: VorberichtTabelle = {
      ...OSTBEVERN,
      posten: OSTBEVERN.posten.filter((kandidat) => kandidat.posten !== VERRECHNUNG),
    }
    expect(rueckgangFormelText(ohne)).not.toContain('Verrechnung aus der Zeile')
  })

  it('wird von EntwicklungPage.vue aufgerufen, die Formelprosa steht nicht in der Seite', () => {
    expect(seitenQuelltext).toContain('rueckgangFormelText(')
    expect(seitenQuelltext).not.toContain('soweit die Ausgleichsrücklage')
  })
})

describe('hskSchwellen (ENTW-03, D-14)', () => {
  const meta = (ersatz: Record<string, unknown>): Meta => ({
    ...haushalt.meta,
    vorbericht_werte: { ...haushalt.meta.vorbericht_werte, ...ersatz } as Meta['vorbericht_werte'],
  })
  // Ostbevern, Vorbericht S. 23: § 76 GO NRW, ein Viertel in einem Jahr, ein Zwanzigstel in zwei Jahren.
  const ostbevern = meta({
    hsk_schwelle_ein_jahr: { wert: 25, einheit: 'prozent', quelle: 23 },
    hsk_schwelle_zwei_jahre: { wert: 5, einheit: 'prozent', quelle: 23 },
  })

  it('liest beide Schwellen als Anteil aus meta.vorbericht_werte, mit der Quellseite', () => {
    expect(hskSchwellen(ostbevern)).toEqual({ einJahr: 0.25, zweiJahre: 0.05, pdfSeite: 23 })
  })

  it('ist null, wenn der Vorbericht keine der beiden Schwellen nennt', () => {
    const ohne = { ...haushalt.meta.vorbericht_werte }
    delete ohne['hsk_schwelle_ein_jahr']
    delete ohne['hsk_schwelle_zwei_jahre']
    expect(hskSchwellen({ ...haushalt.meta, vorbericht_werte: ohne })).toBeNull()
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Hörstel druckt keine Schwellen der Haushaltssicherung', () => {
      expect(hskSchwellen()).toBeNull()
    })
  })

  it('wirft, wenn nur ein Schlüssel fehlt, und nennt ihn', () => {
    const ohne = { ...ostbevern.vorbericht_werte }
    delete ohne['hsk_schwelle_zwei_jahre']
    expect(() => hskSchwellen({ ...haushalt.meta, vorbericht_werte: ohne })).toThrow(
      /hsk_schwelle_zwei_jahre/,
    )
  })

  it('wirft, wenn ein Wert keine Zahl ist', () => {
    expect(() =>
      hskSchwellen({
        ...ostbevern,
        vorbericht_werte: {
          ...ostbevern.vorbericht_werte,
          hsk_schwelle_ein_jahr: { wert: 'viel', einheit: 'prozent', quelle: 23 },
        } as Meta['vorbericht_werte'],
      }),
    ).toThrow(/hsk_schwelle_ein_jahr/)
  })

  it('wirft, wenn die beiden Schwellen verschiedene Quellseiten nennen', () => {
    expect(() =>
      hskSchwellen({
        ...ostbevern,
        vorbericht_werte: {
          ...ostbevern.vorbericht_werte,
          hsk_schwelle_ein_jahr: { wert: 25, einheit: 'prozent', quelle: 24 },
        } as Meta['vorbericht_werte'],
      }),
    ).toThrow(/Quellseiten/)
  })
})

describe('ausgleichsruecklageAufgebrauchtJahr (ENTW-03, D-14)', () => {
  describe('Stand zu Jahresbeginn (Ostbevern)', () => {
    it('ist das Jahr vor der ersten Spalte nach dem Haushaltsjahr mit Ausgleichsrücklage 0', () => {
      // Ostbevern S. 311: Spalte 2027 zeigt 0, aufgebraucht also Ende 2026.
      expect(ausgleichsruecklageAufgebrauchtJahr(OSTBEVERN, STAND_JAHRESBEGINN)).toBe(
        haushalt.jahre[START_INDEX],
      )
    })

    it('hat ohne Nullspalte kein Jahr', () => {
      const nieNull = mitPosten(
        'ausgleichsruecklage',
        haushalt.jahre.map(() => 1),
        OSTBEVERN,
      )
      expect(ausgleichsruecklageAufgebrauchtJahr(nieNull, STAND_JAHRESBEGINN)).toBeNull()
    })

    it('überspringt eine fehlende Spalte, statt sie als 0 zu lesen', () => {
      const luecke = mitPosten(
        'ausgleichsruecklage',
        haushalt.jahre.map((_jahr, index) => (index > START_INDEX ? null : 1)),
        OSTBEVERN,
      )
      expect(ausgleichsruecklageAufgebrauchtJahr(luecke, STAND_JAHRESBEGINN)).toBeNull()
    })
  })

  describe('Stand vor Verrechnung (Hörstel)', () => {
    /** Ausgleichsrücklage 10 je Spalte, Jahresergebnis wie angegeben. */
    function tabelleMit(ergebnis: (number | null)[]): VorberichtTabelle {
      return mitPosten(
        'jahresergebnis',
        ergebnis,
        mitPosten(
          'ausgleichsruecklage',
          haushalt.jahre.map(() => 10),
        ),
      )
    }

    it('ist das erste Jahr ab dem Haushaltsjahr, dessen Fehlbetrag die Ausgleichsrücklage erreicht', () => {
      const ergebnis = haushalt.jahre.map((_jahr, index) => (index === START_INDEX + 1 ? -10 : -1))
      expect(ausgleichsruecklageAufgebrauchtJahr(tabelleMit(ergebnis), STAND_VOR_VERRECHNUNG)).toBe(
        haushalt.jahre[START_INDEX + 1],
      )
    })

    it('zählt ein Jahr vor dem Haushaltsjahr nicht mit', () => {
      const ergebnis = haushalt.jahre.map((_jahr, index) => (index < START_INDEX ? -50 : -1))
      expect(
        ausgleichsruecklageAufgebrauchtJahr(tabelleMit(ergebnis), STAND_VOR_VERRECHNUNG),
      ).toBeNull()
    })

    it('überspringt eine Spalte ohne Jahresergebnis, statt sie als 0 zu lesen', () => {
      const ergebnis = haushalt.jahre.map((_jahr, index) =>
        index === START_INDEX ? null : index === LETZTER_INDEX ? -20 : -1,
      )
      expect(ausgleichsruecklageAufgebrauchtJahr(tabelleMit(ergebnis), STAND_VOR_VERRECHNUNG)).toBe(
        haushalt.jahre[LETZTER_INDEX],
      )
    })

    it('hat kein Jahr, solange die Ausgleichsrücklage jeden Fehlbetrag deckt', () => {
      const ergebnis = haushalt.jahre.map(() => -9)
      expect(
        ausgleichsruecklageAufgebrauchtJahr(tabelleMit(ergebnis), STAND_VOR_VERRECHNUNG),
      ).toBeNull()
    })
  })

  it('stimmt mit der Pipeline-Regel (texte.werte) zum Stand der Daten überein', () => {
    const schluessel =
      haushalt.eigenkapital_stand === STAND_VOR_VERRECHNUNG
        ? 'abgeleitet.ausgleichsruecklage_aufgebraucht_jahr_vor_verrechnung'
        : 'abgeleitet.ausgleichsruecklage_aufgebraucht_jahr'
    const wert = texte.werte[schluessel]
    if (wert === undefined) {
      // Der Wert steht nur in texte.json, solange ein Text ihn nutzt.
      expect(ausgleichsruecklageAufgebrauchtJahr()).not.toBeUndefined()
      return
    }
    expect(ausgleichsruecklageAufgebrauchtJahr()).toBe(wert)
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Haushalt 2026', () => {
    it('Hörstel: aufgebraucht 2029 (Vorbericht S. 72; 4.339.938 € gegen Fehlbetrag 5.014.196 €)', () => {
      expect(ausgleichsruecklageAufgebrauchtJahr()).toBe(2029)
    })
  })
})

describe('rueckgangPlanjahre (ENTW-03, A7)', () => {
  it('hat je Jahr ab dem Haushaltsjahr einen Eintrag mit Wertart und Anteil', () => {
    const planjahre = rueckgangPlanjahre()
    expect(planjahre.map((zeile) => zeile.jahr)).toEqual(haushalt.jahre.slice(START_INDEX))
    expect(planjahre.map((zeile) => zeile.wertart)).toEqual(haushalt.wertarten.slice(START_INDEX))
  })

  it('trägt je Eintrag den Rückgang der eigenen Spalte, ohne Versatz um ein Jahr', () => {
    for (const tabelle of [EIGENKAPITAL, OSTBEVERN]) {
      rueckgangPlanjahre(tabelle).forEach((zeile, versatz) => {
        expect(zeile.anteil).toBe(rueckgang(START_INDEX + versatz, tabelle))
      })
    }
  })

  it('führt kein Jahr vor dem Haushaltsjahr', () => {
    expect(rueckgangPlanjahre().some((zeile) => zeile.jahr < haushalt.haushaltsjahr)).toBe(false)
  })

  it('lässt einen fehlenden Eingangswert null und nicht 0', () => {
    const ohneErgebnis = mitPosten(
      'jahresergebnis',
      haushalt.jahre.map(() => null),
    )
    expect(rueckgangPlanjahre(ohneErgebnis).every((zeile) => zeile.anteil === null)).toBe(true)
  })
})

describe('rueckgangAchsenMaximum (UI-SPEC E3 overflow)', () => {
  it('ist das 1,2-Fache des größeren aus Werten und Schwelle', () => {
    expect(rueckgangAchsenMaximum([0.02, 0.1], 0.05)).toBeCloseTo(0.12, 12)
    expect(rueckgangAchsenMaximum([0.01, 0.02], 0.05)).toBeCloseTo(0.06, 12)
  })

  it('hält die Schwelle ohne Werte im Diagramm', () => {
    expect(rueckgangAchsenMaximum([], 0.05)).toBeCloseTo(0.06, 12)
  })

  it('liegt für die Daten über Schwelle und jedem Wert (ohne Schwelle: Schwelle 0)', () => {
    const anteile = rueckgangPlanjahre().flatMap((zeile) =>
      zeile.anteil === null ? [] : [zeile.anteil],
    )
    const schwelle = hskSchwellen()?.zweiJahre ?? 0
    const maximum = rueckgangAchsenMaximum(anteile, schwelle)
    expect(maximum).toBeGreaterThanOrEqual(schwelle)
    expect(maximum).toBeGreaterThan(Math.max(...anteile))
  })
})

describe('ruecklagenTabelle (ENTW-03)', () => {
  it('hat eine Zeile je Jahr mit Wertart, beiden Rücklagen und dem Rückgang', () => {
    const tabelle = ruecklagenTabelle()
    expect(tabelle.map((zeile) => zeile.jahr)).toEqual(haushalt.jahre)
    expect(tabelle.map((zeile) => zeile.wertart)).toEqual(haushalt.wertarten)
    expect(tabelle.map((zeile) => zeile.allgemeine)).toEqual(posten('allgemeine_ruecklage'))
    expect(tabelle.map((zeile) => zeile.ausgleich)).toEqual(posten('ausgleichsruecklage'))
  })

  it('führt den Rückgang erst ab dem Haushaltsjahr, davor null', () => {
    ruecklagenTabelle().forEach((zeile, index) => {
      expect(zeile.rueckgang).toBe(index < START_INDEX ? null : rueckgang(index))
    })
  })

  it('zeigt eine echte 0 der Ausgleichsrücklage als 0 und keinen Wert als null', () => {
    const mitLuecke = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map((_jahr, index) => (index === 0 ? null : 0)),
    )
    const zeilen = ruecklagenTabelle(mitLuecke)
    expect(zeilen[0]?.ausgleich).toBeNull()
    expect(zeilen[1]?.ausgleich).toBe(0)
  })
})
