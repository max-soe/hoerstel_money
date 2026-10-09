import { afterEach, describe, expect, it, vi } from 'vitest'

import { haushalt, investitionen, produkte } from '@/data/daten'
import type { Grundzahl, HaushaltBezugsgroesse, Produkt } from '@/data/typen'
import { proKopf } from '@/lib/berechnung'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import {
  BEZUGSGROESSEN,
  baueErlaeuterungen,
  baueGrundzahlen,
  baueInvestitionenTabelle,
  baueProduktInvestitionen,
  baueProduktKopf,
  baueTeilergebnisplan,
  bindungsgradText,
  jahrSchluessel,
} from '@/lib/produkt'
import { belegSchluessel, findeBeleg } from '@/lib/quelle'
import { zeilenName } from '@/lib/zeilen'

// Alle Testdaten kommen aus den App-Daten, nicht aus Literalen.
const erstes = produkte[0]

describe('Testdaten', () => {
  it('enthalten genau die Produkte (Ebene P) des Haushalts', () => {
    const codes = haushalt.knoten.filter((k) => k.ebene === 'P').map((k) => k.code)
    expect(produkte.map((p) => p.code).sort()).toEqual([...codes].sort())
    expect(erstes).toBeDefined()
  })

  it.runIf(haushalt.haushaltsjahr === 2026)('Hörstel 2026: 69 Produkte', () => {
    expect(produkte).toHaveLength(69)
  })
})

describe('bindungsgradText', () => {
  it('schreibt die drei Werte der Pipeline aus', () => {
    expect(bindungsgradText('pflichtig')).toBe('pflichtig')
    expect(bindungsgradText('freiwillig')).toBe('freiwillig')
    expect(bindungsgradText('teils')).toBe('teils pflichtig, teils freiwillig')
  })

  it('gibt einen unbekannten Wert unverändert zurück', () => {
    expect(bindungsgradText('unklar')).toBe('unklar')
  })

  it('löst Prototyp-Schlüssel nicht auf', () => {
    expect(bindungsgradText('__proto__')).toBe('__proto__')
    expect(bindungsgradText('constructor')).toBe('constructor')
  })
})

describe('baueProduktKopf (D-09)', () => {
  it.each(produkte.map((p) => p.code))('baut den Kopf von Produkt %s', (code) => {
    const kopf = baueProduktKopf(code)
    expect(kopf).not.toBeNull()
    if (kopf === null) {
      return
    }
    expect(kopf.produkt.code).toBe(code)
    expect(kopf.pbName).toBe(haushalt.knoten.find((k) => k.code === kopf.produkt.pb)?.name)
    expect(kopf.pgName).toBe(haushalt.knoten.find((k) => k.code === kopf.produkt.pg)?.name)
    expect(kopf.pbName).not.toBe('')
    expect(kopf.pgName).not.toBe('')
    expect(kopf.quelleSeite).toBe(kopf.produkt.pdf_seiten[0])
  })

  it('führt ohne gemerkten Zustand zur Produktgruppe des Produkts', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '')
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
    expect(kopf?.zurueckText).toBe(kopf?.pgName)
  })

  it('behält Modus, Aufgabenbereich und Produktgruppe aus einer gültigen Query', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', {
      modus: 'zuschussbedarf',
      pb: erstes?.pb,
      pg: erstes?.pg,
    })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { modus: 'zuschussbedarf', pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it('benennt den Aufgabenbereich, wenn die gemerkte Query keine Produktgruppe trägt', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', { pb: erstes?.pb })
    expect(kopf?.zurueck).toEqual({ name: 'ausgaben', query: { pb: erstes?.pb } })
    expect(kopf?.zurueckText).toBe(kopf?.pbName)
  })

  it('verwirft eine gemerkte Query, die zu einem anderen Aufgabenbereich gehört', () => {
    const fremd = haushalt.knoten.find(
      (k) => k.eltern === 'GESAMT' && k.code !== erstes?.pb && k.code !== 'KL',
    )
    expect(fremd).toBeDefined()
    const kopf = baueProduktKopf(erstes?.code ?? '', { pb: fremd?.code })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it('verwirft unbrauchbare Query-Werte, ohne sie weiterzureichen', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', {
      modus: '<script>',
      pb: '__proto__',
      pg: ['x'],
    })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it.each(['__proto__', 'constructor', 'toString', 'GESAMT', '999999', ''])(
    'liefert für den Code %j kein Produkt',
    (code) => {
      expect(baueProduktKopf(code)).toBeNull()
    },
  )

  it('schreibt den Bindungsgrad aus und nennt nur ein abweichendes Original', () => {
    for (const produkt of produkte) {
      const kopf = baueProduktKopf(produkt.code)
      expect(kopf?.bindungsgrad).toBe(
        produkt.bindungsgrad === null ? null : bindungsgradText(produkt.bindungsgrad),
      )
      if (kopf?.bindungsgradOriginal !== null) {
        expect(kopf?.bindungsgradOriginal).toBe(produkt.bindungsgrad_original)
      }
    }
  })

  it('zeigt ohne Bindungsgrad im Plan weder Text noch Original (Hörstel: keinem Produkt zugeordnet)', () => {
    const ohne = produkte.filter((p) => p.bindungsgrad === null)
    for (const produkt of ohne) {
      const kopf = baueProduktKopf(produkt.code)
      expect(kopf?.bindungsgrad).toBeNull()
      expect(kopf?.bindungsgradOriginal).toBeNull()
    }
    if (haushalt.haushaltsjahr === 2026) {
      expect(ohne).toHaveLength(produkte.length)
    }
  })
})

