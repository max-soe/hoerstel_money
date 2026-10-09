import { afterEach, describe, expect, it, vi } from 'vitest'

import { haushalt } from '@/data/daten'
import type { Haushalt, VorberichtPosten } from '@/data/typen'
import {
  AUFSCHLUESSELUNG_FUER_ERTRAGSART,
  GEZEIGTE_PAUSCHALEN,
  SELBST_FESTGELEGTE_STEUERN,
  SONDERPOSTEN_POSTEN,
  baueInvestiveEinnahmen,
  baueInvestiveTabelle,
  baueSonstigeErtraege,
  baueSteuern,
  baueZuwendungen,
  hatInvestiveWerte,
  quellenText,
} from '@/lib/einnahmen'
import { findeBeleg } from '@/lib/quelle'

const JAHRE = haushalt.jahre.map((jahr, index) => [jahr, index] as const)
const GEP = haushalt.ergebnisplan['GESAMT']?.zeilen
const GFP = haushalt.finanzplan['GESAMT']?.zeilen

function tabelle(name: string) {
  const treffer = haushalt.vorbericht[name]
  if (treffer === undefined) {
    throw new Error(`Vorberichtstabelle ${name} fehlt`)
  }
  return treffer
}

function postenSchluessel(name: string): string[] {
  return tabelle(name).posten.map((p) => p.posten)
}

function summe(werte: readonly (number | null)[]): number {
  return werte.reduce<number>((s, w) => s + (w ?? 0), 0)
}

/**
 * Lädt `lib/einnahmen` mit einer veränderten Kopie von `haushalt` neu. So lässt sich die Logik
 * für Strukturen prüfen, die der aktuelle Jahrgang (Hörstel) nicht druckt, etwa
 * Sonderposten-Auflösungen oder Konzessionsabgaben nach Sparte.
 */
async function ladeEinnahmenMit(aendere: (kopie: Haushalt) => void) {
  vi.resetModules()
  vi.doMock('@/data/daten', async (importOriginal) => {
    const original = await importOriginal<typeof import('@/data/daten')>()
    const kopie = structuredClone(original.haushalt)
    aendere(kopie)
    return { ...original, haushalt: kopie }
  })
  return import('@/lib/einnahmen')
}

/** Ein synthetischer Vorbericht-Posten mit demselben Wert in jedem Jahr. */
function testPosten(posten: string, wert: number): VorberichtPosten {
  return {
    posten,
    name: posten,
    werte: haushalt.jahre.map(() => wert),
    gerundet: true,
    berechnet: false,
    quelle: 1,
    anmerkung: null,
  }
}

/** Sucht rekursiv nach `undefined`: Builder liefern `null` für fehlende Werte (Pitfall 7). */
function enthaeltUndefined(wert: unknown): boolean {
  if (wert === undefined) {
    return true
  }
  if (Array.isArray(wert)) {
    return wert.some(enthaeltUndefined)
  }
  if (typeof wert === 'object' && wert !== null) {
    return Object.values(wert).some(enthaeltUndefined)
  }
  return false
}

