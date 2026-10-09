import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'

import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * Setzt Name und Art der Kommune aus `src/data/haushalt.json` (`[layout.kommune]` im Jahrgang)
 * in `index.html` ein (`%OM_SEITENNAME%`, `%OM_KOMMUNE%`), damit kein Ortsname im Code steht.
 */
function kommuneInIndexHtml(): Plugin {
  return {
    name: 'om-kommune-in-index-html',
    transformIndexHtml(html) {
      const pfad = fileURLToPath(new URL('./src/data/haushalt.json', import.meta.url))
      const { kommune } = JSON.parse(readFileSync(pfad, 'utf-8')) as {
        kommune: { name: string; art: string }
      }
      return html
        .replaceAll('%OM_SEITENNAME%', `${kommune.name} Money`)
        .replaceAll('%OM_KOMMUNE%', `${kommune.art} ${kommune.name}`)
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  // Relativer Pfad statt fest codiertem Repo-Namen: GitHub Pages dient
  // Projekt-Seiten unter `https://<account>.github.io/<repo>/`, der endgültige
  // Repo-Name steht noch nicht fest. Mit Hash-Router funktioniert `'./'`
  // sowohl lokal (`npm run dev`) als auch unter jedem Pages-Unterpfad.
  base: './',
  plugins: [
    kommuneInIndexHtml(),
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('wa-'),
        },
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