const einwohner = haushalt.meta.einwohner.wert
const ERLAUBTE_PRODUKT_FELDER: ReadonlySet<string> = new Set([
  'code',
  'name',
  'pb',
  'pg',
  'fachbereich',
  'gremium',
  'beschreibung',
  'leistungen',
  'auftragsgrundlage',
  'bindungsgrad',
  'bindungsgrad_original',
  'klassifizierung',
  'zielgruppe',
  'ziele',
  'erlaeuterungen',
  'pdf_seiten',
  'grundzahlen',
])
const SUMMENZEILEN = ['ordentliche_ertraege', 'ordentliche_aufwendungen', 'jahresergebnis']

function ergebnisplanVon(code: string) {
  const werte = haushalt.ergebnisplan[code]
  if (werte === undefined) {
    throw new Error(`Kein Ergebnisplan für ${code}`)
  }
  return werte
}

describe('baueTeilergebnisplan (AUSG-05, D-23)', () => {
  it('beschriftet die Spalten mit Wertart und Jahr aus den Daten', () => {
    const plan = baueTeilergebnisplan(erstes?.code ?? '')
    const erwartet = haushalt.jahre.map((j) => `${wertartName(wertartFuerJahr(j))} ${j}`)
    expect(plan?.spalten.slice(1, -1).map((s) => s.titel)).toEqual(erwartet)
    expect(plan?.spalten[0]?.art).toBe('text')
    expect(plan?.spalten.slice(1, -1).every((s) => s.art === 'euro')).toBe(true)
    const erstesJahr = haushalt.jahre[0]
    const letztesJahr = haushalt.jahre.at(-1)
    expect(plan?.titel).toBe(`Teilergebnisplan ${erstesJahr}–${letztesJahr}`)
  })

  it('liefert für unbekannte Codes null', () => {
    expect(baueTeilergebnisplan('__proto__')).toBeNull()
    expect(baueTeilergebnisplan('999999')).toBeNull()
  })

  it.each(produkte.map((p) => p.code))(
    'zeigt für %s jede Zeile mit Wert, die Summen und stimmt mit dem Ergebnisplan überein',
    (code) => {
      const plan = baueTeilergebnisplan(code)
      const werte = ergebnisplanVon(code)
      expect(plan).not.toBeNull()
      const zeilen = plan?.zeilen ?? []
      const einfache = zeilen.filter((z) => z.etikett === null)
      const gezeigt = einfache.map((z) => z.schluessel)

      for (const [schluessel, reihe] of Object.entries(werte.zeilen)) {
        const hatWert = reihe.some((wert) => wert !== 0)
        const istSumme = SUMMENZEILEN.includes(schluessel)
        expect(gezeigt.includes(schluessel)).toBe(hatWert || istSumme)
      }
      for (const zeile of einfache) {
        const reihe = werte.zeilen[String(zeile.schluessel)]
        expect(zeile.name).toBe(zeilenName('ergebnisplan', String(zeile.schluessel)))
        haushalt.jahre.forEach((j, i) => {
          expect(zeile[jahrSchluessel(j)]).toBe(reihe?.[i])
        })
      }
    },
  )

  it.each(produkte.map((p) => p.code))(
    'hängt für %s die berechneten Zeilen mit Etikett an',
    (code) => {
      const plan = baueTeilergebnisplan(code)
      const werte = ergebnisplanVon(code)
      const berechnet = (plan?.zeilen ?? []).filter((z) => z.etikett === 'berechnet')
      expect(berechnet.map((z) => z.schluessel)).toEqual([
        'zuschussbedarf',
        'zuschussbedarf_je_einwohner',
      ])
      expect(berechnet.map((z) => z.name)).toEqual([
        'Zuschussbedarf (berechnet)',
        'Zuschussbedarf je Einwohner (berechnet)',
      ])
      haushalt.jahre.forEach((j, i) => {
        const zuschuss = werte.berechnet.zuschussbedarf[i] ?? Number.NaN
        expect(berechnet[0]?.[jahrSchluessel(j)]).toBe(zuschuss)
        expect(berechnet[1]?.[jahrSchluessel(j)]).toBe(proKopf(zuschuss, Number(einwohner)))
      })
    },
  )
})