describe('fachliche Konstanten (Spez. 6.4)', () => {
  it('SELBST_FESTGELEGTE_STEUERN nennt Grund-, Gewerbe-, Hunde- und Vergnügungssteuer', () => {
    expect([...SELBST_FESTGELEGTE_STEUERN].sort()).toEqual(
      [
        'grundsteuer_a',
        'grundsteuer_b',
        'gewerbesteuer',
        'hundesteuer',
        'vergnuegungssteuer',
      ].sort(),
    )
  })

  it.each([...SELBST_FESTGELEGTE_STEUERN])(
    'Steuer %s steht in vorbericht.steuerarten',
    (posten) => {
      expect(postenSchluessel('steuerarten')).toContain(posten)
    },
  )

  it('SONDERPOSTEN_POSTEN nennt die Auflösung von Sonderposten (Zuwendungen und sonstige Erträge)', () => {
    expect([...SONDERPOSTEN_POSTEN].sort()).toEqual(
      ['aufloesung_sonderposten', 'aufloesung_sonstiger_sonderposten'].sort(),
    )
  })

  it.each([...SONDERPOSTEN_POSTEN])(
    'Sonderposten %s steht höchstens einmal in den Aufschlüsselungen',
    (posten) => {
      const vorhanden = [
        ...postenSchluessel('zuwendungen'),
        ...postenSchluessel('sonstige_ertraege'),
      ]
      expect(vorhanden.filter((p) => p === posten).length).toBeLessThanOrEqual(1)
    },
  )

  it('GEZEIGTE_PAUSCHALEN nennt Investitions-, Schul- und Sportpauschale', () => {
    expect([...GEZEIGTE_PAUSCHALEN]).toEqual([
      'investitionspauschale',
      'schulpauschale',
      'sportpauschale',
    ])
  })

  it.each([...GEZEIGTE_PAUSCHALEN])(
    'Pauschale %s steht in vorbericht.investitionszuwendungen',
    (posten) => {
      expect(postenSchluessel('investitionszuwendungen')).toContain(posten)
    },
  )

  it('AUFSCHLUESSELUNG_FUER_ERTRAGSART verknüpft nur Ertragsarten des Gesamtergebnisplans', () => {
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('steuern')).toBe('steuern')
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('zuwendungen')).toBe('zuwendungen')
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('sonstige_ordentliche_ertraege')).toBe('sonstige')
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('kostenerstattungen')).toBeUndefined()
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('__proto__')).toBeUndefined()
  })
})

describe.each(JAHRE)('Aufschlüsselung Jahr %i', (_jahr, index) => {
  it('baueSteuern: acht Steuerarten, Summe weicht um höchstens acht T€ vom Gesamtergebnisplan ab (EINN-02)', () => {
    const zeilen = baueSteuern(index)
    expect(zeilen).toHaveLength(8)
    const plan = GEP?.['steuern']?.[index]
    expect(plan).toBeDefined()
    expect(Math.abs(summe(zeilen.map((z) => z.wert)) - (plan ?? 0))).toBeLessThanOrEqual(8000)
  })

  it('baueSteuern: genau die selbst festgelegten Steuern tragen die Markierung', () => {
    const markiert = baueSteuern(index)
      .filter((z) => z.selbstFestgelegt)
      .map((z) => z.posten)
      .sort()
    expect(markiert).toEqual([...SELBST_FESTGELEGTE_STEUERN].sort())
  })

  it('baueSteuern: Hebesätze nur für Grundsteuer A/B und Gewerbesteuer, mit PDF-Seite', () => {
    for (const zeile of baueSteuern(index)) {
      const hat = ['grundsteuer_a', 'grundsteuer_b', 'gewerbesteuer'].includes(zeile.posten)
      expect(zeile.hebesatz !== null, zeile.posten).toBe(hat)
      expect(zeile.hebesatzQuelle !== null, zeile.posten).toBe(hat)
    }
  })

  it('baueZuwendungen: Summe weicht um höchstens vier T€ vom Gesamtergebnisplan ab', () => {
    const plan = GEP?.['zuwendungen']?.[index]
    expect(plan).toBeDefined()
    const zeilen = baueZuwendungen(index)
    expect(Math.abs(summe(zeilen.map((z) => z.wert)) - (plan ?? 0))).toBeLessThanOrEqual(4000)
  })

  it('baueZuwendungen: nur Sonderposten tragen „kein Geldfluss“ (EINN-03)', () => {
    for (const zeile of baueZuwendungen(index)) {
      expect(zeile.keinGeldfluss, zeile.posten).toBe(SONDERPOSTEN_POSTEN.includes(zeile.posten))
    }
  })

  // Berechnet sind der Rest „Sonstige“ der Pipeline und die abgeschriebenen Reste `uebrige_*`
  // („berechnet: …“ in daten/manuell, Hörstel S. 15/22).
  it('baueZuwendungen: ein berechneter Rest erscheint nur mit Wert', () => {
    for (const zeile of baueZuwendungen(index).filter((z) => z.berechnet)) {
      expect(zeile.posten === 'sonstige' || zeile.posten.startsWith('uebrige_')).toBe(true)
      expect(zeile.wert).not.toBeNull()
      expect(zeile.quelle).not.toBeNull()
    }
  })

  // Der Hörsteler Vorbericht (S. 24) druckt die sonstigen Erträge nur für 2025 und 2026; in
  // den übrigen Jahren sind alle Posten null und der Rest „Sonstige“ entfällt.
  it('baueSonstigeErtraege: Summe der Hauptposten weicht um höchstens drei T€ vom Gesamtergebnisplan ab (EINN-04)', () => {
    const plan = GEP?.['sonstige_ordentliche_ertraege']?.[index]
    expect(plan).toBeDefined()
    const hauptposten = baueSonstigeErtraege(index).filter((z) => z.teilVon === null)
    expect(hauptposten.length).toBeGreaterThan(0)
    const gedruckt = tabelle('sonstige_ertraege').gesamt_vorbericht?.werte[index] ?? null
    if (gedruckt === null) {
      expect(hauptposten.every((z) => z.wert === null && !z.berechnet)).toBe(true)
    } else {
      expect(Math.abs(summe(hauptposten.map((z) => z.wert)) - (plan ?? 0))).toBeLessThanOrEqual(
        3000,
      )
    }
  })

  it('baueSonstigeErtraege: die Konzessionsabgaben stehen unter den Posten des Vorberichts', () => {
    expect(baueSonstigeErtraege(index).map((z) => z.posten)).toContain('konzessionsabgaben')
  })

  it('baueSonstigeErtraege: nur Sonderposten-Auflösungen tragen „kein Geldfluss“', () => {
    for (const zeile of baueSonstigeErtraege(index)) {
      expect(zeile.keinGeldfluss, zeile.posten).toBe(SONDERPOSTEN_POSTEN.includes(zeile.posten))
    }
  })

  it('kein Builder liefert undefined (fehlende Werte sind null)', () => {
    expect(enthaeltUndefined(baueSteuern(index))).toBe(false)
    expect(enthaeltUndefined(baueZuwendungen(index))).toBe(false)
    expect(enthaeltUndefined(baueSonstigeErtraege(index))).toBe(false)
    expect(enthaeltUndefined(baueInvestiveEinnahmen(index))).toBe(false)
    expect(enthaeltUndefined(baueInvestiveTabelle(index))).toBe(false)
  })
})

