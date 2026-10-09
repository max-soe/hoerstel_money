import { afterEach, describe, expect, it, vi } from 'vitest'

import { euroKurz } from '@/charts/format'
import { haushalt, produkte } from '@/data/daten'
import type { KnotenWerte, Produkt } from '@/data/typen'
import {
  baueBindungsgrad,
  BINDUNGSGRADE,
  FINANZIERUNGSPRODUKT,
  klAnteil,
  OHNE_ANGABE,
  produkteText,
  segmentZusammenfassung,
  type BindungsgradModell,
  type BindungsSegment,
} from '@/lib/bindungsgrad'
import { bindungsgradText } from '@/lib/produkt'
import { ZEITREIHEN_PRODUKT } from '@/lib/zeitreihen'

const INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

/** Zuschussbedarf eines Produkts im Haushaltsjahr, direkt aus den Daten gelesen. */
function zuschussbedarf(code: string): number {
  const wert = haushalt.ergebnisplan[code]?.berechnet.zuschussbedarf[INDEX]
  if (wert === undefined) {
    throw new Error(`Kein Zuschussbedarf für ${code}`)
  }
  return wert
}

describe('FINANZIERUNGSPRODUKT (D-01)', () => {
  it('ist die eine Konstante aus lib/zeitreihen.ts, kein zweites Literal', () => {
    expect(FINANZIERUNGSPRODUKT).toBe(ZEITREIHEN_PRODUKT)
  })

  it('hat im Haushaltsjahr einen negativen Zuschussbedarf', () => {
    expect(zuschussbedarf(FINANZIERUNGSPRODUKT)).toBeLessThan(0)
  })
})

/** Der Wert, oder ein Fehler mit `was`, wenn die Testdaten ihn nicht haben. */
function vorhanden<T>(wert: T | undefined, was: string): T {
  if (wert === undefined) {
    throw new Error(`Testdaten: ${was} fehlt`)
  }
  return wert
}

/**
 * Prüft die Invarianten eines Modells gegen die Produkte und Werte, aus denen es gebaut ist.
 * Läuft gegen die echten Daten und gegen die synthetischen Daten weiter unten.
 */
function pruefeModell(
  modell: BindungsgradModell,
  liste: readonly Produkt[],
  wert: (code: string) => number,
  finanzierung: string,
): void {
  const reihenfolge = modell.segmente.map((s) => s.bindungsgrad)
  expect(reihenfolge).toEqual(BINDUNGSGRADE.filter((b) => reihenfolge.includes(b)))

  const positiv = liste.filter((p) => p.code !== finanzierung && wert(p.code) > 0)
  const summe = positiv.reduce((gesamt, p) => gesamt + wert(p.code), 0)
  expect(modell.summe).toBe(summe)
  expect(
    modell.segmente.reduce((gesamt, s) => gesamt + s.summe, 0) + (modell.ohneAngabe?.summe ?? 0),
  ).toBe(summe)

  const alleSegmente = [
    ...modell.segmente,
    ...(modell.ohneAngabe === null ? [] : [modell.ohneAngabe]),
  ]
  for (const segment of alleSegmente) {
    expect(segment.anzahl).toBeGreaterThan(0)
    expect(segment.anzahl).toBe(segment.produkte.length)
    expect(segment.summe).toBe(segment.produkte.reduce((s, p) => s + p.wert, 0))
    expect(segment.anteil).toBeCloseTo(segment.summe / modell.summe, 12)
    const werte = segment.produkte.map((p) => p.wert)
    expect(werte).toEqual([...werte].sort((a, b) => b - a))
    for (const eintrag of segment.produkte) {
      const produkt = liste.find((p) => p.code === eintrag.code)
      const erwartet = segment.bindungsgrad === OHNE_ANGABE ? null : segment.bindungsgrad
      expect(produkt?.bindungsgrad, eintrag.code).toBe(erwartet)
      expect(produkt?.pb, eintrag.code).toBe(eintrag.pb)
      expect(produkt?.name, eintrag.code).toBe(eintrag.name)
      expect(eintrag.wert, eintrag.code).toBe(wert(eintrag.code))
    }
  }

  const ohne = positiv.filter((p) => p.bindungsgrad === null).map((p) => p.code)
  expect((modell.ohneAngabe?.produkte ?? []).map((p) => p.code).sort()).toEqual(ohne.sort())
  if (ohne.length === 0) {
    expect(modell.ohneAngabe).toBeNull()
  }

  const negativ = liste
    .filter((p) => p.code !== finanzierung && wert(p.code) < 0)
    .map((p) => p.code)
    .sort()
  expect(modell.ueberschuss.map((p) => p.code).sort()).toEqual(negativ)
  const ueberschussWerte = modell.ueberschuss.map((p) => p.wert)
  expect(ueberschussWerte).toEqual([...ueberschussWerte].sort((a, b) => a - b))
  for (const eintrag of modell.ueberschuss) {
    expect(eintrag.wert, eintrag.code).toBe(wert(eintrag.code))
  }

  const codes = [
    ...alleSegmente.flatMap((s) => s.produkte.map((p) => p.code)),
    ...modell.ueberschuss.map((p) => p.code),
  ]
  expect(codes).not.toContain(finanzierung)
}