/** Bezugsgrößen, deren Produkt es im Jahrgang gibt (Hörstel 2026: keine, siehe unten). */
const ANWENDBARE_BEZUGSGROESSEN = BEZUGSGROESSEN.filter((b) =>
  produkte.some((p) => p.code === b.produkt),
)

describe('BEZUGSGROESSEN (Freigabe 05-03, Open Question 6)', () => {
  it('nennt je Bezugsgröße mindestens eine Grundzahl und eine Einheit', () => {
    for (const bezug of BEZUGSGROESSEN) {
      expect(bezug.bezeichnungen.length).toBeGreaterThan(0)
      expect(bezug.einheitText).not.toBe('')
    }
  })

  it('nennt für jedes vorhandene Produkt Grundzahlen, die im Produkt genau einmal vorkommen', () => {
    for (const bezug of ANWENDBARE_BEZUGSGROESSEN) {
      const produkt = produkte.find((p) => p.code === bezug.produkt)
      for (const bezeichnung of bezug.bezeichnungen) {
        expect(
          produkt?.grundzahlen.filter((g) => g.bezeichnung === bezeichnung),
          `${bezug.produkt}: ${bezeichnung}`,
        ).toHaveLength(1)
      }
    }
  })

  it.runIf(haushalt.haushaltsjahr === 2026)(
    'Hörstel 2026: keine freigegebene Bezugsgröße trifft ein Produkt (Kennzahlen „je …“ sind gedruckt)',
    () => {
      expect(ANWENDBARE_BEZUGSGROESSEN).toEqual([])
    },
  )
})

/** Was die Prüfung von „Zuschussbedarf je Einheit“ braucht: echte oder synthetische Daten. */
interface ZuschussQuelle {
  baueGrundzahlen: typeof baueGrundzahlen
  produkte: readonly Produkt[]
  ergebnisplan: typeof haushalt.ergebnisplan
  jahre: readonly number[]
}

/** Prüft die Zeile „Zuschussbedarf je {Einheit} (berechnet)“ einer Bezugsgröße. */
function pruefeZuschussJeEinheit(
  quelle: ZuschussQuelle,
  bezug: (typeof BEZUGSGROESSEN)[number],
): void {
  const produkt = quelle.produkte.find((p) => p.code === bezug.produkt)
  const zuschuss = quelle.ergebnisplan[bezug.produkt]?.berechnet.zuschussbedarf ?? []
  const tabelle = quelle.baueGrundzahlen(bezug.produkt)
  const zeile = tabelle?.zeilen.find((z) => z.etikett === 'berechnet')
  expect(zeile?.name).toBe(`Zuschussbedarf je ${bezug.einheitText} (berechnet)`)
  const jahrSpalten = tabelle?.spalten.slice(2, -1) ?? []
  for (const spalte of jahrSpalten) {
    const j = Number(spalte.schluessel.slice(1))
    const planIndex = quelle.jahre.indexOf(j)
    const teile = bezug.bezeichnungen.map((bezeichnung) =>
      produkt?.grundzahlen
        .find((g) => g.bezeichnung === bezeichnung)
        ?.werte.find((w) => w.jahr === j),
    )
    const wert = zeile?.[spalte.schluessel]
    if (planIndex < 0 || teile.some((t) => t === undefined)) {
      expect(wert).toBeNull()
    } else {
      const summe = teile.reduce((gesamt, t) => gesamt + (t?.wert ?? 0), 0)
      expect(wert).toBe(Math.round((zuschuss[planIndex] ?? Number.NaN) / summe))
    }
  }
  // Mindestens ein Jahr hat beide Werte.
  expect(jahrSpalten.some((s) => zeile?.[s.schluessel] !== null)).toBe(true)
}