const SPARTEN = ['konzessionsabgabe_strom', 'konzessionsabgabe_gas', 'konzessionsabgabe_wasser']

describe('Konzessionsabgaben nach Sparte', () => {
  afterEach(() => {
    vi.doUnmock('@/data/daten')
    vi.resetModules()
  })

  it('ohne Sparten in meta.vorbericht_werte gibt es in keinem Jahr Unterzeilen (Hörstel)', () => {
    const vorhanden = SPARTEN.filter((s) => haushalt.meta.vorbericht_werte[s] !== undefined)
    expect(vorhanden).toEqual([])
    for (const [jahr, index] of JAHRE) {
      const unterzeilen = baueSonstigeErtraege(index).filter((z) => z.teilVon !== null)
      expect(unterzeilen, String(jahr)).toEqual([])
    }
  })

  /** Konzessionsabgaben des Haushaltsjahrs, synthetisch auf Strom, Gas und Wasser verteilt. */
  async function ladeMitSparten(sparten: readonly string[]) {
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    const posten = tabelle('sonstige_ertraege').posten.find(
      (p) => p.posten === 'konzessionsabgaben',
    )
    const gesamt = posten?.werte[index] ?? 0
    expect(gesamt).toBeGreaterThan(0)
    const anteile = [gesamt - 2000, 1000, 1000]
    const modul = await ladeEinnahmenMit((kopie) => {
      sparten.forEach((schluessel) => {
        kopie.meta.vorbericht_werte[schluessel] = {
          wert: anteile[SPARTEN.indexOf(schluessel)] ?? 0,
          einheit: 'euro',
          quelle: 24,
          gerundet: true,
        }
      })
    })
    return { modul, index, gesamt }
  }

  it('Unterzeilen erscheinen nur im Haushaltsjahr (synthetische Sparten)', async () => {
    const { modul } = await ladeMitSparten(SPARTEN)
    for (const [jahr, index] of JAHRE) {
      const unterzeilen = modul
        .baueSonstigeErtraege(index)
        .filter((z) => z.teilVon === 'konzessionsabgaben')
      expect(unterzeilen.length > 0, String(jahr)).toBe(jahr === haushalt.haushaltsjahr)
    }
  })

  it('Strom, Gas und Wasser ergeben im Haushaltsjahr den Posten Konzessionsabgaben (synthetische Sparten)', async () => {
    const { modul, index, gesamt } = await ladeMitSparten(SPARTEN)
    const zeilen = modul.baueSonstigeErtraege(index)
    expect(zeilen.find((z) => z.posten === 'konzessionsabgaben')?.wert).toBe(gesamt)
    const teile = zeilen.filter((z) => z.teilVon === 'konzessionsabgaben')
    expect(teile.map((z) => z.posten).sort()).toEqual([...SPARTEN].sort())
    expect(summe(teile.map((z) => z.wert))).toBe(gesamt)
    for (const teil of teile) {
      expect(teil.gerundet, teil.posten).toBe(true)
      expect(teil.quelle, teil.posten).toBe(24)
      expect(teil.beleg, teil.posten).toBe(`meta:vorbericht_werte.${teil.posten}`)
      expect(teil.keinGeldfluss, teil.posten).toBe(false)
    }
  })

  it('die Unterzeilen stehen direkt hinter den Konzessionsabgaben (synthetische Sparten)', async () => {
    const { modul, index } = await ladeMitSparten(SPARTEN)
    const posten = modul.baueSonstigeErtraege(index).map((z) => z.posten)
    const start = posten.indexOf('konzessionsabgaben')
    expect(start).toBeGreaterThanOrEqual(0)
    expect(posten.slice(start + 1, start + 4)).toEqual(SPARTEN)
  })

  it('nur ein Teil der Sparten ist ein Datenfehler', async () => {
    const { modul, index } = await ladeMitSparten(['konzessionsabgabe_strom'])
    expect(() => modul.baueSonstigeErtraege(index)).toThrow(/konzessionsabgabe_gas/)
  })
})

