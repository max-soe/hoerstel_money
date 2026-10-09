import { afterEach, describe, expect, it, vi } from 'vitest'

import { haushalt } from '@/data/daten'
import type { VorberichtPosten, VorberichtTabelle } from '@/data/typen'
import { baueKreisumlage, findeKlKnoten } from '@/lib/kreisumlage'
import { findeBeleg } from '@/lib/quelle'
import {
  kitaZuschuesse,
  nichtBeeinflussbar,
  ohneLeere,
  optionaleVorberichtTabelle,
  SOZIALLEISTUNGEN_BEZEICHNUNG,
  vorberichtPosten,
  vorberichtTabelle,
  weitereZuschuesse,
  zusammen,
} from '@/lib/zuschuesse'

const INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

/** Die eigenen Zuschüsse unter den Transferaufwendungen, wie `lib/zuschuesse.ts` sie sucht. */
const TRANSFER_ZUSCHUESSE = [
  'zuschuss_kinder_jugendwerk',
  'zuschuss_ogs',
  'zuweisungen_zuschuesse_laufende_zwecke',
]

/** Die Schlüssel der Sozialleistungen; jeder Jahrgang trägt genau einen. */
const SOZIAL_SCHLUESSEL = ['sozialleistungen', 'sozialtransferaufwendungen']

const TRANSFER_POSTEN = haushalt.vorbericht.transferaufwendungen?.posten ?? []

function transferWert(schluessel: string): number | null | undefined {
  return haushalt.vorbericht.transferaufwendungen?.posten.find((p) => p.posten === schluessel)
    ?.werte[INDEX]
}

function summe(posten: readonly { wert: number | null }[]): number {
  return posten.reduce((s, p) => s + (p.wert ?? 0), 0)
}

describe('vorberichtTabelle', () => {
  it('liefert eine vorhandene Vorberichtstabelle', () => {
    expect(vorberichtTabelle('transferaufwendungen').tabelle).toBe('transferaufwendungen')
  })

  it('wirft bei einer fehlenden Tabelle mit dem Namen der Tabelle', () => {
    expect(() => vorberichtTabelle('gibt_es_nicht')).toThrow(/gibt_es_nicht/)
  })
})

describe('optionaleVorberichtTabelle', () => {
  it('liefert eine vorhandene Tabelle wie vorberichtTabelle', () => {
    expect(optionaleVorberichtTabelle('transferaufwendungen')).toBe(
      vorberichtTabelle('transferaufwendungen'),
    )
  })

  it('liefert null statt zu werfen, wenn der Jahrgang die Tabelle nicht druckt', () => {
    expect(optionaleVorberichtTabelle('gibt_es_nicht')).toBeNull()
  })
})

describe('vorberichtPosten', () => {
  it('liefert einen vorhandenen Posten und wirft bei einem fehlenden mit dessen Namen', () => {
    const erster = TRANSFER_POSTEN[0]
    expect(erster).toBeDefined()
    expect(vorberichtPosten('transferaufwendungen', erster?.posten ?? '')).toBe(erster)
    expect(() => vorberichtPosten('transferaufwendungen', 'gibt_es_nicht')).toThrow(/gibt_es_nicht/)
  })
})

describe('kitaZuschuesse', () => {
  it('liefert die Tabelle genau dann, wenn der Jahrgang sie druckt', () => {
    const kita = kitaZuschuesse()
    if (haushalt.vorbericht['kita_zuschuesse'] === undefined) {
      expect(kita).toBeNull()
    } else {
      expect(kita?.posten.length).toBeGreaterThan(0)
    }
  })
})

