<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

import ErklaerText from '@/components/ErklaerText.vue'
import { findeText, rendereAbsatz } from '@/lib/texte'

type Variante = 'ausgaben' | 'einnahmen' | 'kurz'

const props = defineProps<{
  variante: Variante
}>()

// Die Leitsätze sind geprüfte Pipeline-Texte je Variante (`nicht_im_haushalt_{variante}`),
// denn was außerhalb des Haushalts steht (eigene Gesellschaften, Eigenbetriebe), ist je Kommune
// verschieden. Sie nennen keine Zahl; Beträge stehen nur
// im ausführlichen Text `nicht_im_haushalt`, mit PDF-Seite (UI-05, D-18).
function leitsatzFuer(variante: Variante): string {
  const text = findeText(`nicht_im_haushalt_${variante}`)
  if (text === undefined) {
    throw new Error(`Erklärtext nicht_im_haushalt_${variante} fehlt in texte.json`)
  }
  return text.absaetze.map((absatz) => rendereAbsatz(absatz)).join(' ')
}

const GLOSSAR_ZIEL: RouteLocationRaw = { name: 'glossar', hash: '#nicht_im_haushalt' }

const leitsatz = computed(() => leitsatzFuer(props.variante))
const istKurz = computed(() => props.variante === 'kurz')
// Fehlt der Pipeline-Text, entfällt nur der Aufklapper; der Leitsatz bleibt (UI-SPEC E11 empty).
const erklaerung = computed(() => findeText('nicht_im_haushalt'))
const hatErklaerung = computed(() => erklaerung.value !== undefined)
</script>

<template>
  <section class="om-hinweis" aria-labelledby="om-nicht-im-haushalt-titel">
    <wa-callout variant="neutral" class="om-hinweis__callout">
      <wa-icon slot="icon" name="circle-info"></wa-icon>
      <h2 id="om-nicht-im-haushalt-titel" class="om-hinweis__titel">Was nicht im Haushalt steht</h2>
      <p class="om-hinweis__leitsatz">{{ leitsatz }}</p>
      <p v-if="istKurz" class="om-hinweis__link">
        <RouterLink :to="GLOSSAR_ZIEL">Mehr dazu im Glossar</RouterLink>
      </p>
      <wa-details
        v-else-if="hatErklaerung"
        :summary="erklaerung?.titel ?? ''"
        class="om-hinweis__details"
      >
        <ErklaerText schluessel="nicht_im_haushalt" :ueberschrift="false" />
      </wa-details>
    </wa-callout>
  </section>
</template>

<style scoped>
.om-hinweis {
  margin-block-start: var(--wa-space-xl);
  min-width: 0;
}

.om-hinweis__callout {
  display: block;
  width: 100%;
}

.om-hinweis__titel {
  margin: 0 0 var(--wa-space-s);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-hinweis__leitsatz,
.om-hinweis__link {
  margin: 0 0 var(--wa-space-s);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-hinweis__details {
  margin-block-start: var(--wa-space-s);
}
</style>