describe('baueBindungsgrad', () => {
  const modell = baueBindungsgrad()

  it('hält alle Invarianten auf den echten Daten', () => {
    pruefeModell(modell, produkte, zuschussbedarf, FINANZIERUNGSPRODUKT)
  })

  it('benennt die Segmente mit dem ausgeschriebenen Bindungsgrad', () => {
    for (const segment of modell.segmente) {
      expect(segment.name).toBe(bindungsgradText(segment.bindungsgrad))
    }
  })

  it('liest jeden Wert aus berechnet.zuschussbedarf, ohne neu zu rechnen', () => {
    const alle = [
      ...modell.segmente.flatMap((s) => s.produkte),
      ...(modell.ohneAngabe?.produkte ?? []),
      ...modell.ueberschuss,
    ]
    expect(alle.length).toBeGreaterThan(0)
    for (const eintrag of alle) {
      expect(eintrag.wert, eintrag.code).toBe(zuschussbedarf(eintrag.code))
    }
  })

  it('führt Produkte mit Zuschussbedarf 0 nirgends', () => {
    const ohneBedarf = produkte.filter((p) => zuschussbedarf(p.code) === 0).map((p) => p.code)
    const codes = [
      ...modell.segmente.flatMap((s) => s.produkte.map((p) => p.code)),
      ...(modell.ohneAngabe?.produkte.map((p) => p.code) ?? []),
      ...modell.ueberschuss.map((p) => p.code),
    ]
    for (const code of ohneBedarf) {
      expect(codes).not.toContain(code)
    }
  })

  it('benennt das Segment ohne Angabe als solches', () => {
    if (modell.ohneAngabe !== null) {
      expect(modell.ohneAngabe.bindungsgrad).toBe(OHNE_ANGABE)
      expect(modell.ohneAngabe.bezeichnung).toBe('Ohne Angabe im Plan')
      expect(modell.ohneAngabe.name).toBe('Ohne Angabe im Plan')
    }
  })
})

// ---------------------------------------------------------------------------------------------
// Segmentlogik mit synthetischen Produkten: Hörstel ordnet keinem Produkt einen Bindungsgrad zu,
// deshalb laufen die Segmente pflichtig/teils/freiwillig hier gegen eigene Testdaten.
// ---------------------------------------------------------------------------------------------