describe('baueGrundzahlen (AUSG-05)', () => {
  it('liefert null für Produkte ohne Grundzahlen und unbekannte Codes', () => {
    const ohne = produkte.filter((p) => p.grundzahlen.length === 0)
    for (const produkt of ohne) {
      expect(baueGrundzahlen(produkt.code)).toBeNull()
    }
    expect(baueGrundzahlen('__proto__')).toBeNull()
    expect(baueGrundzahlen('999999')).toBeNull()
  })

  it.runIf(haushalt.haushaltsjahr === 2026)(
    'Hörstel 2026: jedes Produkt druckt Grundzahlen',
    () => {
      expect(produkte.filter((p) => p.grundzahlen.length === 0)).toEqual([])
    },
  )

  it.each(produkte.filter((p) => p.grundzahlen.length > 0).map((p) => p.code))(
    'zeigt für %s jede Grundzahl mit ihren Werten und nur freigegebene Je-Einheit-Zeilen',
    (code) => {
      const tabelle = baueGrundzahlen(code)
      const produkt = produkte.find((p) => p.code === code)
      expect(tabelle).not.toBeNull()
      const zeilen = tabelle?.zeilen ?? []
      const einfache = zeilen.filter((z) => z.etikett === null)
      const berechnet = zeilen.filter((z) => z.etikett === 'berechnet')

      expect(einfache).toHaveLength(produkt?.grundzahlen.length ?? -1)
      produkt?.grundzahlen.forEach((grundzahl, index) => {
        const zeile = einfache[index]
        expect(zeile?.einheit).toBe(grundzahl.einheit)
        for (const wert of grundzahl.werte) {
          expect(zeile?.[jahrSchluessel(wert.jahr)]).toBe(wert.wert)
        }
      })

      // Gedruckte Grundzahlen dürfen selbst „Zuschussbedarf je …“ heißen (Hörstel 0842403
      // Hallenbad Riesenbeck); berechnet sind nur die Zeilen mit Etikett.
      const freigegeben = BEZUGSGROESSEN.filter((b) => b.produkt === code)
      expect(berechnet).toHaveLength(freigegeben.length)
      expect(berechnet.filter((z) => String(z.name).includes('Zuschussbedarf je'))).toHaveLength(
        freigegeben.length,
      )
    },
  )

  it('wählt dezimale Spalten genau dann, wenn eine Grundzahl Nachkommastellen hat', () => {
    for (const produkt of produkte.filter((p) => p.grundzahlen.length > 0)) {
      const mitKomma = produkt.grundzahlen.some((g) => g.nachkommastellen > 0)
      const jahrSpalten = baueGrundzahlen(produkt.code)?.spalten.slice(2, -1) ?? []
      expect(jahrSpalten.length).toBeGreaterThan(0)
      expect(jahrSpalten.every((s) => s.art === (mitKomma ? 'dezimal' : 'zahl'))).toBe(true)
    }
    expect(produkte.some((p) => p.grundzahlen.some((g) => g.nachkommastellen > 0))).toBe(true)
  })

  it('rechnet Zuschussbedarf je Einheit nur für Jahre mit beiden Werten', () => {
    for (const bezug of ANWENDBARE_BEZUGSGROESSEN) {
      pruefeZuschussJeEinheit(
        { baueGrundzahlen, produkte, ergebnisplan: haushalt.ergebnisplan, jahre: haushalt.jahre },
        bezug,
      )
    }
  })

  it('fasst die Hinweise der Grundzahlen als Fußnote zusammen', () => {
    const tabelle = baueGrundzahlen(erstes?.code ?? '')
    const hinweise = new Set(
      erstes?.grundzahlen.flatMap((g) => g.werte.map((w) => w.hinweis).filter((h) => h !== null)) ??
        [],
    )
    expect(hinweise.size).toBeGreaterThan(0)
    for (const hinweis of hinweise) {
      expect(tabelle?.fussnote).toContain(hinweis)
    }
  })
})