describe('Sonderposten-Auflösung (EINN-03, synthetische Posten)', () => {
  afterEach(() => {
    vi.doUnmock('@/data/daten')
    vi.resetModules()
  })

  it('trägt in Zuwendungen und sonstigen Erträgen „kein Geldfluss“, die übrigen Posten nicht', async () => {
    const modul = await ladeEinnahmenMit((kopie) => {
      kopie.vorbericht['zuwendungen']?.posten.push(testPosten('aufloesung_sonderposten', 1000))
      kopie.vorbericht['sonstige_ertraege']?.posten.push(
        testPosten('aufloesung_sonstiger_sonderposten', 1000),
      )
    })
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    const zuwendungen = modul.baueZuwendungen(index)
    const sonstige = modul.baueSonstigeErtraege(index)
    expect(zuwendungen.find((z) => z.posten === 'aufloesung_sonderposten')?.keinGeldfluss).toBe(
      true,
    )
    expect(
      sonstige.find((z) => z.posten === 'aufloesung_sonstiger_sonderposten')?.keinGeldfluss,
    ).toBe(true)
    for (const zeile of [...zuwendungen, ...sonstige]) {
      expect(zeile.keinGeldfluss, zeile.posten).toBe(SONDERPOSTEN_POSTEN.includes(zeile.posten))
    }
  })
})

describe('Hebesätze (EINN-02)', () => {
  it('stammen aus meta.hebesaetze', () => {
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    for (const zeile of baueSteuern(index)) {
      const meta = haushalt.meta.hebesaetze[zeile.posten]
      if (meta === undefined) {
        expect(zeile.hebesatz).toBeNull()
      } else {
        expect(zeile.hebesatz).toBe(meta.wert)
        expect(zeile.hebesatzQuelle).toBe(meta.quelle)
      }
    }
  })
})