describe('baueBindungsgrad mit synthetischen Produkten', () => {
  afterEach(() => {
    vi.doUnmock('@/data/daten')
    vi.resetModules()
  })

  const vorlage = vorhanden(produkte[0], 'erstes Produkt')
  const planVorlage = vorhanden(haushalt.ergebnisplan[vorlage.code], 'Ergebnisplan der Vorlage')

  /** Synthetische Produkte: Code, Bindungsgrad, Zuschussbedarf im Haushaltsjahr. */
  const ZEILEN: readonly [string, string | null, number][] = [
    ['T01', 'pflichtig', 300],
    ['T02', 'freiwillig', 50],
    ['T03', 'pflichtig', 700],
    ['T04', 'freiwillig', 150],
    ['T05', null, 100],
    ['T06', 'pflichtig', -40],
    ['T07', 'freiwillig', 0],
    ['T08', null, -5],
    ['T09', null, 200],
  ]
  const FINANZ = 'T99'

  function produkt(code: string, bindungsgrad: string | null): Produkt {
    return { ...vorlage, code, name: `Produkt ${code}`, bindungsgrad }
  }

  function plan(wert: number): KnotenWerte {
    const reihe = haushalt.jahre.map((_, i) => (i === INDEX ? wert : 0))
    return { ...planVorlage, berechnet: { ...planVorlage.berechnet, zuschussbedarf: reihe } }
  }

  async function ladeMit(zeilen: readonly [string, string | null, number][]) {
    vi.resetModules()
    vi.doMock('@/data/daten', async (importOriginal) => {
      const echt = await importOriginal<typeof import('@/data/daten')>()
      const alle: [string, string | null, number][] = [...zeilen, [FINANZ, 'pflichtig', -9000]]
      return {
        ...echt,
        produkte: alle.map(([code, grad]) => produkt(code, grad)),
        haushalt: {
          ...echt.haushalt,
          finanzierungsprodukt: FINANZ,
          ergebnisplan: Object.fromEntries(alle.map(([code, , wert]) => [code, plan(wert)])),
        },
      }
    })
    return import('@/lib/bindungsgrad')
  }

  function wertVon(zeilen: readonly [string, string | null, number][]) {
    return (code: string): number =>
      code === FINANZ ? -9000 : (zeilen.find(([c]) => c === code)?.[2] ?? Number.NaN)
  }

  it('bildet die Segmente pflichtig und freiwillig, lässt teils ohne Produkte weg', async () => {
    const modul = await ladeMit(ZEILEN)
    expect(modul.FINANZIERUNGSPRODUKT).toBe(FINANZ)
    const modell = modul.baueBindungsgrad()
    pruefeModell(
      modell,
      [...ZEILEN, [FINANZ, 'pflichtig', -9000] as const].map(([c, g]) => produkt(c, g)),
      wertVon(ZEILEN),
      FINANZ,
    )
    expect(modell.segmente.map((s) => s.bindungsgrad)).toEqual(['pflichtig', 'freiwillig'])
    expect(modell.segmente.map((s) => s.summe)).toEqual([1000, 200])
    expect(modell.segmente.map((s) => s.produkte.map((p) => p.code))).toEqual([
      ['T03', 'T01'],
      ['T04', 'T02'],
    ])
    expect(modell.segmente.map((s) => s.bezeichnung)).toEqual(['Pflichtig', 'Freiwillig'])
    expect(modell.segmente.map((s) => s.name)).toEqual(['pflichtig', 'freiwillig'])
    expect(modell.ohneAngabe?.produkte.map((p) => p.code)).toEqual(['T09', 'T05'])
    expect(modell.ohneAngabe?.summe).toBe(300)
    expect(modell.summe).toBe(1500)
    expect(modell.segmente[0]?.anteil).toBeCloseTo(1000 / 1500, 12)
    expect(modell.ohneAngabe?.anteil).toBeCloseTo(300 / 1500, 12)
    expect(modell.ueberschuss.map((p) => p.code)).toEqual(['T06', 'T08'])
  })

  it('führt alle drei Segmente in fester Reihenfolge, auch wenn die Daten anders sortiert sind', async () => {
    const zeilen: [string, string | null, number][] = [
      ['T01', 'freiwillig', 10],
      ['T02', 'teils', 20],
      ['T03', 'pflichtig', 30],
    ]
    const modell = (await ladeMit(zeilen)).baueBindungsgrad()
    expect(modell.segmente.map((s) => s.bindungsgrad)).toEqual(['pflichtig', 'teils', 'freiwillig'])
    expect(modell.segmente.map((s) => s.name)).toEqual([
      'pflichtig',
      'teils pflichtig, teils freiwillig',
      'freiwillig',
    ])
    expect(modell.segmente.map((s) => s.bezeichnung)).toEqual([
      'Pflichtig',
      'Teils pflichtig',
      'Freiwillig',
    ])
    expect(modell.ohneAngabe).toBeNull()
    expect(modell.summe).toBe(60)
  })

  it('wirft bei einem unbekannten Bindungsgrad mit Zuschussbedarf', async () => {
    const modul = await ladeMit([['T01', 'unklar', 10]])
    expect(() => modul.baueBindungsgrad()).toThrow(/T01/)
  })
})

describe('klAnteil (RAT-02, D-02)', () => {
  it('teilt die Weitergabe an Kreis und Land durch die Summe im Balken', () => {
    expect(klAnteil(500, 2000)).toBe(0.25)
    expect(klAnteil(3000, 2000)).toBe(1.5)
  })

  it('liefert null, wenn die Summe im Balken 0 ist', () => {
    expect(klAnteil(500, 0)).toBeNull()
  })

  it('liefert 0 für eine Weitergabe von 0 €', () => {
    expect(klAnteil(0, 2000)).toBe(0)
  })
})