describe('weitereZuschuesse', () => {
  it('führt unter transfer genau die vorhandenen eigenen Zuschüsse der Transferaufwendungen', () => {
    const { transfer } = weitereZuschuesse()
    const erwartet = TRANSFER_ZUSCHUESSE.filter((s) => TRANSFER_POSTEN.some((p) => p.posten === s))
    expect(transfer.posten.map((p) => p.schluessel)).toEqual(erwartet)
    expect(transfer.gesamt).toBeNull()
    for (const p of transfer.posten) {
      expect(p.wert, p.schluessel).toBe(transferWert(p.schluessel) ?? null)
      expect(p.gerundet, p.schluessel).toBe(true)
      expect(p.pdfSeite, p.schluessel).not.toBeNull()
    }
    expect(transfer.pdfSeiten).toEqual(
      [...new Set(transfer.posten.flatMap((p) => (p.pdfSeite === null ? [] : [p.pdfSeite])))].sort(
        (a, b) => a - b,
      ),
    )
  })

  it('liefert lfdZwecke genau dann, wenn der Jahrgang die Einzelposten druckt', () => {
    const { lfdZwecke } = weitereZuschuesse()
    if (haushalt.vorbericht['zuschuesse_lfd_zwecke'] === undefined) {
      expect(lfdZwecke).toBeNull()
    } else {
      expect(lfdZwecke?.posten.length).toBeGreaterThan(0)
    }
  })
})