describe.each(JAHRE)('investive Einnahmen Jahr %i (EINN-06, D-03)', (_jahr, index) => {
  const gfp = (schluessel: string): number | undefined => GFP?.[schluessel]?.[index]
  const hatAufschluesselung = tabelle('investitionszuwendungen').posten.some(
    (p) => p.werte[index] != null,
  )

  it('Pauschalen plus „Sonstige (berechnet)“ ergeben die Zeile 18 des Gesamtfinanzplans', () => {
    const zeilen = baueInvestiveEinnahmen(index)
    const teile = zeilen.filter((z) => z.gruppe === 'pauschale' || z.gruppe === 'sonstige')
    expect(summe(teile.map((z) => z.wert))).toBe(gfp('investitionszuwendungen'))
  })

  it('Grundstücksverkäufe, Beiträge und Kredite sind die Finanzplan-Zeilen', () => {
    const zeilen = baueInvestiveEinnahmen(index)
    const wert = (schluessel: string) => zeilen.find((z) => z.schluessel === schluessel)?.wert
    expect(wert('veraeusserung_sachanlagen')).toBe(gfp('veraeusserung_sachanlagen'))
    expect(wert('beitraege')).toBe(gfp('beitraege'))
    expect(wert('kreditaufnahme')).toBe(gfp('kreditaufnahme'))
  })

  it('die Reihenfolge folgt dem UI-SPEC', () => {
    expect(baueInvestiveEinnahmen(index).map((z) => z.schluessel)).toEqual([
      'investitionspauschale',
      'schulpauschale',
      'sportpauschale',
      'sonstige_berechnet',
      'veraeusserung_sachanlagen',
      'beitraege',
      'kreditaufnahme',
    ])
  })

  it('„Sonstige (berechnet)“ ist als berechnet gekennzeichnet, die übrigen Zeilen nicht', () => {
    for (const zeile of baueInvestiveEinnahmen(index)) {
      expect(zeile.berechnet, zeile.schluessel).toBe(zeile.schluessel === 'sonstige_berechnet')
    }
  })

  it('jede Zeile kennt ihre PDF-Seite', () => {
    for (const zeile of baueInvestiveEinnahmen(index)) {
      expect(zeile.quelle, zeile.schluessel).not.toBeNull()
    }
  })

  it(
    hatAufschluesselung
      ? 'mit gedruckter Aufschlüsselung tragen die Pauschalen Werte'
      : 'ohne gedruckte Aufschlüsselung sind alle Pauschalen null und „Sonstige“ trägt die ganze Zeile 18',
    () => {
      const zeilen = baueInvestiveEinnahmen(index)
      const pauschalen = zeilen.filter((z) => z.gruppe === 'pauschale')
      const sonstige = zeilen.find((z) => z.schluessel === 'sonstige_berechnet')
      if (hatAufschluesselung) {
        expect(pauschalen.some((z) => z.wert !== null)).toBe(true)
      } else {
        expect(pauschalen.every((z) => z.wert === null)).toBe(true)
        expect(sonstige?.wert).toBe(gfp('investitionszuwendungen'))
      }
    },
  )

  it('die Tabelle nennt die Finanzplan-Zeilen mit ihrem gedruckten Namen', () => {
    const tabellenzeilen = baueInvestiveTabelle(index)
    const finanzplan = tabellenzeilen.filter((z) => z.gruppe === 'finanzplan')
    expect(finanzplan.map((z) => z.schluessel)).toEqual([
      'investitionszuwendungen',
      'veraeusserung_sachanlagen',
      'beitraege',
      'kreditaufnahme',
    ])
    for (const zeile of finanzplan) {
      expect(zeile.name.length, zeile.schluessel).toBeGreaterThan(0)
      expect(zeile.wert, zeile.schluessel).toBe(gfp(zeile.schluessel))
    }
  })

  it('die Tabelle listet alle gedruckten Pauschalen und Förderungen des Jahres', () => {
    const gedruckt = tabelle('investitionszuwendungen').posten.filter((p) => p.werte[index] != null)
    const tabellenzeilen = baueInvestiveTabelle(index).filter((z) => z.gruppe === 'pauschale')
    expect(tabellenzeilen.map((z) => z.schluessel)).toEqual(gedruckt.map((p) => p.posten))
    expect(tabellenzeilen.every((z) => z.gerundet)).toBe(true)
  })
})