describe('baueProduktInvestitionen (AUSG-05)', () => {
  it('liefert genau die Maßnahmen mit dem Produktcode', () => {
    for (const produkt of produkte) {
      const liste = baueProduktInvestitionen(produkt.code)
      expect(liste).toEqual(investitionen.massnahmen.filter((m) => m.produkt === produkt.code))
    }
  })

  it('verteilt alle Maßnahmen auf Produkte und lässt andere Produkte leer', () => {
    const gesamt = produkte.reduce((n, p) => n + baueProduktInvestitionen(p.code).length, 0)
    expect(gesamt).toBe(investitionen.massnahmen.length)
    const ohne = produkte.find((p) => baueProduktInvestitionen(p.code).length === 0)
    expect(ohne).toBeDefined()
    expect(baueProduktInvestitionen('__proto__')).toEqual([])
  })

  it('baut die Tabelle mit Jahresspalten und Fehlwerten als null', () => {
    const mit = produkte.find((p) => baueProduktInvestitionen(p.code).length > 0)
    const liste = baueProduktInvestitionen(mit?.code ?? '')
    const tabelle = baueInvestitionenTabelle(liste)
    expect(tabelle.zeilen).toHaveLength(liste.length)
    expect(tabelle.spalten.map((s) => s.titel).slice(0, 3)).toEqual([
      'Maßnahme',
      'Konto',
      'Richtung',
    ])
    liste.forEach((massnahme, index) => {
      expect(tabelle.zeilen[index]?.name).toBe(massnahme.massnahme_name)
      expect(tabelle.zeilen[index]?.konto).toBe(massnahme.konto_name)
      investitionen.jahre.forEach((j, i) => {
        expect(tabelle.zeilen[index]?.[jahrSchluessel(j)]).toBe(massnahme.werte[i] ?? null)
      })
    })
    expect(baueInvestitionenTabelle([]).zeilen).toEqual([])
  })
})

describe('baueErlaeuterungen (AUSG-05)', () => {
  it('liefert für Produkte ohne Erläuterungen und unbekannte Codes eine leere Liste', () => {
    const ohne = produkte.filter((p) => p.erlaeuterungen.length === 0)
    for (const produkt of ohne) {
      expect(baueErlaeuterungen(produkt.code)).toEqual([])
    }
    expect(baueErlaeuterungen('__proto__')).toEqual([])
    expect(baueErlaeuterungen('999999')).toEqual([])
  })

  it.runIf(haushalt.haushaltsjahr === 2026)('Hörstel 2026: jedes Produkt hat Erläuterungen', () => {
    expect(produkte.filter((p) => p.erlaeuterungen.length === 0)).toEqual([])
  })

  it('löst zweistellige Zeilennummern zu gedruckten Zeilennamen auf', () => {
    const mit = produkte.find((p) =>
      p.erlaeuterungen.some((e) => e.zu_zeilen !== null && e.betrag !== null),
    )
    const liste = baueErlaeuterungen(mit?.code ?? '')
    expect(liste).toHaveLength(mit?.erlaeuterungen.length ?? -1)
    mit?.erlaeuterungen.forEach((erlaeuterung, index) => {
      const eintrag = liste[index]
      expect(eintrag?.betrag).toBe(erlaeuterung.betrag)
      expect(eintrag?.text).toBe(erlaeuterung.text)
      const erwartet = (erlaeuterung.zu_zeilen ?? []).map((nummer) => {
        const zeile = haushalt.zeilen_namen.ergebnisplan.find((z) => z.nummer === nummer)
        return zeile?.name
      })
      expect(eintrag?.zeilenNamen).toEqual(erwartet)
      expect(eintrag?.zeilenNamen.every((name) => name !== undefined)).toBe(true)
    })
  })

  it('nennt die Zeilen nur, wenn sie sich vom vorigen Posten unterscheiden', () => {
    for (const produkt of produkte) {
      const liste = baueErlaeuterungen(produkt.code)
      liste.forEach((eintrag, index) => {
        const davor = liste[index - 1]
        const gleich =
          davor !== undefined && davor.zeilenNamen.join('|') === eintrag.zeilenNamen.join('|')
        expect(eintrag.zuAnzeigen).toBe(eintrag.zeilenNamen.length > 0 && !gleich)
      })
    }
  })
})

