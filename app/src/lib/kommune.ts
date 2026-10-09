// Name und Art der Kommune aus den Daten (`haushalt.kommune`, `[layout.kommune]` im Jahrgang):
// Seitentitel, Kopfzeile und Texte nennen die Kommune nur über diese Konstanten, damit kein
// Ortsname im App-Code steht. „Stadt“ und „Gemeinde“ sind beide feminin, deshalb passt
// „der {art}“ / „die {art}“ für beide.

import { haushalt } from '@/data/daten'

const ARTEN = ['Stadt', 'Gemeinde'] as const

if (!(ARTEN as readonly string[]).includes(haushalt.kommune.art)) {
  throw new Error(`haushalt.kommune.art „${haushalt.kommune.art}“ ist unbekannt`)
}

/** Ortsname, z. B. „Hörstel“. */
export const KOMMUNE_NAME = haushalt.kommune.name

/** „Stadt“ oder „Gemeinde“. */
export const KOMMUNE_ART = haushalt.kommune.art

/** Vollständiger Name, z. B. „Stadt Hörstel“. */
export const KOMMUNE_VOLL = `${KOMMUNE_ART} ${KOMMUNE_NAME}`

/** Name der App, z. B. „Hörstel Money“. */
export const SEITENNAME = `${KOMMUNE_NAME} Money`