describe('quellenText', () => {
  it('nennt eine einzelne Seite im Singular', () => {
    expect(quellenText([27, 27, null])).toBe('Quelle: PDF-Seite 27')
  })

  it('nennt mehrere Seiten aufsteigend und ohne Doppelte', () => {
    expect(quellenText([29, 28, 28])).toBe('Quelle: PDF-Seiten 28, 29')
  })

  it('liefert ohne Seite keine Zeile', () => {
    expect(quellenText([])).toBeUndefined()
    expect(quellenText([null])).toBeUndefined()
  })
})

describe('hatInvestiveWerte', () => {
  it('ist falsch ohne Zeilen und bei lauter Nullen oder fehlenden Werten', () => {
    expect(hatInvestiveWerte([])).toBe(false)
    expect(
      hatInvestiveWerte([
        {
          schluessel: 'a',
          name: 'A',
          wert: 0,
          gerundet: false,
          berechnet: false,
          quelle: 1,
          beleg: null,
          herleitung: null,
          gruppe: 'finanzplan',
        },
        {
          schluessel: 'b',
          name: 'B',
          wert: null,
          gerundet: false,
          berechnet: false,
          quelle: 1,
          beleg: null,
          herleitung: null,
          gruppe: 'pauschale',
        },
      ]),
    ).toBe(false)
  })

  it('ist wahr, sobald eine Zeile einen Wert ungleich 0 hat', () => {
    expect(
      hatInvestiveWerte([
        {
          schluessel: 'a',
          name: 'A',
          wert: 5,
          gerundet: false,
          berechnet: false,
          quelle: 1,
          beleg: null,
          herleitung: null,
          gruppe: 'finanzplan',
        },
      ]),
    ).toBe(true)
  })

  it('jedes Jahr der Daten hat investive Einnahmen', () => {
    for (const [, index] of JAHRE) {
      expect(hatInvestiveWerte(baueInvestiveEinnahmen(index))).toBe(true)
    }
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)(
  'Haushalt 2026: Werte aus dem PDF (S. 8, 16, 22, 61, 80)',
  () => {
    const index = haushalt.jahre.indexOf(2026)

    it('Steuerarten: Gewerbesteuer 15.734.000 € (S. 16), Hebesatz 421 (S. 8)', () => {
      const gewerbe = baueSteuern(index).find((z) => z.posten === 'gewerbesteuer')
      expect(gewerbe?.wert).toBe(15_734_000)
      expect(gewerbe?.gerundet).toBe(true)
      expect(gewerbe?.quelle).toBe(16)
      expect(gewerbe?.hebesatz).toBe(421)
      expect(gewerbe?.hebesatzQuelle).toBe(8)
    })

    it('Zuwendungen: Schlüsselzuweisung 4.478.000 € (S. 22), kein Rest „Sonstige“', () => {
      const zeilen = baueZuwendungen(index)
      const schluessel = zeilen.find((z) => z.posten === 'schluesselzuweisung')
      expect(schluessel?.wert).toBe(4_478_000)
      expect(schluessel?.quelle).toBe(22)
      // Schlüsselzuweisung und übrige Zuwendungen (5.745 T€, S. 15) ergeben die gedruckte
      // Summe 10.223 T€; ein Rest bleibt nicht.
      expect(zeilen.find((z) => z.posten === 'uebrige_zuwendungen')?.wert).toBe(5_745_000)
      expect(zeilen.find((z) => z.posten === 'sonstige')).toBeUndefined()
    })

    it('Hörstel druckt keine Sonderposten-Auflösung in Zuwendungen und sonstigen Erträgen', () => {
      const vorhanden = [
        ...postenSchluessel('zuwendungen'),
        ...postenSchluessel('sonstige_ertraege'),
      ]
      for (const posten of SONDERPOSTEN_POSTEN) {
        expect(vorhanden).not.toContain(posten)
      }
    })

    it('Investive Einnahmen: Pauschalen 2.137.000 / 738.000 / 83.000 € (S. 61), Sonstige (berechnet) 1.453.383 €', () => {
      const zeilen = baueInvestiveEinnahmen(index)
      const wert = (schluessel: string) => zeilen.find((z) => z.schluessel === schluessel)?.wert
      expect(wert('investitionspauschale')).toBe(2_137_000)
      expect(wert('schulpauschale')).toBe(738_000)
      expect(wert('sportpauschale')).toBe(83_000)
      // Gesamtfinanzplan S. 80, Zeile 18: 4.411.383 € minus 2.958.000 € Pauschalen
      expect(wert('sonstige_berechnet')).toBe(1_453_383)
    })

    it('„Sonstige (berechnet)“ entspricht bis auf die T€-Rundung den übrigen Posten von S. 80', () => {
      const uebrige = tabelle('investitionszuwendungen').posten.filter(
        (p) => !GEZEIGTE_PAUSCHALEN.includes(p.posten),
      )
      const erwartet = summe(uebrige.map((p) => p.werte[index] ?? null))
      expect(erwartet).toBe(1_453_000)
      const sonstige = baueInvestiveEinnahmen(index).find(
        (z) => z.schluessel === 'sonstige_berechnet',
      )
      expect(Math.abs((sonstige?.wert ?? 0) - erwartet)).toBeLessThan(500)
    })
  },
)

describe.each(JAHRE)('Belegschlüssel der Tabellenzeilen, Jahr %i (D-01)', (_jahr, index) => {
  it('baueSteuern, baueZuwendungen: vb-Schlüssel je Posten, der Beleg löst auf', () => {
    for (const [name, zeilen] of [
      ['steuerarten', baueSteuern(index)],
      ['zuwendungen', baueZuwendungen(index)],
    ] as const) {
      for (const zeile of zeilen) {
        expect(zeile.beleg, `${name}:${zeile.posten}`).toBe(`vb:${name}:${zeile.posten}`)
        expect(findeBeleg(zeile.beleg ?? '')?.pdfSeite, `${name}:${zeile.posten}`).toBe(
          zeile.quelle,
        )
      }
    }
  })

  it('baueSonstigeErtraege: vb-Schlüssel, die Konzessionsabgaben nach Sparte tragen den meta-Schlüssel', () => {
    for (const zeile of baueSonstigeErtraege(index)) {
      const erwartet =
        zeile.teilVon === null
          ? `vb:sonstige_ertraege:${zeile.posten}`
          : `meta:vorbericht_werte.${zeile.posten}`
      expect(zeile.beleg, zeile.posten).toBe(erwartet)
      expect(findeBeleg(zeile.beleg ?? '')?.pdfSeite, zeile.posten).toBe(zeile.quelle)
    }
  })

  it('berechnete Posten nennen eine Herleitung, gedruckte nicht', () => {
    for (const zeile of [
      ...baueSteuern(index),
      ...baueZuwendungen(index),
      ...baueSonstigeErtraege(index),
    ]) {
      expect(zeile.herleitung !== null, zeile.posten).toBe(zeile.berechnet)
    }
  })

  it('baueInvestiveTabelle: Pauschalen und Förderungen vb, Finanzplan-Zeilen fp:GESAMT', () => {
    for (const zeile of baueInvestiveTabelle(index)) {
      const erwartet =
        zeile.gruppe === 'finanzplan'
          ? `fp:GESAMT:${zeile.schluessel}`
          : `vb:investitionszuwendungen:${zeile.schluessel}`
      expect(zeile.beleg, zeile.schluessel).toBe(erwartet)
      expect(findeBeleg(zeile.beleg ?? ''), zeile.schluessel).not.toBeNull()
    }
  })

  it('baueInvestiveEinnahmen: „Sonstige (berechnet)“ zeigt auf die Finanzplanzeile und nennt die Herleitung', () => {
    const sonstige = baueInvestiveEinnahmen(index).find(
      (z) => z.schluessel === 'sonstige_berechnet',
    )
    expect(sonstige?.beleg).toBe('fp:GESAMT:investitionszuwendungen')
    expect(sonstige?.herleitung).toMatch(/Pauschalen/)
    for (const zeile of baueInvestiveEinnahmen(index)) {
      expect(findeBeleg(zeile.beleg ?? ''), zeile.schluessel).not.toBeNull()
      expect(zeile.herleitung !== null, zeile.schluessel).toBe(zeile.berechnet)
    }
  })
})