describe('Probe AUSG-05: alle Produkte', () => {
  it('baut jedes Seitenmodell ohne Fehler', () => {
    for (const produkt of produkte) {
      expect(() => {
        baueProduktKopf(produkt.code)
        baueTeilergebnisplan(produkt.code)
        baueErlaeuterungen(produkt.code)
        baueGrundzahlen(produkt.code)
        baueInvestitionenTabelle(baueProduktInvestitionen(produkt.code))
      }).not.toThrow()
    }
  })

  it('verwendet nur namenfreie Produktfelder (Datenschutz, Phase 3 D-09)', () => {
    for (const produkt of produkte) {
      for (const feld of Object.keys(produkt)) {
        expect(ERLAUBTE_PRODUKT_FELDER.has(feld)).toBe(true)
      }
    }
  })
})

const QUELLE_SPALTE = { schluessel: 'quelle', titel: 'Quelle', art: 'quelle' }

describe('Quelle-Spalte der Produkttabellen (D-01, UI-02)', () => {
  it('der Teilergebnisplan hat als letzte Spalte „Quelle“ mit ep-Schlüsseln je gedruckter Zeile', () => {
    for (const produkt of produkte) {
      const plan = baueTeilergebnisplan(produkt.code)
      expect(plan?.spalten.at(-1)).toEqual(QUELLE_SPALTE)
      for (const zeile of plan?.zeilen ?? []) {
        expect(zeile.quelle).toBe(
          zeile.etikett === 'berechnet'
            ? null
            : belegSchluessel.ep(produkt.code, String(zeile.schluessel)),
        )
      }
    }
  })

  it('die beiden berechneten Zeilen des Teilergebnisplans haben keine Quelle', () => {
    const berechnet = (baueTeilergebnisplan(erstes?.code ?? '')?.zeilen ?? []).filter(
      (zeile) => zeile.etikett === 'berechnet',
    )
    expect(berechnet).toHaveLength(2)
    expect(berechnet.every((zeile) => zeile.quelle === null)).toBe(true)
  })

  it('die Grundzahlen haben als letzte Spalte „Quelle“ mit gz-Schlüsseln, berechnete Zeilen ohne', () => {
    let berechnete = 0
    for (const produkt of produkte.filter((p) => p.grundzahlen.length > 0)) {
      const tabelle = baueGrundzahlen(produkt.code)
      expect(tabelle?.spalten.at(-1)).toEqual(QUELLE_SPALTE)
      const gedruckte = (tabelle?.zeilen ?? []).filter((zeile) => zeile.etikett === null)
      expect(gedruckte.map((zeile) => zeile.quelle)).toEqual(
        produkt.grundzahlen.map((g) => belegSchluessel.gz(produkt.code, g.position)),
      )
      for (const zeile of (tabelle?.zeilen ?? []).filter((z) => z.etikett === 'berechnet')) {
        expect(zeile.quelle).toBeNull()
        berechnete += 1
      }
    }
    expect(berechnete).toBe(ANWENDBARE_BEZUGSGROESSEN.length)
  })

  it('die Investitionen haben als letzte Spalte „Quelle“ mit inv-Schlüsseln', () => {
    let geprueft = 0
    for (const produkt of produkte) {
      const liste = baueProduktInvestitionen(produkt.code)
      const tabelle = baueInvestitionenTabelle(liste)
      expect(tabelle.spalten.at(-1)).toEqual(QUELLE_SPALTE)
      liste.forEach((massnahme, index) => {
        expect(tabelle.zeilen[index]?.quelle).toBe(
          belegSchluessel.inv(
            massnahme.produkt,
            massnahme.massnahme_id,
            massnahme.konto,
            massnahme.richtung,
          ),
        )
        geprueft += 1
      })
    }
    expect(geprueft).toBe(investitionen.massnahmen.length)
  })

  it('jeder Schlüssel einer Tabellenzeile löst auf, außer bei Planzeilen ohne Wert, die das PDF nicht druckt', () => {
    // „Ordentliche Erträge“ und „Ordentliche Aufwendungen“ zeigt der Teilergebnisplan immer; hat
    // ein Produkt keine Erträge (bzw. keine Aufwendungen, Hörstel 1153101 und 1153201), druckt der
    // Haushaltsplan die Zeile nicht und quellen.json hat keinen Beleg (leere Zelle, kein Knopf).
    const ungedruckt: string[] = []
    const unaufgeloest: string[] = []
    for (const produkt of produkte) {
      const werte = ergebnisplanVon(produkt.code)
      const tabellen = [
        baueTeilergebnisplan(produkt.code),
        baueGrundzahlen(produkt.code),
        baueInvestitionenTabelle(baueProduktInvestitionen(produkt.code)),
      ]
      for (const tabelle of tabellen) {
        for (const zeile of tabelle?.zeilen ?? []) {
          const schluessel = zeile.quelle
          if (typeof schluessel !== 'string' || findeBeleg(schluessel) !== null) {
            continue
          }
          const reihe = werte.zeilen[String(zeile.schluessel)]
          if (reihe !== undefined && reihe.every((wert) => wert === 0)) {
            ungedruckt.push(schluessel)
          } else {
            unaufgeloest.push(schluessel)
          }
        }
      }
    }
    expect(unaufgeloest).toEqual([])
    expect(
      ungedruckt.filter(
        (schluessel) =>
          !schluessel.endsWith(':ordentliche_ertraege') &&
          !schluessel.endsWith(':ordentliche_aufwendungen'),
      ),
    ).toEqual([])
  })
})

