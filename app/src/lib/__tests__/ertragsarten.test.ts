import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { baueErtragsarten } from '@/lib/ertragsarten'

const GESAMT = haushalt.ergebnisplan.GESAMT

describe('baueErtragsarten', () => {
  it.each(haushalt.jahre.map((j, i) => [j, i] as const))(
    'Jahr %i: Summe der Werte entspricht berechnet.ertraege, absteigend, ohne Nullwerte, Anteile = 100 %%',
    (_jahr, i) => {
      expect(GESAMT).toBeDefined()
      const reihen = baueErtragsarten(i)
      expect(reihen.length).toBeGreaterThan(0)

      // Ist-Ergebnisse sind mit Cent gedruckt und je Wert auf Euro gerundet; die Summe der
      // gerundeten Zeilen weicht dann um wenige Euro ab (befunde.md, Cent-Rundung). Plan-
      // und Ansatzwerte sind eurogenau.
      const toleranz = haushalt.wertarten[i] === 'ergebnis' ? 2 : 0
      const summeWerte = reihen.reduce((s, r) => s + r.wert, 0)
      expect(Math.abs(summeWerte - GESAMT!.berechnet.ertraege[i]!)).toBeLessThanOrEqual(toleranz)

      for (const r of reihen) {
        expect(r.wert, r.schluessel).not.toBe(0)
        expect(r.name.length, r.schluessel).toBeGreaterThan(0)
      }
      for (let k = 1; k < reihen.length; k++) {
        expect(reihen[k - 1]!.wert).toBeGreaterThanOrEqual(reihen[k]!.wert)
      }

      const summeAnteile = reihen.reduce((s, r) => s + r.anteil, 0)
      expect(Math.abs(summeAnteile - 1)).toBeLessThanOrEqual(0.001)
    },
  )
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Ertragsarten Haushalt 2026', () => {
  // Gesamtergebnisplan S. 79: Zeilen 01–07 und 19 sind 2026 belegt, 08/09 sind 0.
  it('2026 liefert 8 Zeilen, größte Zeile sind die Steuern', () => {
    const reihen = baueErtragsarten(haushalt.jahre.indexOf(2026))
    expect(reihen).toHaveLength(8)
    expect(reihen[0]?.schluessel).toBe('steuern')
    expect(reihen[0]?.wert).toBe(34214000)
  })

  // 2024 kommen aktivierte Eigenleistungen (Zeile 08, 23.700 €) hinzu.
  it('2024 liefert 9 Zeilen', () => {
    const reihen = baueErtragsarten(haushalt.jahre.indexOf(2024))
    expect(reihen).toHaveLength(9)
    expect(reihen.find((r) => r.schluessel === 'aktivierte_eigenleistungen')?.wert).toBe(23700)
  })
})