describe('produkteText und segmentZusammenfassung (WR-02, RAT-01)', () => {
  it('nutzt den Singular genau für ein Produkt', () => {
    expect(produkteText(1)).toBe('1 Produkt')
  })

  it('nutzt für 0 und für viele den Plural', () => {
    expect(produkteText(0)).toBe('0 Produkte')
    expect(produkteText(15)).toBe('15 Produkte')
  })

  it('schreibt die Zusammenfassung eines Segments mit genau einem Produkt im Singular', () => {
    const segment: BindungsSegment = {
      bindungsgrad: 'freiwillig',
      name: 'freiwillig',
      bezeichnung: 'Freiwillig',
      summe: 59900,
      anzahl: 1,
      anteil: 1,
      produkte: [{ code: '000000', name: 'Testprodukt', pb: '01', wert: 59900 }],
    }
    expect(segmentZusammenfassung(segment)).toBe(`Freiwillig · ${euroKurz(59900)} · 1 Produkt`)
  })

  it('setzt die Zusammenfassung jedes echten Segments aus Bezeichnung, Summe und Anzahl zusammen', () => {
    const modell = baueBindungsgrad()
    const segmente = [
      ...modell.segmente,
      ...(modell.ohneAngabe === null ? [] : [modell.ohneAngabe]),
    ]
    expect(segmente.length).toBeGreaterThan(0)
    for (const segment of segmente) {
      expect(segmentZusammenfassung(segment)).toBe(
        `${segment.bezeichnung} · ${euroKurz(segment.summe)} · ${produkteText(segment.anzahl)}`,
      )
    }
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('endet die Zusammenfassung von „Ohne Angabe im Plan“ auf 56 Produkte', () => {
      const ohne = baueBindungsgrad().ohneAngabe
      expect(ohne).not.toBeNull()
      expect(segmentZusammenfassung(ohne as BindungsSegment)).toMatch(
        /^Ohne Angabe im Plan · .* · 56 Produkte$/,
      )
    })
  })
})

describe('Anzahltexte in den Komponenten (WR-02)', () => {
  const quelltexte = import.meta.glob<string>(
    [
      '/src/components/MassnahmenFilter.vue',
      '/src/components/ProduktBalkenListe.vue',
      '/src/components/BindungsgradBalken.vue',
    ],
    { query: '?raw', import: 'default', eager: true },
  )
  const quelltext = (name: string): string => {
    const treffer = Object.entries(quelltexte).find(([pfad]) => pfad.endsWith(`/${name}`))
    if (treffer === undefined) {
      throw new Error(`Quelltext ${name} nicht gefunden`)
    }
    return treffer[1]
  }

  it('findet alle drei Komponenten', () => {
    expect(Object.keys(quelltexte)).toHaveLength(3)
  })

  it.each(['MassnahmenFilter.vue', 'ProduktBalkenListe.vue', 'BindungsgradBalken.vue'])(
    'baut in %s keinen Anzahltext mit festem Plural',
    (name) => {
      expect(quelltext(name)).not.toMatch(/\$\{[^}]*\}\s+(Maßnahmen|Produkte)\b/)
    },
  )

  it('nutzt in ProduktBalkenListe.vue segmentZusammenfassung()', () => {
    expect(quelltext('ProduktBalkenListe.vue')).toContain('segmentZusammenfassung(')
  })

  it('nutzt in BindungsgradBalken.vue produkteText() und definiert es nicht selbst', () => {
    const text = quelltext('BindungsgradBalken.vue')
    expect(text).toContain('produkteText(')
    expect(text).not.toMatch(/function\s+produkteText/)
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Bindungsgrad Haushalt 2026 (Hörstel)', () => {
  const modell = baueBindungsgrad()

  it('ordnet keinem Produkt einen Bindungsgrad zu: keine Segmente im Balken', () => {
    expect(produkte.every((p) => p.bindungsgrad === null)).toBe(true)
    expect(modell.segmente).toEqual([])
  })

  it('führt 56 Produkte mit 23.848.827 € unter „Ohne Angabe im Plan“, Anteil 1', () => {
    expect(modell.ohneAngabe?.anzahl).toBe(56)
    expect(modell.ohneAngabe?.summe).toBe(23848827)
    expect(modell.summe).toBe(23848827)
    expect(modell.ohneAngabe?.anteil).toBe(1)
  })

  it('nennt Zentrales Gebäudemanagement (0111110) mit 4.678.561 € als größten Posten', () => {
    expect(modell.ohneAngabe?.produkte[0]).toMatchObject({ code: '0111110', wert: 4678561 })
  })

  it('führt im Überschuss genau zehn Produkte, Abwasserbeseitigung (1153801) zuerst', () => {
    expect(modell.ueberschuss.map((p) => p.code)).toEqual([
      '1153801',
      '0111109',
      '0537501',
      '1153101',
      '1153701',
      '1557302',
      '1153201',
      '1355201',
      '1254501',
      '1153802',
    ])
    expect(modell.ueberschuss[0]?.wert).toBe(-2699505)
  })

  it('lässt die Produkte mit Zuschussbedarf 0 (0531201, 0535101) und 1661101 weg', () => {
    const codes = [
      ...(modell.ohneAngabe?.produkte.map((p) => p.code) ?? []),
      ...modell.ueberschuss.map((p) => p.code),
    ]
    expect(FINANZIERUNGSPRODUKT).toBe('1661101')
    for (const code of ['0531201', '0535101', '1661101']) {
      expect(codes).not.toContain(code)
    }
  })
})