// ---------------------------------------------------------------------------------------------
// Synthetische Produkte: Bindungsgrad und Bezugsgrößen, die der Hörsteler Plan nicht trägt
// ---------------------------------------------------------------------------------------------

describe('Synthetische Produkte (Bindungsgrad, Bezugsgrößen)', () => {
  afterEach(() => {
    vi.doUnmock('@/data/daten')
    vi.resetModules()
  })

  if (erstes === undefined) {
    throw new Error('Keine Produkte in den Daten')
  }
  const vorlage: Produkt = erstes
  const planVorlage = ergebnisplanVon(vorlage.code)

  /** Ein Produkt auf Basis der Vorlage (gleicher PB/PG, damit die Namen auflösen). */
  function synthetisch(code: string, felder: Partial<Produkt>): Produkt {
    return {
      ...vorlage,
      code,
      bindungsgrad: null,
      bindungsgrad_original: null,
      grundzahlen: [],
      ...felder,
    }
  }

  /** Grundzahl mit Werten je Jahr. */
  function grundzahl(position: number, bezeichnung: string, werte: [number, number][]): Grundzahl {
    return {
      position,
      gruppe: null,
      bezeichnung,
      einheit: null,
      nachkommastellen: 0,
      pdf_seite: 1,
      werte: werte.map(([jahr, wert]) => ({ jahr, wert, hinweis: null })),
    }
  }

  /** Lädt `lib/produkt` neu mit den echten Daten plus den synthetischen Produkten. */
  async function ladeMit(
    zusatz: Produkt[],
    bezugsgroessen: HaushaltBezugsgroesse[] | undefined = undefined,
  ) {
    vi.resetModules()
    vi.doMock('@/data/daten', async (importOriginal) => {
      const echt = await importOriginal<typeof import('@/data/daten')>()
      const plaene = Object.fromEntries(zusatz.map((p) => [p.code, planVorlage]))
      return {
        ...echt,
        produkte: [...echt.produkte, ...zusatz],
        haushalt: {
          ...echt.haushalt,
          ergebnisplan: { ...echt.haushalt.ergebnisplan, ...plaene },
          bezugsgroessen: bezugsgroessen ?? echt.haushalt.bezugsgroessen,
        },
      }
    })
    return import('@/lib/produkt')
  }

  it('nennt ein abweichendes Original des Bindungsgrads, sonst nicht', async () => {
    const modul = await ladeMit([
      synthetisch('S000001', { bindungsgrad: 'pflichtig' }),
      synthetisch('S000002', {
        bindungsgrad: 'teils',
        bindungsgrad_original: 'Teils pflichtig, teils  freiwillig',
      }),
      synthetisch('S000003', {
        bindungsgrad: 'pflichtig',
        bindungsgrad_original: 'pflichtig (Gesetz)',
      }),
      synthetisch('S000004', { bindungsgrad: 'freiwillig', bindungsgrad_original: 'freiwillig' }),
    ])
    expect(modul.baueProduktKopf('S000001')?.bindungsgrad).toBe('pflichtig')
    expect(modul.baueProduktKopf('S000001')?.bindungsgradOriginal).toBeNull()
    expect(modul.baueProduktKopf('S000002')?.bindungsgrad).toBe('teils pflichtig, teils freiwillig')
    expect(modul.baueProduktKopf('S000002')?.bindungsgradOriginal).toBeNull()
    expect(modul.baueProduktKopf('S000003')?.bindungsgrad).toBe('pflichtig')
    expect(modul.baueProduktKopf('S000003')?.bindungsgradOriginal).toBe('pflichtig (Gesetz)')
    expect(modul.baueProduktKopf('S000004')?.bindungsgradOriginal).toBeNull()
  })

  it('rechnet Zuschussbedarf je Einheit nur für Jahre mit beiden Werten', async () => {
    const [erstesJahr, zweitesJahr] = haushalt.jahre
    if (erstesJahr === undefined || zweitesJahr === undefined) {
      throw new Error('Zu wenige Planjahre')
    }
    // Synthetische Bezugsgrößen nach dem Ostbevern-Muster ([layout.bezugsgroessen], eine und
    // zwei Grundzahlen im Nenner); Hörstel führt keine. Je Bezugsgröße ein Produkt mit ihrem
    // Code: die erste Grundzahl hat beide Planjahre und ein Jahr vor dem Plan, weitere
    // Grundzahlen nur das erste Planjahr.
    const bezugsgroessen: HaushaltBezugsgroesse[] = [
      { produkt: 'S100001', einheit_text: 'Schüler/in', bezeichnungen: ['Schüler/innen'] },
      {
        produkt: 'S100002',
        einheit_text: 'betreutem Kind',
        bezeichnungen: ['Betreute Kinder unter 3 Jahre', 'Betreute Kinder von 3 - 6 Jahre'],
      },
    ]
    const zusatz = bezugsgroessen.map((bezug) =>
      synthetisch(bezug.produkt, {
        grundzahlen: bezug.bezeichnungen.map((bezeichnung, index) =>
          grundzahl(
            index + 1,
            bezeichnung,
            index === 0
              ? [
                  [erstesJahr - 1, 40],
                  [erstesJahr, 50],
                  [zweitesJahr, 60],
                ]
              : [[erstesJahr, 25]],
          ),
        ),
      }),
    )
    const modul = await ladeMit(zusatz, bezugsgroessen)
    const echt = await import('@/data/daten')
    expect(modul.BEZUGSGROESSEN.map((b) => b.produkt)).toEqual(['S100001', 'S100002'])
    for (const bezug of modul.BEZUGSGROESSEN) {
      pruefeZuschussJeEinheit(
        {
          baueGrundzahlen: modul.baueGrundzahlen,
          produkte: echt.produkte,
          ergebnisplan: echt.haushalt.ergebnisplan,
          jahre: echt.haushalt.jahre,
        },
        bezug,
      )
      const tabelle = modul.baueGrundzahlen(bezug.produkt)
      const berechnet = tabelle?.zeilen.filter((z) => z.etikett === 'berechnet') ?? []
      expect(berechnet).toHaveLength(1)
      expect(berechnet[0]?.quelle).toBeNull()
      // Das Jahr vor dem Plan hat keinen Zuschussbedarf: kein erfundener Wert.
      expect(berechnet[0]?.[jahrSchluessel(erstesJahr - 1)]).toBeNull()
    }
  })

  it('liefert null für ein Produkt ohne Grundzahlen', async () => {
    const modul = await ladeMit([synthetisch('S000005', { grundzahlen: [] })])
    expect(modul.baueGrundzahlen('S000005')).toBeNull()
    expect(modul.baueProduktKopf('S000005')).not.toBeNull()
  })
})