describe('zusammen', () => {
  const posten = (wert: number | null) => ({
    schluessel: 'x',
    name: 'X',
    wert,
    gerundet: true,
    pdfSeite: 1,
    beleg: null,
  })

  it('nimmt die gedruckte Gesamtzeile, wenn es sie gibt, ohne Kennzeichen berechnet', () => {
    expect(zusammen({ posten: [posten(1000)], gesamt: 5000, pdfSeiten: [1] })).toEqual({
      wert: 5000,
      berechnet: false,
    })
  })

  it('summiert ohne Gesamtzeile nur vorhandene Werte und kennzeichnet sie als berechnet', () => {
    expect(
      zusammen({
        posten: [posten(1000), posten(null), posten(2000)],
        gesamt: null,
        pdfSeiten: [1],
      }),
    ).toEqual({ wert: 3000, berechnet: true })
  })

  it('liefert null, wenn kein einziger Wert vorhanden ist', () => {
    expect(zusammen({ posten: [posten(null)], gesamt: null, pdfSeiten: [1] })).toBeNull()
    expect(zusammen({ posten: [], gesamt: null, pdfSeiten: [] })).toBeNull()
  })

  it('die Gruppe transfer hat keine gedruckte Gesamtzeile und ist immer berechnet', () => {
    const summeTransfer = zusammen(weitereZuschuesse().transfer)
    expect(summeTransfer?.berechnet).toBe(true)
    expect(summeTransfer?.wert).toBe(summe(weitereZuschuesse().transfer.posten))
  })

  it('eine gedruckte Gesamtzeile ist nicht berechnet, eine selbst gebildete Summe ist es', () => {
    const posten = (wert: number | null) => ({
      schluessel: 'x',
      name: 'X',
      wert,
      gerundet: true,
      pdfSeite: 1,
      beleg: null,
    })
    expect(zusammen({ posten: [posten(5)], gesamt: 100, pdfSeiten: [1] })).toEqual({
      wert: 100,
      berechnet: false,
    })
    expect(zusammen({ posten: [posten(5), posten(7)], gesamt: null, pdfSeiten: [1] })).toEqual({
      wert: 12,
      berechnet: true,
    })
    expect(zusammen({ posten: [posten(null)], gesamt: null, pdfSeiten: [1] })).toBeNull()
    // Hörstel druckt weder Kita- noch Einzelzuschuss-Tabelle; wo es sie gibt, ist die Gesamtzeile gedruckt.
    for (const gruppe of [kitaZuschuesse(), weitereZuschuesse().lfdZwecke]) {
      if (gruppe !== null && gruppe.gesamt !== null) {
        expect(zusammen(gruppe)?.berechnet).toBe(false)
      }
    }
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Einzelzuschüsse Haushalt 2026 (Hörstel)', () => {
  it('druckt weder Kita-Tabelle noch Einzelposten der laufenden Zwecke', () => {
    expect(kitaZuschuesse()).toBeNull()
    expect(weitereZuschuesse().lfdZwecke).toBeNull()
  })

  it('Zuweisungen und Zuschüsse für laufende Zwecke 2.773.000 € (S. 33) als einziger Transferzuschuss', () => {
    const { transfer } = weitereZuschuesse()
    expect(transfer.posten.map((p) => [p.schluessel, p.wert, p.pdfSeite])).toEqual([
      ['zuweisungen_zuschuesse_laufende_zwecke', 2773000, 33],
    ])
    expect(zusammen(transfer)).toEqual({ wert: 2773000, berechnet: true })
    expect(transfer.pdfSeiten).toEqual([33])
  })
})

describe('Zuschuss.beleg', () => {
  it('trägt zu jedem Posten mit Seite einen auflösbaren Schlüssel, ohne Seite null', () => {
    const { transfer, lfdZwecke } = weitereZuschuesse()
    const alle = [
      ...(kitaZuschuesse()?.posten ?? []),
      ...transfer.posten,
      ...(lfdZwecke?.posten ?? []),
    ]
    expect(alle.length).toBeGreaterThan(0)
    for (const z of alle) {
      if (z.pdfSeite === null) {
        expect(z.beleg, z.schluessel).toBeNull()
      } else {
        expect(findeBeleg(z.beleg ?? '')?.pdfSeite, z.schluessel).toBe(z.pdfSeite)
      }
    }
  })

  it('nichtBeeinflussbar liefert zu jeder Kachel einen auflösbaren Schlüssel', () => {
    for (const p of nichtBeeinflussbar().posten) {
      expect(findeBeleg(p.beleg ?? ''), p.schluessel).not.toBeNull()
    }
  })
})

describe('ohneLeere', () => {
  const posten = (schluessel: string, wert: number | null) => ({
    schluessel,
    name: schluessel,
    wert,
    gerundet: true,
    pdfSeite: 1,
    beleg: null,
  })

  it('lässt Posten mit dem Wert 0 oder ohne Wert weg', () => {
    const rest = ohneLeere([posten('a', 0), posten('b', null), posten('c', 5000)])
    expect(rest.map((p) => p.schluessel)).toEqual(['c'])
  })
})

describe('nichtBeeinflussbar', () => {
  const ergebnis = nichtBeeinflussbar()

  it('enthält jeden Unterposten der Weitergabe an Kreis und Land mit denselben Werten wie /ausgaben', () => {
    const kreisumlage = baueKreisumlage(INDEX)
    expect(kreisumlage.unterposten.length).toBeGreaterThan(0)
    for (const u of kreisumlage.unterposten) {
      const kachel = ergebnis.posten.find((p) => p.schluessel === u.code)
      expect(kachel?.wert, u.code).toBe(u.wert)
      expect(kachel?.name, u.code).toBe(u.name)
      expect(kachel?.pdfSeite, u.code).toBe(u.pdfSeite)
    }
  })

  it('enthält die gesetzlichen Sozialleistungen aus den Transferaufwendungen', () => {
    const kachel = ergebnis.posten.find((p) => p.name === SOZIALLEISTUNGEN_BEZEICHNUNG)
    const sozial = TRANSFER_POSTEN.filter((p) => SOZIAL_SCHLUESSEL.includes(p.posten))
    expect(sozial).toHaveLength(1)
    expect(kachel?.schluessel ?? sozial[0]?.posten).toBe(sozial[0]?.posten)
    const wert = transferWert(sozial[0]?.posten ?? '')
    if (wert === null || wert === undefined || wert === 0) {
      expect(kachel).toBeUndefined()
    } else {
      expect(kachel?.wert).toBe(wert)
    }
  })

  it('zeigt keinen Posten ohne Wert oder mit dem Wert 0 und belegt jeden mit einer PDF-Seite', () => {
    expect(ergebnis.posten.length).toBeGreaterThan(0)
    for (const p of ergebnis.posten) {
      expect(p.wert, p.schluessel).not.toBeNull()
      expect(p.wert, p.schluessel).not.toBe(0)
      expect(p.pdfSeite, p.schluessel).not.toBeNull()
      expect(p.gerundet, p.schluessel).toBe(true)
    }
  })

  it('liefert Gesamtbetrag und Namen der Weitergabe an Kreis und Land', () => {
    expect(ergebnis.klGesamt).toBe(baueKreisumlage(INDEX).gesamt)
    expect(ergebnis.klName).toBe(findeKlKnoten().name)
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Nicht beeinflussbare Posten Haushalt 2026', () => {
  const werte = Object.fromEntries(nichtBeeinflussbar().posten.map((p) => [p.name, p.wert]))

  it('Kreisumlage 12.465.000 €, Jugendamtsumlage 10.202.000 € (S. 34/35), Gewerbesteuerumlage 1.327.000 € (S. 557)', () => {
    expect(werte.Kreisumlage).toBe(12465000)
    expect(werte.Jugendamtsumlage).toBe(10202000)
    expect(werte.Gewerbesteuerumlage).toBe(1327000)
  })

  it('Gesetzliche Sozialleistungen 1.537.000 € aus den Sozialtransferaufwendungen (S. 33)', () => {
    const kachel = nichtBeeinflussbar().posten.find((p) => p.name === SOZIALLEISTUNGEN_BEZEICHNUNG)
    expect(kachel?.schluessel).toBe('sozialtransferaufwendungen')
    expect(kachel?.wert).toBe(1537000)
    expect(kachel?.pdfSeite).toBe(33)
  })

  it('vier Kacheln, Weitergabe an Kreis und Land 23.994.000 €', () => {
    expect(nichtBeeinflussbar().posten).toHaveLength(4)
    expect(nichtBeeinflussbar().klGesamt).toBe(23994000)
  })
})

// ---------------------------------------------------------------------------------------------
// Synthetische Vorberichtstabellen (Kita-Einrichtungen, Einzelposten der laufenden Zwecke,
// Kinder- und Jugendwerk/OGS), die der Hörsteler Vorbericht nicht druckt
// ---------------------------------------------------------------------------------------------

describe('Zuschüsse mit synthetischen Vorberichtstabellen', () => {
  afterEach(() => {
    vi.doUnmock('@/data/daten')
    vi.resetModules()
  })

  const gefunden = haushalt.vorbericht.transferaufwendungen
  if (gefunden === undefined) {
    throw new Error('Testdaten: Transferaufwendungen fehlen')
  }
  const transferTabelle: VorberichtTabelle = gefunden

  /** Werte nur im Haushaltsjahr, sonst `null`. */
  function imHaushaltsjahr(wert: number): (number | null)[] {
    return haushalt.jahre.map((_, i) => (i === INDEX ? wert : null))
  }

  function posten(
    schluessel: string,
    wert: number | null,
    quelle: number | null,
  ): VorberichtPosten {
    return {
      posten: schluessel,
      name: `Posten ${schluessel}`,
      werte: wert === null ? haushalt.jahre.map(() => null) : imHaushaltsjahr(wert),
      gerundet: true,
      berechnet: false,
      quelle,
      anmerkung: null,
    }
  }

  function tabelle(
    name: string,
    liste: VorberichtPosten[],
    gesamt: number | null,
    quelle: number | null,
  ): VorberichtTabelle {
    return {
      ...transferTabelle,
      tabelle: name,
      planzeile: null,
      gesamt_plan: null,
      gesamt_vorbericht: {
        werte: gesamt === null ? haushalt.jahre.map(() => null) : imHaushaltsjahr(gesamt),
        gerundet: true,
        quelle,
      },
      posten: liste,
    }
  }

  /** Lädt `lib/zuschuesse` mit den angegebenen Vorberichtstabellen neu. */
  async function ladeMit(vorbericht: Record<string, VorberichtTabelle>) {
    vi.resetModules()
    vi.doMock('@/data/daten', async (importOriginal) => {
      const echt = await importOriginal<typeof import('@/data/daten')>()
      return {
        ...echt,
        haushalt: { ...echt.haushalt, vorbericht: { ...echt.haushalt.vorbericht, ...vorbericht } },
      }
    })
    return import('@/lib/zuschuesse')
  }

  const OSTBEVERN_ARTIG = {
    transferaufwendungen: tabelle(
      'transferaufwendungen',
      [
        posten('zuschuss_ogs', 90_000, 46),
        posten('zuschuss_kinder_jugendwerk', 150_000, 46),
        posten('zuschuesse_kindertageseinrichtungen', 50_000, 46),
        posten('sozialleistungen', 491_000, 46),
        posten('ohne_wert', null, null),
      ],
      null,
      46,
    ),
    kita_zuschuesse: tabelle(
      'kita_zuschuesse',
      [posten('kita_a', 20_000, 46), posten('kita_b', 30_000, 46)],
      50_000,
      46,
    ),
    zuschuesse_lfd_zwecke: tabelle(
      'zuschuesse_lfd_zwecke',
      [posten('verein_a', 7_000, 47), posten('verein_b', 5_000, 47), posten('verein_c', null, 47)],
      12_000,
      48,
    ),
  }

  it('liefert die Kita-Einrichtungen einzeln mit Gesamtzeile und Seiten', async () => {
    const modul = await ladeMit(OSTBEVERN_ARTIG)
    const kita = modul.kitaZuschuesse()
    expect(kita?.posten.map((p) => [p.schluessel, p.wert, p.pdfSeite])).toEqual([
      ['kita_a', 20_000, 46],
      ['kita_b', 30_000, 46],
    ])
    expect(kita?.gesamt).toBe(50_000)
    expect(summe(kita?.posten ?? [])).toBe(kita?.gesamt)
    expect(kita?.pdfSeiten).toEqual([46])
    for (const p of kita?.posten ?? []) {
      expect(p.beleg).toBe(`vb:kita_zuschuesse:${p.schluessel}`)
    }
  })

  it('führt Kinder- und Jugendwerk und OGS in fester Reihenfolge, lfdZwecke mit Gesamtzeile', async () => {
    const modul = await ladeMit(OSTBEVERN_ARTIG)
    const { transfer, lfdZwecke } = modul.weitereZuschuesse()
    expect(transfer.posten.map((p) => [p.schluessel, p.wert])).toEqual([
      ['zuschuss_kinder_jugendwerk', 150_000],
      ['zuschuss_ogs', 90_000],
    ])
    expect(transfer.pdfSeiten).toEqual([46])
    expect(modul.zusammen(transfer)).toEqual({ wert: 240_000, berechnet: true })
    // Ein Posten ohne Wert bleibt null (nie 0); die Seite der Gesamtzeile zählt mit.
    expect(lfdZwecke?.posten.map((p) => p.wert)).toEqual([7_000, 5_000, null])
    expect(lfdZwecke?.gesamt).toBe(12_000)
    expect(lfdZwecke?.pdfSeiten).toEqual([47, 48])
  })

  it('nimmt die Sozialleistungen aus dem Posten „sozialleistungen“', async () => {
    const modul = await ladeMit(OSTBEVERN_ARTIG)
    const kachel = modul
      .nichtBeeinflussbar()
      .posten.find((p) => p.name === modul.SOZIALLEISTUNGEN_BEZEICHNUNG)
    expect(kachel?.schluessel).toBe('sozialleistungen')
    expect(kachel?.wert).toBe(491_000)
  })

  it('wirft, wenn keiner oder beide Sozialleistungs-Posten stehen', async () => {
    const ohne = await ladeMit({
      transferaufwendungen: tabelle('transferaufwendungen', [posten('x', 1, 1)], null, 1),
    })
    expect(() => ohne.nichtBeeinflussbar()).toThrow(/sozialleistungen/)
    const beide = await ladeMit({
      transferaufwendungen: tabelle(
        'transferaufwendungen',
        [posten('sozialleistungen', 1, 1), posten('sozialtransferaufwendungen', 2, 1)],
        null,
        1,
      ),
    })
    expect(() => beide.nichtBeeinflussbar()).toThrow(/sozialtransferaufwendungen/)
  })

  it('lässt Sozialleistungen mit dem Wert 0 als Kachel weg', async () => {
    const modul = await ladeMit({
      transferaufwendungen: tabelle(
        'transferaufwendungen',
        [posten('sozialtransferaufwendungen', 0, 33)],
        null,
        33,
      ),
    })
    const namen = modul.nichtBeeinflussbar().posten.map((p) => p.name)
    expect(namen).not.toContain(modul.SOZIALLEISTUNGEN_BEZEICHNUNG)
    expect(namen.length).toBeGreaterThan(0)
  })
})
