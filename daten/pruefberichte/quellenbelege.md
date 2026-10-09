# Quellenbelege – Werte ohne Markierung

Schritt 08 (`pipeline/08_quellenbelege.py`) sucht zu jedem Wert mit PDF-Seite die Zeile
auf der Seite (Beschriftung oder Zeilennummer plus Betrag des Haushaltsjahrs). Ohne genau
einen Treffer bekommt der Beleg kein Rechteck; die App zeigt dann die Seite ohne
Markierung mit einem Hinweis. Diese Datei wird bei jedem Lauf neu geschrieben.

## Überblick

| Art | Belege | ohne Markierung |
|---|---|---|
| ep (Ergebnisplanzeilen) | 1681 | 600 |
| fp (Finanzplanzeilen) | 38 | 1 |
| vb (Vorberichtsposten) | 70 | 39 |
| meta (Meta-Werte) | 9 | 0 |
| gz (Grundzahlen) | 232 | 62 |
| pr (Produktseiten) | 69 | 0 |
| inv (Investitionsmaßnahmen) | 219 | 12 |
| ve (VE-Fälligkeiten) | 15 | 15 |
| sd (Schuldenstand) | 3 | 2 |
| sp (Stellenplan) | 171 | 171 |
| seite (Seitenbelege) | 292 | – |

## ep – Ergebnisplanzeilen

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `ep:01111:abschreibungen` | 116 | berechnet |
| `ep:01111:aktivierte_eigenleistungen` | 116 | berechnet |
| `ep:01111:ergebnis_laufende_verwaltung` | 116 | berechnet |
| `ep:01111:ergebnis_nach_minderaufwand` | 116 | berechnet |
| `ep:01111:jahresergebnis` | 116 | berechnet |
| `ep:01111:kostenerstattungen` | 116 | berechnet |
| `ep:01111:oeffentlich_rechtliche_entgelte` | 116 | berechnet |
| `ep:01111:ordentliche_aufwendungen` | 116 | berechnet |
| `ep:01111:ordentliche_ertraege` | 116 | berechnet |
| `ep:01111:ordentliches_ergebnis` | 116 | berechnet |
| `ep:01111:personalaufwendungen` | 116 | berechnet |
| `ep:01111:privatrechtliche_entgelte` | 116 | berechnet |
| `ep:01111:sach_und_dienstleistungen` | 116 | berechnet |
| `ep:01111:sonstige_ordentliche_aufwendungen` | 116 | berechnet |
| `ep:01111:sonstige_ordentliche_ertraege` | 116 | berechnet |
| `ep:01111:transferaufwendungen` | 116 | berechnet |
| `ep:01111:versorgungsaufwendungen` | 116 | berechnet |
| `ep:01111:zuwendungen` | 116 | berechnet |
| `ep:02121:ergebnis_laufende_verwaltung` | 189 | berechnet |
| `ep:02121:ergebnis_nach_minderaufwand` | 189 | berechnet |
| `ep:02121:jahresergebnis` | 189 | berechnet |
| `ep:02121:ordentliche_aufwendungen` | 189 | berechnet |
| `ep:02121:ordentliche_ertraege` | 189 | berechnet |
| `ep:02121:ordentliches_ergebnis` | 189 | berechnet |
| `ep:02121:personalaufwendungen` | 189 | berechnet |
| `ep:02121:sach_und_dienstleistungen` | 189 | berechnet |
| `ep:02121:sonstige_ordentliche_aufwendungen` | 189 | berechnet |
| `ep:02121:sonstige_ordentliche_ertraege` | 189 | berechnet |
| `ep:02121:zuwendungen` | 189 | berechnet |
| `ep:02122:abschreibungen` | 194 | berechnet |
| `ep:02122:ergebnis_laufende_verwaltung` | 194 | berechnet |
| `ep:02122:ergebnis_nach_minderaufwand` | 194 | berechnet |
| `ep:02122:jahresergebnis` | 194 | berechnet |
| `ep:02122:kostenerstattungen` | 194 | berechnet |
| `ep:02122:oeffentlich_rechtliche_entgelte` | 194 | berechnet |
| `ep:02122:ordentliche_aufwendungen` | 194 | berechnet |
| `ep:02122:ordentliche_ertraege` | 194 | berechnet |
| `ep:02122:ordentliches_ergebnis` | 194 | berechnet |
| `ep:02122:personalaufwendungen` | 194 | berechnet |
| `ep:02122:privatrechtliche_entgelte` | 194 | berechnet |
| `ep:02122:sach_und_dienstleistungen` | 194 | berechnet |
| `ep:02122:sonstige_ordentliche_aufwendungen` | 194 | berechnet |
| `ep:02122:sonstige_ordentliche_ertraege` | 194 | berechnet |
| `ep:02122:zuwendungen` | 194 | berechnet |
| `ep:02126:abschreibungen` | 205 | berechnet |
| `ep:02126:ergebnis_laufende_verwaltung` | 205 | berechnet |
| `ep:02126:ergebnis_nach_minderaufwand` | 205 | berechnet |
| `ep:02126:jahresergebnis` | 205 | berechnet |
| `ep:02126:kostenerstattungen` | 205 | berechnet |
| `ep:02126:oeffentlich_rechtliche_entgelte` | 205 | berechnet |
| `ep:02126:ordentliche_aufwendungen` | 205 | berechnet |
| `ep:02126:ordentliche_ertraege` | 205 | berechnet |
| `ep:02126:ordentliches_ergebnis` | 205 | berechnet |
| `ep:02126:personalaufwendungen` | 205 | berechnet |
| `ep:02126:privatrechtliche_entgelte` | 205 | berechnet |
| `ep:02126:sach_und_dienstleistungen` | 205 | berechnet |
| `ep:02126:sonstige_ordentliche_aufwendungen` | 205 | berechnet |
| `ep:02126:sonstige_ordentliche_ertraege` | 205 | berechnet |
| `ep:02126:transferaufwendungen` | 205 | berechnet |
| `ep:02126:zuwendungen` | 205 | berechnet |
| `ep:03211:abschreibungen` | 217 | berechnet |
| `ep:03211:ergebnis_laufende_verwaltung` | 217 | berechnet |
| `ep:03211:ergebnis_nach_minderaufwand` | 217 | berechnet |
| `ep:03211:jahresergebnis` | 217 | berechnet |
| `ep:03211:kostenerstattungen` | 217 | berechnet |
| `ep:03211:oeffentlich_rechtliche_entgelte` | 217 | berechnet |
| `ep:03211:ordentliche_aufwendungen` | 217 | berechnet |
| `ep:03211:ordentliche_ertraege` | 217 | berechnet |
| `ep:03211:ordentliches_ergebnis` | 217 | berechnet |
| `ep:03211:personalaufwendungen` | 217 | berechnet |
| `ep:03211:privatrechtliche_entgelte` | 217 | berechnet |
| `ep:03211:sach_und_dienstleistungen` | 217 | berechnet |
| `ep:03211:sonstige_ordentliche_aufwendungen` | 217 | berechnet |
| `ep:03211:sonstige_ordentliche_ertraege` | 217 | berechnet |
| `ep:03211:transferaufwendungen` | 217 | berechnet |
| `ep:03211:zuwendungen` | 217 | berechnet |
| `ep:03218:abschreibungen` | 228 | berechnet |
| `ep:03218:ergebnis_laufende_verwaltung` | 228 | berechnet |
| `ep:03218:ergebnis_nach_minderaufwand` | 228 | berechnet |
| `ep:03218:jahresergebnis` | 228 | berechnet |
| `ep:03218:kostenerstattungen` | 228 | berechnet |
| `ep:03218:ordentliche_aufwendungen` | 228 | berechnet |
| `ep:03218:ordentliche_ertraege` | 228 | berechnet |
| `ep:03218:ordentliches_ergebnis` | 228 | berechnet |
| `ep:03218:personalaufwendungen` | 228 | berechnet |
| `ep:03218:privatrechtliche_entgelte` | 228 | berechnet |
| `ep:03218:sach_und_dienstleistungen` | 228 | berechnet |
| `ep:03218:sonstige_ordentliche_aufwendungen` | 228 | berechnet |
| `ep:03218:sonstige_ordentliche_ertraege` | 228 | berechnet |
| `ep:03218:transferaufwendungen` | 228 | berechnet |
| `ep:03218:zuwendungen` | 228 | berechnet |
| `ep:03232:ergebnis_laufende_verwaltung` | 237 | berechnet |
| `ep:03232:ergebnis_nach_minderaufwand` | 237 | berechnet |
| `ep:03232:jahresergebnis` | 237 | berechnet |
| `ep:03232:oeffentlich_rechtliche_entgelte` | 237 | berechnet |
| `ep:03232:ordentliche_aufwendungen` | 237 | berechnet |
| `ep:03232:ordentliche_ertraege` | 237 | berechnet |
| `ep:03232:ordentliches_ergebnis` | 237 | berechnet |
| `ep:03232:personalaufwendungen` | 237 | berechnet |
| `ep:03232:privatrechtliche_entgelte` | 237 | berechnet |
| `ep:03232:sach_und_dienstleistungen` | 237 | berechnet |
| `ep:03232:sonstige_ordentliche_aufwendungen` | 237 | berechnet |
| `ep:03232:sonstige_ordentliche_ertraege` | 237 | berechnet |
| `ep:03232:transferaufwendungen` | 237 | berechnet |
| `ep:03232:zuwendungen` | 237 | berechnet |
| `ep:03241:ergebnis_laufende_verwaltung` | 243 | berechnet |
| `ep:03241:ergebnis_nach_minderaufwand` | 243 | berechnet |
| `ep:03241:jahresergebnis` | 243 | berechnet |
| `ep:03241:ordentliche_aufwendungen` | 243 | berechnet |
| `ep:03241:ordentliche_ertraege` | 243 | berechnet |
| `ep:03241:ordentliches_ergebnis` | 243 | berechnet |
| `ep:03241:personalaufwendungen` | 243 | berechnet |
| `ep:03241:sach_und_dienstleistungen` | 243 | berechnet |
| `ep:03241:sonstige_ordentliche_ertraege` | 243 | berechnet |
| `ep:03241:zuwendungen` | 243 | berechnet |
| `ep:04263:ergebnis_laufende_verwaltung` | 252 | berechnet |
| `ep:04263:ergebnis_nach_minderaufwand` | 252 | berechnet |
| `ep:04263:jahresergebnis` | 252 | berechnet |
| `ep:04263:ordentliche_aufwendungen` | 252 | berechnet |
| `ep:04263:ordentliche_ertraege` | 252 | berechnet |
| `ep:04263:ordentliches_ergebnis` | 252 | berechnet |
| `ep:04263:personalaufwendungen` | 252 | berechnet |
| `ep:04263:sonstige_ordentliche_ertraege` | 252 | berechnet |
| `ep:04263:transferaufwendungen` | 252 | berechnet |
| `ep:04271:ergebnis_laufende_verwaltung` | 256 | berechnet |
| `ep:04271:ergebnis_nach_minderaufwand` | 256 | berechnet |
| `ep:04271:jahresergebnis` | 256 | berechnet |
| `ep:04271:ordentliche_aufwendungen` | 256 | berechnet |
| `ep:04271:ordentliche_ertraege` | 256 | berechnet |
| `ep:04271:ordentliches_ergebnis` | 256 | berechnet |
| `ep:04271:personalaufwendungen` | 256 | berechnet |
| `ep:04271:sonstige_ordentliche_aufwendungen` | 256 | berechnet |
| `ep:04271:sonstige_ordentliche_ertraege` | 256 | berechnet |
| `ep:04271:transferaufwendungen` | 256 | berechnet |
| `ep:04272:ergebnis_laufende_verwaltung` | 260 | berechnet |
| `ep:04272:ergebnis_nach_minderaufwand` | 260 | berechnet |
| `ep:04272:jahresergebnis` | 260 | berechnet |
| `ep:04272:ordentliche_aufwendungen` | 260 | berechnet |
| `ep:04272:ordentliche_ertraege` | 260 | berechnet |
| `ep:04272:ordentliches_ergebnis` | 260 | berechnet |
| `ep:04272:personalaufwendungen` | 260 | berechnet |
| `ep:04272:sonstige_ordentliche_ertraege` | 260 | berechnet |
| `ep:04272:transferaufwendungen` | 260 | berechnet |
| `ep:04281:abschreibungen` | 264 | berechnet |
| `ep:04281:ergebnis_laufende_verwaltung` | 264 | berechnet |
| `ep:04281:ergebnis_nach_minderaufwand` | 264 | berechnet |
| `ep:04281:jahresergebnis` | 264 | berechnet |
| `ep:04281:kostenerstattungen` | 264 | berechnet |
| `ep:04281:ordentliche_aufwendungen` | 264 | berechnet |
| `ep:04281:ordentliche_ertraege` | 264 | berechnet |
| `ep:04281:ordentliches_ergebnis` | 264 | berechnet |
| `ep:04281:personalaufwendungen` | 264 | berechnet |
| `ep:04281:privatrechtliche_entgelte` | 264 | berechnet |
| `ep:04281:sach_und_dienstleistungen` | 264 | berechnet |
| `ep:04281:sonstige_ordentliche_aufwendungen` | 264 | berechnet |
| `ep:04281:sonstige_ordentliche_ertraege` | 264 | berechnet |
| `ep:04281:transferaufwendungen` | 264 | berechnet |
| `ep:04281:zuwendungen` | 264 | berechnet |
| `ep:0531201:ordentliche_aufwendungen` | 280 | mehrdeutig |
| `ep:05312:ergebnis_laufende_verwaltung` | 279 | berechnet |
| `ep:05312:ergebnis_nach_minderaufwand` | 279 | berechnet |
| `ep:05312:jahresergebnis` | 279 | berechnet |
| `ep:05312:ordentliche_aufwendungen` | 279 | berechnet |
| `ep:05312:ordentliche_ertraege` | 279 | berechnet |
| `ep:05312:ordentliches_ergebnis` | 279 | berechnet |
| `ep:05312:personalaufwendungen` | 279 | berechnet |
| `ep:05312:sonstige_ordentliche_aufwendungen` | 279 | berechnet |
| `ep:05312:sonstige_ordentliche_ertraege` | 279 | berechnet |
| `ep:05312:zuwendungen` | 279 | berechnet |
| `ep:05313:ergebnis_laufende_verwaltung` | 284 | berechnet |
| `ep:05313:ergebnis_nach_minderaufwand` | 284 | berechnet |
| `ep:05313:jahresergebnis` | 284 | berechnet |
| `ep:05313:ordentliche_aufwendungen` | 284 | berechnet |
| `ep:05313:ordentliche_ertraege` | 284 | berechnet |
| `ep:05313:ordentliches_ergebnis` | 284 | berechnet |
| `ep:05313:personalaufwendungen` | 284 | berechnet |
| `ep:05313:sach_und_dienstleistungen` | 284 | berechnet |
| `ep:05313:sonstige_ordentliche_aufwendungen` | 284 | berechnet |
| `ep:05313:sonstige_ordentliche_ertraege` | 284 | berechnet |
| `ep:05313:sonstige_transferertraege` | 284 | berechnet |
| `ep:05313:transferaufwendungen` | 284 | berechnet |
| `ep:05313:zuwendungen` | 284 | berechnet |
| `ep:05316:ergebnis_laufende_verwaltung` | 290 | berechnet |
| `ep:05316:ergebnis_nach_minderaufwand` | 290 | berechnet |
| `ep:05316:jahresergebnis` | 290 | berechnet |
| `ep:05316:ordentliche_aufwendungen` | 290 | berechnet |
| `ep:05316:ordentliche_ertraege` | 290 | berechnet |
| `ep:05316:ordentliches_ergebnis` | 290 | berechnet |
| `ep:05316:personalaufwendungen` | 290 | berechnet |
| `ep:05316:sonstige_ordentliche_aufwendungen` | 290 | berechnet |
| `ep:05316:sonstige_ordentliche_ertraege` | 290 | berechnet |
| `ep:05316:transferaufwendungen` | 290 | berechnet |
| `ep:05316:zuwendungen` | 290 | berechnet |
| `ep:05317:ergebnis_laufende_verwaltung` | 295 | berechnet |
| `ep:05317:ergebnis_nach_minderaufwand` | 295 | berechnet |
| `ep:05317:jahresergebnis` | 295 | berechnet |
| `ep:05317:ordentliche_aufwendungen` | 295 | berechnet |
| `ep:05317:ordentliche_ertraege` | 295 | berechnet |
| `ep:05317:ordentliches_ergebnis` | 295 | berechnet |
| `ep:05317:personalaufwendungen` | 295 | berechnet |
| `ep:05317:sonstige_ordentliche_ertraege` | 295 | berechnet |
| `ep:05317:zuwendungen` | 295 | berechnet |
| `ep:05318:ergebnis_laufende_verwaltung` | 299 | berechnet |
| `ep:05318:ergebnis_nach_minderaufwand` | 299 | berechnet |
| `ep:05318:jahresergebnis` | 299 | berechnet |
| `ep:05318:ordentliche_aufwendungen` | 299 | berechnet |
| `ep:05318:ordentliche_ertraege` | 299 | berechnet |
| `ep:05318:ordentliches_ergebnis` | 299 | berechnet |
| `ep:05318:personalaufwendungen` | 299 | berechnet |
| `ep:05318:sonstige_ordentliche_aufwendungen` | 299 | berechnet |
| `ep:05318:sonstige_ordentliche_ertraege` | 299 | berechnet |
| `ep:05318:zuwendungen` | 299 | berechnet |
| `ep:05333:ergebnis_laufende_verwaltung` | 304 | berechnet |
| `ep:05333:ergebnis_nach_minderaufwand` | 304 | berechnet |
| `ep:05333:jahresergebnis` | 304 | berechnet |
| `ep:05333:ordentliche_aufwendungen` | 304 | berechnet |
| `ep:05333:ordentliche_ertraege` | 304 | berechnet |
| `ep:05333:ordentliches_ergebnis` | 304 | berechnet |
| `ep:05333:personalaufwendungen` | 304 | berechnet |
| `ep:05333:sonstige_ordentliche_aufwendungen` | 304 | berechnet |
| `ep:05333:sonstige_ordentliche_ertraege` | 304 | berechnet |
| `ep:05345:ergebnis_laufende_verwaltung` | 308 | berechnet |
| `ep:05345:ergebnis_nach_minderaufwand` | 308 | berechnet |
| `ep:05345:jahresergebnis` | 308 | berechnet |
| `ep:05345:ordentliche_aufwendungen` | 308 | berechnet |
| `ep:05345:ordentliche_ertraege` | 308 | berechnet |
| `ep:05345:ordentliches_ergebnis` | 308 | berechnet |
| `ep:05345:personalaufwendungen` | 308 | berechnet |
| `ep:05345:sonstige_ordentliche_aufwendungen` | 308 | berechnet |
| `ep:05345:sonstige_ordentliche_ertraege` | 308 | berechnet |
| `ep:0535101:ergebnis_nach_minderaufwand` | 313 | mehrdeutig |
| `ep:0535101:ordentliche_aufwendungen` | 313 | mehrdeutig |
| `ep:05351:ergebnis_laufende_verwaltung` | 312 | berechnet |
| `ep:05351:ergebnis_nach_minderaufwand` | 312 | berechnet |
| `ep:05351:jahresergebnis` | 312 | berechnet |
| `ep:05351:ordentliche_aufwendungen` | 312 | berechnet |
| `ep:05351:ordentliche_ertraege` | 312 | berechnet |
| `ep:05351:ordentliches_ergebnis` | 312 | berechnet |
| `ep:05351:personalaufwendungen` | 312 | berechnet |
| `ep:05351:sonstige_ordentliche_ertraege` | 312 | berechnet |
| `ep:05351:transferaufwendungen` | 312 | berechnet |
| `ep:05375:abschreibungen` | 320 | berechnet |
| `ep:05375:ergebnis_laufende_verwaltung` | 320 | berechnet |
| `ep:05375:ergebnis_nach_minderaufwand` | 320 | berechnet |
| `ep:05375:jahresergebnis` | 320 | berechnet |
| `ep:05375:kostenerstattungen` | 320 | berechnet |
| `ep:05375:oeffentlich_rechtliche_entgelte` | 320 | berechnet |
| `ep:05375:ordentliche_aufwendungen` | 320 | berechnet |
| `ep:05375:ordentliche_ertraege` | 320 | berechnet |
| `ep:05375:ordentliches_ergebnis` | 320 | berechnet |
| `ep:05375:personalaufwendungen` | 320 | berechnet |
| `ep:05375:sach_und_dienstleistungen` | 320 | berechnet |
| `ep:05375:sonstige_ordentliche_aufwendungen` | 320 | berechnet |
| `ep:05375:sonstige_ordentliche_ertraege` | 320 | berechnet |
| `ep:05375:zuwendungen` | 320 | berechnet |
| `ep:06361:abschreibungen` | 329 | berechnet |
| `ep:06361:ergebnis_laufende_verwaltung` | 329 | berechnet |
| `ep:06361:ergebnis_nach_minderaufwand` | 329 | berechnet |
| `ep:06361:jahresergebnis` | 329 | berechnet |
| `ep:06361:ordentliche_aufwendungen` | 329 | berechnet |
| `ep:06361:ordentliche_ertraege` | 329 | berechnet |
| `ep:06361:ordentliches_ergebnis` | 329 | berechnet |
| `ep:06361:personalaufwendungen` | 329 | berechnet |
| `ep:06361:privatrechtliche_entgelte` | 329 | berechnet |
| `ep:06361:sach_und_dienstleistungen` | 329 | berechnet |
| `ep:06361:sonstige_ordentliche_aufwendungen` | 329 | berechnet |
| `ep:06361:sonstige_ordentliche_ertraege` | 329 | berechnet |
| `ep:06361:transferaufwendungen` | 329 | berechnet |
| `ep:06361:zuwendungen` | 329 | berechnet |
| `ep:06362:ergebnis_laufende_verwaltung` | 335 | berechnet |
| `ep:06362:ergebnis_nach_minderaufwand` | 335 | berechnet |
| `ep:06362:jahresergebnis` | 335 | berechnet |
| `ep:06362:ordentliche_aufwendungen` | 335 | berechnet |
| `ep:06362:ordentliche_ertraege` | 335 | berechnet |
| `ep:06362:ordentliches_ergebnis` | 335 | berechnet |
| `ep:06362:personalaufwendungen` | 335 | berechnet |
| `ep:06362:sach_und_dienstleistungen` | 335 | berechnet |
| `ep:06362:sonstige_ordentliche_aufwendungen` | 335 | berechnet |
| `ep:06362:sonstige_ordentliche_ertraege` | 335 | berechnet |
| `ep:06362:transferaufwendungen` | 335 | berechnet |
| `ep:06366:abschreibungen` | 340 | berechnet |
| `ep:06366:ergebnis_laufende_verwaltung` | 340 | berechnet |
| `ep:06366:ergebnis_nach_minderaufwand` | 340 | berechnet |
| `ep:06366:jahresergebnis` | 340 | berechnet |
| `ep:06366:ordentliche_aufwendungen` | 340 | berechnet |
| `ep:06366:ordentliche_ertraege` | 340 | berechnet |
| `ep:06366:ordentliches_ergebnis` | 340 | berechnet |
| `ep:06366:personalaufwendungen` | 340 | berechnet |
| `ep:06366:sach_und_dienstleistungen` | 340 | berechnet |
| `ep:06366:zuwendungen` | 340 | berechnet |
| `ep:07411:ergebnis_laufende_verwaltung` | 349 | berechnet |
| `ep:07411:ergebnis_nach_minderaufwand` | 349 | berechnet |
| `ep:07411:jahresergebnis` | 349 | berechnet |
| `ep:07411:ordentliche_aufwendungen` | 349 | berechnet |
| `ep:07411:ordentliches_ergebnis` | 349 | berechnet |
| `ep:07411:transferaufwendungen` | 349 | berechnet |
| `ep:08421:ergebnis_laufende_verwaltung` | 357 | berechnet |
| `ep:08421:ergebnis_nach_minderaufwand` | 357 | berechnet |
| `ep:08421:jahresergebnis` | 357 | berechnet |
| `ep:08421:ordentliche_aufwendungen` | 357 | berechnet |
| `ep:08421:ordentliche_ertraege` | 357 | berechnet |
| `ep:08421:ordentliches_ergebnis` | 357 | berechnet |
| `ep:08421:personalaufwendungen` | 357 | berechnet |
| `ep:08421:sonstige_ordentliche_aufwendungen` | 357 | berechnet |
| `ep:08421:sonstige_ordentliche_ertraege` | 357 | berechnet |
| `ep:08421:transferaufwendungen` | 357 | berechnet |
| `ep:08421:zuwendungen` | 357 | berechnet |
| `ep:08424:abschreibungen` | 362 | berechnet |
| `ep:08424:ergebnis_laufende_verwaltung` | 362 | berechnet |
| `ep:08424:ergebnis_nach_minderaufwand` | 362 | berechnet |
| `ep:08424:jahresergebnis` | 362 | berechnet |
| `ep:08424:kostenerstattungen` | 362 | berechnet |
| `ep:08424:oeffentlich_rechtliche_entgelte` | 362 | berechnet |
| `ep:08424:ordentliche_aufwendungen` | 362 | berechnet |
| `ep:08424:ordentliche_ertraege` | 362 | berechnet |
| `ep:08424:ordentliches_ergebnis` | 362 | berechnet |
| `ep:08424:personalaufwendungen` | 362 | berechnet |
| `ep:08424:sach_und_dienstleistungen` | 362 | berechnet |
| `ep:08424:sonstige_ordentliche_aufwendungen` | 362 | berechnet |
| `ep:08424:sonstige_ordentliche_ertraege` | 362 | berechnet |
| `ep:08424:transferaufwendungen` | 362 | berechnet |
| `ep:08424:zuwendungen` | 362 | berechnet |
| `ep:09511:ergebnis_laufende_verwaltung` | 385 | berechnet |
| `ep:09511:ergebnis_nach_minderaufwand` | 385 | berechnet |
| `ep:09511:jahresergebnis` | 385 | berechnet |
| `ep:09511:kostenerstattungen` | 385 | berechnet |
| `ep:09511:oeffentlich_rechtliche_entgelte` | 385 | berechnet |
| `ep:09511:ordentliche_aufwendungen` | 385 | berechnet |
| `ep:09511:ordentliche_ertraege` | 385 | berechnet |
| `ep:09511:ordentliches_ergebnis` | 385 | berechnet |
| `ep:09511:personalaufwendungen` | 385 | berechnet |
| `ep:09511:sach_und_dienstleistungen` | 385 | berechnet |
| `ep:09511:sonstige_ordentliche_aufwendungen` | 385 | berechnet |
| `ep:09511:sonstige_ordentliche_ertraege` | 385 | berechnet |
| `ep:09511:transferaufwendungen` | 385 | berechnet |
| `ep:09511:zuwendungen` | 385 | berechnet |
| `ep:10521:ergebnis_laufende_verwaltung` | 393 | berechnet |
| `ep:10521:ergebnis_nach_minderaufwand` | 393 | berechnet |
| `ep:10521:jahresergebnis` | 393 | berechnet |
| `ep:10521:oeffentlich_rechtliche_entgelte` | 393 | berechnet |
| `ep:10521:ordentliche_aufwendungen` | 393 | berechnet |
| `ep:10521:ordentliche_ertraege` | 393 | berechnet |
| `ep:10521:ordentliches_ergebnis` | 393 | berechnet |
| `ep:10521:personalaufwendungen` | 393 | berechnet |
| `ep:10521:sonstige_ordentliche_ertraege` | 393 | berechnet |
| `ep:10522:ergebnis_laufende_verwaltung` | 397 | berechnet |
| `ep:10522:ergebnis_nach_minderaufwand` | 397 | berechnet |
| `ep:10522:jahresergebnis` | 397 | berechnet |
| `ep:10522:ordentliche_aufwendungen` | 397 | berechnet |
| `ep:10522:ordentliches_ergebnis` | 397 | berechnet |
| `ep:10522:personalaufwendungen` | 397 | berechnet |
| `ep:10522:transferaufwendungen` | 397 | berechnet |
| `ep:10523:ergebnis_laufende_verwaltung` | 401 | berechnet |
| `ep:10523:ergebnis_nach_minderaufwand` | 401 | berechnet |
| `ep:10523:jahresergebnis` | 401 | berechnet |
| `ep:10523:oeffentlich_rechtliche_entgelte` | 401 | berechnet |
| `ep:10523:ordentliche_aufwendungen` | 401 | berechnet |
| `ep:10523:ordentliche_ertraege` | 401 | berechnet |
| `ep:10523:ordentliches_ergebnis` | 401 | berechnet |
| `ep:10523:personalaufwendungen` | 401 | berechnet |
| `ep:10523:sonstige_ordentliche_aufwendungen` | 401 | berechnet |
| `ep:10523:transferaufwendungen` | 401 | berechnet |
| `ep:10523:zuwendungen` | 401 | berechnet |
| `ep:11531:ergebnis_laufende_verwaltung` | 410 | berechnet |
| `ep:11531:ergebnis_nach_minderaufwand` | 410 | berechnet |
| `ep:11531:jahresergebnis` | 410 | berechnet |
| `ep:11531:ordentliche_ertraege` | 410 | berechnet |
| `ep:11531:ordentliches_ergebnis` | 410 | berechnet |
| `ep:11531:privatrechtliche_entgelte` | 410 | berechnet |
| `ep:11531:sonstige_ordentliche_ertraege` | 410 | berechnet |
| `ep:11532:ergebnis_laufende_verwaltung` | 414 | berechnet |
| `ep:11532:ergebnis_nach_minderaufwand` | 414 | berechnet |
| `ep:11532:jahresergebnis` | 414 | berechnet |
| `ep:11532:ordentliche_ertraege` | 414 | berechnet |
| `ep:11532:ordentliches_ergebnis` | 414 | berechnet |
| `ep:11532:sonstige_ordentliche_ertraege` | 414 | berechnet |
| `ep:11537:abschreibungen` | 418 | berechnet |
| `ep:11537:ergebnis_laufende_verwaltung` | 418 | berechnet |
| `ep:11537:ergebnis_nach_minderaufwand` | 418 | berechnet |
| `ep:11537:finanzergebnis` | 418 | berechnet |
| `ep:11537:finanzertraege` | 418 | berechnet |
| `ep:11537:jahresergebnis` | 418 | berechnet |
| `ep:11537:oeffentlich_rechtliche_entgelte` | 418 | berechnet |
| `ep:11537:ordentliche_aufwendungen` | 418 | berechnet |
| `ep:11537:ordentliche_ertraege` | 418 | berechnet |
| `ep:11537:ordentliches_ergebnis` | 418 | berechnet |
| `ep:11537:personalaufwendungen` | 418 | berechnet |
| `ep:11537:privatrechtliche_entgelte` | 418 | berechnet |
| `ep:11537:sach_und_dienstleistungen` | 418 | berechnet |
| `ep:11537:sonstige_ordentliche_aufwendungen` | 418 | berechnet |
| `ep:11537:sonstige_ordentliche_ertraege` | 418 | berechnet |
| `ep:11538:abschreibungen` | 425 | berechnet |
| `ep:11538:ergebnis_laufende_verwaltung` | 425 | berechnet |
| `ep:11538:ergebnis_nach_minderaufwand` | 425 | berechnet |
| `ep:11538:finanzergebnis` | 425 | berechnet |
| `ep:11538:finanzertraege` | 425 | berechnet |
| `ep:11538:jahresergebnis` | 425 | berechnet |
| `ep:11538:kostenerstattungen` | 425 | berechnet |
| `ep:11538:oeffentlich_rechtliche_entgelte` | 425 | berechnet |
| `ep:11538:ordentliche_aufwendungen` | 425 | berechnet |
| `ep:11538:ordentliche_ertraege` | 425 | berechnet |
| `ep:11538:ordentliches_ergebnis` | 425 | berechnet |
| `ep:11538:personalaufwendungen` | 425 | berechnet |
| `ep:11538:privatrechtliche_entgelte` | 425 | berechnet |
| `ep:11538:sach_und_dienstleistungen` | 425 | berechnet |
| `ep:11538:sonstige_ordentliche_aufwendungen` | 425 | berechnet |
| `ep:11538:sonstige_ordentliche_ertraege` | 425 | berechnet |
| `ep:11538:zuwendungen` | 425 | berechnet |
| `ep:12541:abschreibungen` | 447 | berechnet |
| `ep:12541:ergebnis_laufende_verwaltung` | 447 | berechnet |
| `ep:12541:ergebnis_nach_minderaufwand` | 447 | berechnet |
| `ep:12541:jahresergebnis` | 447 | berechnet |
| `ep:12541:kostenerstattungen` | 447 | berechnet |
| `ep:12541:oeffentlich_rechtliche_entgelte` | 447 | berechnet |
| `ep:12541:ordentliche_aufwendungen` | 447 | berechnet |
| `ep:12541:ordentliche_ertraege` | 447 | berechnet |
| `ep:12541:ordentliches_ergebnis` | 447 | berechnet |
| `ep:12541:personalaufwendungen` | 447 | berechnet |
| `ep:12541:privatrechtliche_entgelte` | 447 | berechnet |
| `ep:12541:sach_und_dienstleistungen` | 447 | berechnet |
| `ep:12541:sonstige_ordentliche_aufwendungen` | 447 | berechnet |
| `ep:12541:sonstige_ordentliche_ertraege` | 447 | berechnet |
| `ep:12541:zuwendungen` | 447 | berechnet |
| `ep:12542:ergebnis_laufende_verwaltung` | 463 | berechnet |
| `ep:12542:ergebnis_nach_minderaufwand` | 463 | berechnet |
| `ep:12542:jahresergebnis` | 463 | berechnet |
| `ep:12542:ordentliche_aufwendungen` | 463 | berechnet |
| `ep:12542:ordentliche_ertraege` | 463 | berechnet |
| `ep:12542:ordentliches_ergebnis` | 463 | berechnet |
| `ep:12542:personalaufwendungen` | 463 | berechnet |
| `ep:12542:transferaufwendungen` | 463 | berechnet |
| `ep:12542:zuwendungen` | 463 | berechnet |
| `ep:12543:ergebnis_laufende_verwaltung` | 469 | berechnet |
| `ep:12543:ergebnis_nach_minderaufwand` | 469 | berechnet |
| `ep:12543:jahresergebnis` | 469 | berechnet |
| `ep:12543:ordentliche_aufwendungen` | 469 | berechnet |
| `ep:12543:ordentliches_ergebnis` | 469 | berechnet |
| `ep:12543:personalaufwendungen` | 469 | berechnet |
| `ep:12545:ergebnis_laufende_verwaltung` | 473 | berechnet |
| `ep:12545:ergebnis_nach_minderaufwand` | 473 | berechnet |
| `ep:12545:finanzergebnis` | 473 | berechnet |
| `ep:12545:finanzertraege` | 473 | berechnet |
| `ep:12545:jahresergebnis` | 473 | berechnet |
| `ep:12545:oeffentlich_rechtliche_entgelte` | 473 | berechnet |
| `ep:12545:ordentliche_aufwendungen` | 473 | berechnet |
| `ep:12545:ordentliche_ertraege` | 473 | berechnet |
| `ep:12545:ordentliches_ergebnis` | 473 | berechnet |
| `ep:12545:personalaufwendungen` | 473 | berechnet |
| `ep:12545:sach_und_dienstleistungen` | 473 | berechnet |
| `ep:12545:sonstige_ordentliche_aufwendungen` | 473 | berechnet |
| `ep:12545:sonstige_ordentliche_ertraege` | 473 | berechnet |
| `ep:12546:abschreibungen` | 478 | berechnet |
| `ep:12546:ergebnis_laufende_verwaltung` | 478 | berechnet |
| `ep:12546:ergebnis_nach_minderaufwand` | 478 | berechnet |
| `ep:12546:jahresergebnis` | 478 | berechnet |
| `ep:12546:oeffentlich_rechtliche_entgelte` | 478 | berechnet |
| `ep:12546:ordentliche_aufwendungen` | 478 | berechnet |
| `ep:12546:ordentliche_ertraege` | 478 | berechnet |
| `ep:12546:ordentliches_ergebnis` | 478 | berechnet |
| `ep:12546:personalaufwendungen` | 478 | berechnet |
| `ep:12546:sach_und_dienstleistungen` | 478 | berechnet |
| `ep:12546:zuwendungen` | 478 | berechnet |
| `ep:12547:abschreibungen` | 483 | berechnet |
| `ep:12547:ergebnis_laufende_verwaltung` | 483 | berechnet |
| `ep:12547:ergebnis_nach_minderaufwand` | 483 | berechnet |
| `ep:12547:jahresergebnis` | 483 | berechnet |
| `ep:12547:oeffentlich_rechtliche_entgelte` | 483 | berechnet |
| `ep:12547:ordentliche_aufwendungen` | 483 | berechnet |
| `ep:12547:ordentliche_ertraege` | 483 | berechnet |
| `ep:12547:ordentliches_ergebnis` | 483 | berechnet |
| `ep:12547:personalaufwendungen` | 483 | berechnet |
| `ep:12547:privatrechtliche_entgelte` | 483 | berechnet |
| `ep:12547:sach_und_dienstleistungen` | 483 | berechnet |
| `ep:12547:sonstige_ordentliche_aufwendungen` | 483 | berechnet |
| `ep:12547:sonstige_ordentliche_ertraege` | 483 | berechnet |
| `ep:12547:zuwendungen` | 483 | berechnet |
| `ep:13551:abschreibungen` | 492 | berechnet |
| `ep:13551:ergebnis_laufende_verwaltung` | 492 | berechnet |
| `ep:13551:ergebnis_nach_minderaufwand` | 492 | berechnet |
| `ep:13551:jahresergebnis` | 492 | berechnet |
| `ep:13551:oeffentlich_rechtliche_entgelte` | 492 | berechnet |
| `ep:13551:ordentliche_aufwendungen` | 492 | berechnet |
| `ep:13551:ordentliche_ertraege` | 492 | berechnet |
| `ep:13551:ordentliches_ergebnis` | 492 | berechnet |
| `ep:13551:personalaufwendungen` | 492 | berechnet |
| `ep:13551:privatrechtliche_entgelte` | 492 | berechnet |
| `ep:13551:sach_und_dienstleistungen` | 492 | berechnet |
| `ep:13551:sonstige_ordentliche_aufwendungen` | 492 | berechnet |
| `ep:13551:sonstige_ordentliche_ertraege` | 492 | berechnet |
| `ep:13551:zuwendungen` | 492 | berechnet |
| `ep:13552:ergebnis_laufende_verwaltung` | 503 | berechnet |
| `ep:13552:ergebnis_nach_minderaufwand` | 503 | berechnet |
| `ep:13552:finanzergebnis` | 503 | berechnet |
| `ep:13552:finanzertraege` | 503 | berechnet |
| `ep:13552:jahresergebnis` | 503 | berechnet |
| `ep:13552:kostenerstattungen` | 503 | berechnet |
| `ep:13552:oeffentlich_rechtliche_entgelte` | 503 | berechnet |
| `ep:13552:ordentliche_aufwendungen` | 503 | berechnet |
| `ep:13552:ordentliche_ertraege` | 503 | berechnet |
| `ep:13552:ordentliches_ergebnis` | 503 | berechnet |
| `ep:13552:personalaufwendungen` | 503 | berechnet |
| `ep:13552:sach_und_dienstleistungen` | 503 | berechnet |
| `ep:13552:sonstige_ordentliche_aufwendungen` | 503 | berechnet |
| `ep:13552:sonstige_ordentliche_ertraege` | 503 | berechnet |
| `ep:13553:abschreibungen` | 509 | berechnet |
| `ep:13553:ergebnis_laufende_verwaltung` | 509 | berechnet |
| `ep:13553:ergebnis_nach_minderaufwand` | 509 | berechnet |
| `ep:13553:jahresergebnis` | 509 | berechnet |
| `ep:13553:ordentliche_aufwendungen` | 509 | berechnet |
| `ep:13553:ordentliche_ertraege` | 509 | berechnet |
| `ep:13553:ordentliches_ergebnis` | 509 | berechnet |
| `ep:13553:personalaufwendungen` | 509 | berechnet |
| `ep:13553:privatrechtliche_entgelte` | 509 | berechnet |
| `ep:13553:sach_und_dienstleistungen` | 509 | berechnet |
| `ep:13553:sonstige_ordentliche_aufwendungen` | 509 | berechnet |
| `ep:13553:sonstige_ordentliche_ertraege` | 509 | berechnet |
| `ep:13553:transferaufwendungen` | 509 | berechnet |
| `ep:13553:zuwendungen` | 509 | berechnet |
| `ep:14561:abschreibungen` | 517 | berechnet |
| `ep:14561:ergebnis_laufende_verwaltung` | 517 | berechnet |
| `ep:14561:ergebnis_nach_minderaufwand` | 517 | berechnet |
| `ep:14561:jahresergebnis` | 517 | berechnet |
| `ep:14561:ordentliche_aufwendungen` | 517 | berechnet |
| `ep:14561:ordentliche_ertraege` | 517 | berechnet |
| `ep:14561:ordentliches_ergebnis` | 517 | berechnet |
| `ep:14561:personalaufwendungen` | 517 | berechnet |
| `ep:14561:sach_und_dienstleistungen` | 517 | berechnet |
| `ep:14561:sonstige_ordentliche_aufwendungen` | 517 | berechnet |
| `ep:14561:sonstige_ordentliche_ertraege` | 517 | berechnet |
| `ep:14561:transferaufwendungen` | 517 | berechnet |
| `ep:14561:zuwendungen` | 517 | berechnet |
| `ep:15571:abschreibungen` | 528 | berechnet |
| `ep:15571:ergebnis_laufende_verwaltung` | 528 | berechnet |
| `ep:15571:ergebnis_nach_minderaufwand` | 528 | berechnet |
| `ep:15571:jahresergebnis` | 528 | berechnet |
| `ep:15571:ordentliche_aufwendungen` | 528 | berechnet |
| `ep:15571:ordentliche_ertraege` | 528 | berechnet |
| `ep:15571:ordentliches_ergebnis` | 528 | berechnet |
| `ep:15571:personalaufwendungen` | 528 | berechnet |
| `ep:15571:sach_und_dienstleistungen` | 528 | berechnet |
| `ep:15571:sonstige_ordentliche_aufwendungen` | 528 | berechnet |
| `ep:15571:sonstige_ordentliche_ertraege` | 528 | berechnet |
| `ep:15571:transferaufwendungen` | 528 | berechnet |
| `ep:15571:zuwendungen` | 528 | berechnet |
| `ep:15573:abschreibungen` | 534 | berechnet |
| `ep:15573:ergebnis_laufende_verwaltung` | 534 | berechnet |
| `ep:15573:ergebnis_nach_minderaufwand` | 534 | berechnet |
| `ep:15573:finanzergebnis` | 534 | berechnet |
| `ep:15573:finanzertraege` | 534 | berechnet |
| `ep:15573:jahresergebnis` | 534 | berechnet |
| `ep:15573:kostenerstattungen` | 534 | berechnet |
| `ep:15573:oeffentlich_rechtliche_entgelte` | 534 | berechnet |
| `ep:15573:ordentliche_aufwendungen` | 534 | berechnet |
| `ep:15573:ordentliche_ertraege` | 534 | berechnet |
| `ep:15573:ordentliches_ergebnis` | 534 | berechnet |
| `ep:15573:personalaufwendungen` | 534 | berechnet |
| `ep:15573:sach_und_dienstleistungen` | 534 | berechnet |
| `ep:15573:sonstige_ordentliche_aufwendungen` | 534 | berechnet |
| `ep:15573:sonstige_ordentliche_ertraege` | 534 | berechnet |
| `ep:15573:zinsaufwendungen` | 534 | berechnet |
| `ep:15573:zuwendungen` | 534 | berechnet |
| `ep:15575:abschreibungen` | 546 | berechnet |
| `ep:15575:ergebnis_laufende_verwaltung` | 546 | berechnet |
| `ep:15575:ergebnis_nach_minderaufwand` | 546 | berechnet |
| `ep:15575:jahresergebnis` | 546 | berechnet |
| `ep:15575:oeffentlich_rechtliche_entgelte` | 546 | berechnet |
| `ep:15575:ordentliche_aufwendungen` | 546 | berechnet |
| `ep:15575:ordentliche_ertraege` | 546 | berechnet |
| `ep:15575:ordentliches_ergebnis` | 546 | berechnet |
| `ep:15575:personalaufwendungen` | 546 | berechnet |
| `ep:15575:privatrechtliche_entgelte` | 546 | berechnet |
| `ep:15575:sach_und_dienstleistungen` | 546 | berechnet |
| `ep:15575:sonstige_ordentliche_aufwendungen` | 546 | berechnet |
| `ep:15575:sonstige_ordentliche_ertraege` | 546 | berechnet |
| `ep:15575:transferaufwendungen` | 546 | berechnet |
| `ep:15575:zuwendungen` | 546 | berechnet |
| `ep:16611:ergebnis_laufende_verwaltung` | 556 | berechnet |
| `ep:16611:ergebnis_nach_minderaufwand` | 556 | berechnet |
| `ep:16611:jahresergebnis` | 556 | berechnet |
| `ep:16611:oeffentlich_rechtliche_entgelte` | 556 | berechnet |
| `ep:16611:ordentliche_aufwendungen` | 556 | berechnet |
| `ep:16611:ordentliche_ertraege` | 556 | berechnet |
| `ep:16611:ordentliches_ergebnis` | 556 | berechnet |
| `ep:16611:sonstige_ordentliche_aufwendungen` | 556 | berechnet |
| `ep:16611:sonstige_ordentliche_ertraege` | 556 | berechnet |
| `ep:16611:sonstige_transferertraege` | 556 | berechnet |
| `ep:16611:steuern` | 556 | berechnet |
| `ep:16611:transferaufwendungen` | 556 | berechnet |
| `ep:16611:zuwendungen` | 556 | berechnet |
| `ep:16612:ergebnis_laufende_verwaltung` | 562 | berechnet |
| `ep:16612:ergebnis_nach_minderaufwand` | 562 | berechnet |
| `ep:16612:finanzergebnis` | 562 | berechnet |
| `ep:16612:finanzertraege` | 562 | berechnet |
| `ep:16612:jahresergebnis` | 562 | berechnet |
| `ep:16612:ordentliche_aufwendungen` | 562 | berechnet |
| `ep:16612:ordentliche_ertraege` | 562 | berechnet |
| `ep:16612:ordentliches_ergebnis` | 562 | berechnet |
| `ep:16612:sonstige_ordentliche_aufwendungen` | 562 | berechnet |
| `ep:16612:sonstige_ordentliche_ertraege` | 562 | berechnet |
| `ep:16612:zinsaufwendungen` | 562 | berechnet |

## fp – Finanzplanzeilen

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `fp:GESAMT:liquide_mittel` | 81 | nicht_gefunden |

## vb – Vorberichtsposten

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `vb:eigenkapital:allgemeine_ruecklage` | 588 | nicht_gefunden |
| `vb:eigenkapital:ausgleichsruecklage` | 588 | nicht_gefunden |
| `vb:eigenkapital:bilanzieller_verlustvortrag` | 588 | nicht_gefunden |
| `vb:eigenkapital:gesamt` | 588 | nicht_gefunden |
| `vb:eigenkapital:jahresergebnis` | 588 | nicht_gefunden |
| `vb:eigenkapital:sonderruecklagen` | 588 | nicht_gefunden |
| `vb:investitionszuwendungen:gesamt` | 80 | nicht_gefunden |
| `vb:investitionszuwendungen:investitionspauschale` | 61 | nicht_gefunden |
| `vb:investitionszuwendungen:schulpauschale` | 61 | nicht_gefunden |
| `vb:investitionszuwendungen:sportpauschale` | 61 | nicht_gefunden |
| `vb:investitionszuwendungen:uebrige_investitionszuwendungen` | 80 | berechnet |
| `vb:leistungsentgelte:aufloesung_sonderposten_beitraege` | 24 | betrag_fehlt |
| `vb:leistungsentgelte:aufloesung_sonderposten_gebuehrenausgleich` | 24 | betrag_fehlt |
| `vb:personal:beihilfen_beschaeftigte` | 28 | betrag_fehlt |
| `vb:personal:beihilferueckstellungen` | 28 | betrag_fehlt |
| `vb:personal:dienstaufwendungen_tariflich` | 28 | betrag_fehlt |
| `vb:personal:pensionsrueckstellungen` | 28 | betrag_fehlt |
| `vb:personal:sozialversicherung_tariflich` | 28 | betrag_fehlt |
| `vb:personal:uebrige_personalaufwendungen` | 28 | berechnet |
| `vb:personal:versorgungskassen_tariflich` | 28 | betrag_fehlt |
| `vb:privatrechtliche_leistungsentgelte:uebrige_privatrechtliche_leistungsentgelte` | 24 | berechnet |
| `vb:sachaufwand:unbewegliches_vermoegen` | 30 | betrag_fehlt |
| `vb:sonstige_aufwendungen:leistungsbeteiligungen` | 37 | betrag_fehlt |
| `vb:sonstige_aufwendungen:rechte_und_dienste` | 37 | betrag_fehlt |
| `vb:sonstige_aufwendungen:sonstige_personal_versorgung` | 37 | betrag_fehlt |
| `vb:sonstige_aufwendungen:weitere_sonstige_aufwendungen` | 37 | betrag_fehlt |
| `vb:sonstige_ertraege:andere_sonstige_ertraege` | 24 | betrag_fehlt |
| `vb:sonstige_ertraege:aufloesung_rueckstellungen` | 24 | betrag_fehlt |
| `vb:sonstige_ertraege:gesamt` | 24 | betrag_fehlt |
| `vb:sonstige_ertraege:sonstige` | 24 | berechnet |
| `vb:sonstige_ertraege:uebrige_sonstige_ertraege` | 24 | berechnet |
| `vb:sonstige_ertraege:veraeusserung_grundstuecke` | 24 | betrag_fehlt |
| `vb:transferaufwendungen:gewerbesteuerumlage` | 33 | berechnet |
| `vb:transferaufwendungen:jugendamtsumlage` | 34 | betrag_fehlt |
| `vb:transferaufwendungen:kreisumlage` | 34 | betrag_fehlt |
| `vb:transferaufwendungen:uebrige_transferaufwendungen` | 27 | berechnet |
| `vb:zuwendungen:schluesselzuweisung` | 22 | betrag_fehlt |
| `vb:zuwendungen:sonstige` | 15 | berechnet |
| `vb:zuwendungen:uebrige_zuwendungen` | 15 | berechnet |

## gz – Grundzahlen

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `gz:0111101:2` | 116 | nicht_gefunden |
| `gz:0111101:3` | 116 | nicht_gefunden |
| `gz:0111107:2` | 148 | nicht_gefunden |
| `gz:0111107:3` | 148 | nicht_gefunden |
| `gz:0111107:4` | 148 | nicht_gefunden |
| `gz:0111107:5` | 148 | nicht_gefunden |
| `gz:0111107:6` | 148 | nicht_gefunden |
| `gz:0111107:7` | 148 | nicht_gefunden |
| `gz:0111108:3` | 154 | nicht_gefunden |
| `gz:0111109:2` | 160 | nicht_gefunden |
| `gz:0111109:3` | 160 | nicht_gefunden |
| `gz:0212201:4` | 194 | nicht_gefunden |
| `gz:0212201:5` | 194 | nicht_gefunden |
| `gz:0212201:6` | 194 | nicht_gefunden |
| `gz:0212201:7` | 194 | nicht_gefunden |
| `gz:0212202:2` | 200 | nicht_gefunden |
| `gz:0212202:3` | 200 | nicht_gefunden |
| `gz:0212202:4` | 200 | nicht_gefunden |
| `gz:0212601:10` | 205 | nicht_gefunden |
| `gz:0212601:11` | 205 | nicht_gefunden |
| `gz:0212601:2` | 205 | nicht_gefunden |
| `gz:0212601:3` | 205 | nicht_gefunden |
| `gz:0212601:4` | 205 | nicht_gefunden |
| `gz:0212601:5` | 205 | nicht_gefunden |
| `gz:0212601:6` | 205 | nicht_gefunden |
| `gz:0212601:7` | 205 | nicht_gefunden |
| `gz:0212601:8` | 205 | nicht_gefunden |
| `gz:0212601:9` | 205 | nicht_gefunden |
| `gz:0427101:2` | 256 | nicht_gefunden |
| `gz:0531301:2` | 284 | nicht_gefunden |
| `gz:0534501:3` | 308 | nicht_gefunden |
| `gz:0534501:4` | 308 | nicht_gefunden |
| `gz:0534501:5` | 308 | nicht_gefunden |
| `gz:0535101:2` | 312 | nicht_gefunden |
| `gz:0535101:3` | 312 | nicht_gefunden |
| `gz:0535101:4` | 312 | nicht_gefunden |
| `gz:0535102:2` | 316 | nicht_gefunden |
| `gz:0535102:3` | 316 | nicht_gefunden |
| `gz:0636201:2` | 335 | nicht_gefunden |
| `gz:0636201:3` | 335 | nicht_gefunden |
| `gz:0636201:4` | 335 | nicht_gefunden |
| `gz:0636201:5` | 335 | nicht_gefunden |
| `gz:0636201:6` | 335 | nicht_gefunden |
| `gz:0636201:7` | 335 | nicht_gefunden |
| `gz:0636201:8` | 335 | nicht_gefunden |
| `gz:0842101:2` | 357 | nicht_gefunden |
| `gz:0842403:6` | 376 | nicht_gefunden |
| `gz:0842403:7` | 376 | nicht_gefunden |
| `gz:1052101:2` | 393 | nicht_gefunden |
| `gz:1052101:3` | 393 | nicht_gefunden |
| `gz:1052101:4` | 393 | nicht_gefunden |
| `gz:1153701:2` | 418 | nicht_gefunden |
| `gz:1153701:3` | 418 | nicht_gefunden |
| `gz:1153701:4` | 418 | nicht_gefunden |
| `gz:1153701:5` | 418 | nicht_gefunden |
| `gz:1355101:5` | 492 | nicht_gefunden |
| `gz:1355101:6` | 492 | nicht_gefunden |
| `gz:1355101:7` | 492 | nicht_gefunden |
| `gz:1557501:2` | 546 | nicht_gefunden |
| `gz:1557501:3` | 546 | nicht_gefunden |
| `gz:1557501:4` | 546 | nicht_gefunden |
| `gz:1661101:1` | 556 | nicht_gefunden |

## inv – Investitionsmaßnahmen

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `inv:0111102:111.02-003::auszahlung` | 124 | nicht_gefunden |
| `inv:0111109:111.09-003::auszahlung` | 163 | nicht_gefunden |
| `inv:0111112:111.12-004::einzahlung` | 181 | nicht_gefunden |
| `inv:0212601:126.01-004::auszahlung` | 209 | nicht_gefunden |
| `inv:0321101:211.01-016::auszahlung` | 223 | nicht_gefunden |
| `inv:1153801:538.01-3-005::auszahlung` | 431 | nicht_gefunden |
| `inv:1153801:538.01-5-002::auszahlung` | 432 | nicht_gefunden |
| `inv:1254101:541.01-1-006::einzahlung` | 450 | nicht_gefunden |
| `inv:1254101:541.01-2-012::einzahlung` | 451 | nicht_gefunden |
| `inv:1254101:541.01-3-008::auszahlung` | 452 | nicht_gefunden |
| `inv:1254101:541.01-3-008::einzahlung` | 452 | nicht_gefunden |
| `inv:1254101:541.01-5-006::auszahlung` | 453 | nicht_gefunden |

## ve – VE-Fälligkeiten

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `ve:0111102:111.02-004:` | 586 | nicht_gefunden |
| `ve:0111102:111.02-008:` | 586 | nicht_gefunden |
| `ve:0111102::` | 586 | nicht_gefunden |
| `ve:0111108:111.08-001:` | 586 | nicht_gefunden |
| `ve:0111108:111.08-002:` | 586 | nicht_gefunden |
| `ve:0212601:126.01-005:` | 586 | nicht_gefunden |
| `ve:0321101:211.01-015:` | 586 | nicht_gefunden |
| `ve:0842402:424.02-005:` | 586 | nicht_gefunden |
| `ve:0842402:424.02.-006:` | 586 | nicht_gefunden |
| `ve:1153801:538.01-3-003:` | 586 | nicht_gefunden |
| `ve:1153801:538.01-3-009:` | 586 | nicht_gefunden |
| `ve:1254101:541.01-3-004:` | 586 | nicht_gefunden |
| `ve:1254101:541.01-3-009:` | 586 | nicht_gefunden |
| `ve:1254101:541.01-5-003:` | 586 | nicht_gefunden |
| `ve:1254101:541.01-5-007:` | 586 | nicht_gefunden |

## sd – Schuldenstand

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `sd:investitionskredite` | 587 | betrag_fehlt |
| `sd:liquiditaetskredite` | 587 | betrag_fehlt |

## sp – Stellenplan

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `sp:beamte:1:-` | 568 | betrag_fehlt |
| `sp:beamte:1:01` | 570 | betrag_fehlt |
| `sp:beamte:2:-` | 568 | betrag_fehlt |
| `sp:beamte:2:01` | 570 | betrag_fehlt |
| `sp:beamte:2:02` | 570 | betrag_fehlt |
| `sp:beamte:2:03` | 570 | betrag_fehlt |
| `sp:beamte:2:04` | 570 | betrag_fehlt |
| `sp:beamte:2:06` | 570 | betrag_fehlt |
| `sp:beamte:2:08` | 570 | betrag_fehlt |
| `sp:beamte:2:11` | 570 | betrag_fehlt |
| `sp:beamte:2:12` | 571 | betrag_fehlt |
| `sp:beamte:2:13` | 571 | betrag_fehlt |
| `sp:beamte:2:15` | 571 | betrag_fehlt |
| `sp:beamte:3:-` | 568 | betrag_fehlt |
| `sp:beamte:3:01` | 570 | betrag_fehlt |
| `sp:beamte:3:05` | 570 | betrag_fehlt |
| `sp:beamte:4:-` | 568 | betrag_fehlt |
| `sp:beamte:4:01` | 570 | betrag_fehlt |
| `sp:beamte:4:03` | 570 | betrag_fehlt |
| `sp:beamte:4:04` | 570 | betrag_fehlt |
| `sp:beamte:4:06` | 570 | betrag_fehlt |
| `sp:beamte:4:08` | 570 | betrag_fehlt |
| `sp:beamte:4:09` | 570 | betrag_fehlt |
| `sp:beamte:4:11` | 571 | betrag_fehlt |
| `sp:beamte:4:12` | 571 | betrag_fehlt |
| `sp:beamte:4:13` | 571 | betrag_fehlt |
| `sp:beamte:4:14` | 571 | betrag_fehlt |
| `sp:beamte:4:15` | 571 | betrag_fehlt |
| `sp:beamte:5:-` | 568 | betrag_fehlt |
| `sp:beamte:5:01` | 570 | betrag_fehlt |
| `sp:beamte:5:11` | 571 | betrag_fehlt |
| `sp:beamte:5:12` | 571 | betrag_fehlt |
| `sp:beamte:6:-` | 568 | betrag_fehlt |
| `sp:beamte:6:01` | 570 | betrag_fehlt |
| `sp:beamte:6:02` | 570 | betrag_fehlt |
| `sp:beamte:6:03` | 570 | betrag_fehlt |
| `sp:beamte:6:05` | 570 | betrag_fehlt |
| `sp:beamte:6:06` | 570 | betrag_fehlt |
| `sp:beamte:6:08` | 570 | betrag_fehlt |
| `sp:beamte:6:09` | 570 | betrag_fehlt |
| `sp:beamte:6:13` | 571 | betrag_fehlt |
| `sp:beamte:7:-` | 568 | betrag_fehlt |
| `sp:beamte:7:02` | 570 | betrag_fehlt |
| `sp:beamte:7:03` | 570 | betrag_fehlt |
| `sp:beamte:7:04` | 570 | betrag_fehlt |
| `sp:beamte:7:11` | 570 | betrag_fehlt |
| `sp:beamte:7:15` | 571 | betrag_fehlt |
| `sp:beamte:8:-` | 568 | nicht_gefunden |
| `sp:beamte:9:-` | 568 | betrag_fehlt |
| `sp:beamte:9:03` | 570 | betrag_fehlt |
| `sp:beamte:9:04` | 570 | betrag_fehlt |
| `sp:beamte:9:06` | 570 | betrag_fehlt |
| `sp:beamte:9:08` | 570 | betrag_fehlt |
| `sp:nachwuchs:1:-` | 574 | nicht_gefunden |
| `sp:nachwuchs:2:-` | 574 | nicht_gefunden |
| `sp:nachwuchs:3:-` | 574 | nicht_gefunden |
| `sp:nachwuchs:4:-` | 574 | nicht_gefunden |
| `sp:nachwuchs:5:-` | 574 | nicht_gefunden |
| `sp:nachwuchs:6:-` | 574 | nicht_gefunden |
| `sp:sozial_erziehungsdienst:15:-` | 569 | betrag_fehlt |
| `sp:sozial_erziehungsdienst:15:03` | 572 | betrag_fehlt |
| `sp:sozial_erziehungsdienst:16:-` | 569 | betrag_fehlt |
| `sp:sozial_erziehungsdienst:16:03` | 572 | betrag_fehlt |
| `sp:sozial_erziehungsdienst:16:05` | 572 | betrag_fehlt |
| `sp:tarif:10:-` | 569 | betrag_fehlt |
| `sp:tarif:10:01` | 572 | betrag_fehlt |
| `sp:tarif:10:02` | 572 | betrag_fehlt |
| `sp:tarif:10:03` | 572 | betrag_fehlt |
| `sp:tarif:10:04` | 572 | betrag_fehlt |
| `sp:tarif:10:05` | 572 | betrag_fehlt |
| `sp:tarif:10:08` | 572 | betrag_fehlt |
| `sp:tarif:10:11` | 573 | betrag_fehlt |
| `sp:tarif:10:12` | 573 | betrag_fehlt |
| `sp:tarif:10:13` | 573 | betrag_fehlt |
| `sp:tarif:11:-` | 569 | betrag_fehlt |
| `sp:tarif:11:01` | 572 | betrag_fehlt |
| `sp:tarif:11:02` | 572 | betrag_fehlt |
| `sp:tarif:11:03` | 572 | betrag_fehlt |
| `sp:tarif:11:04` | 572 | betrag_fehlt |
| `sp:tarif:11:05` | 572 | betrag_fehlt |
| `sp:tarif:11:08` | 572 | betrag_fehlt |
| `sp:tarif:11:09` | 572 | betrag_fehlt |
| `sp:tarif:11:11` | 573 | betrag_fehlt |
| `sp:tarif:11:12` | 573 | betrag_fehlt |
| `sp:tarif:11:13` | 573 | betrag_fehlt |
| `sp:tarif:12:-` | 569 | nicht_gefunden |
| `sp:tarif:13:-` | 569 | betrag_fehlt |
| `sp:tarif:13:01` | 572 | betrag_fehlt |
| `sp:tarif:13:05` | 572 | betrag_fehlt |
| `sp:tarif:14:-` | 569 | betrag_fehlt |
| `sp:tarif:14:02` | 572 | betrag_fehlt |
| `sp:tarif:14:08` | 572 | betrag_fehlt |
| `sp:tarif:1:-` | 569 | betrag_fehlt |
| `sp:tarif:1:01` | 572 | betrag_fehlt |
| `sp:tarif:1:06` | 572 | betrag_fehlt |
| `sp:tarif:1:08` | 572 | betrag_fehlt |
| `sp:tarif:1:09` | 572 | betrag_fehlt |
| `sp:tarif:1:11` | 573 | betrag_fehlt |
| `sp:tarif:1:12` | 573 | betrag_fehlt |
| `sp:tarif:1:13` | 573 | betrag_fehlt |
| `sp:tarif:2:-` | 569 | betrag_fehlt |
| `sp:tarif:2:01` | 572 | betrag_fehlt |
| `sp:tarif:2:05` | 572 | betrag_fehlt |
| `sp:tarif:2:06` | 572 | betrag_fehlt |
| `sp:tarif:2:08` | 572 | betrag_fehlt |
| `sp:tarif:2:11` | 573 | betrag_fehlt |
| `sp:tarif:2:12` | 573 | betrag_fehlt |
| `sp:tarif:2:13` | 573 | betrag_fehlt |
| `sp:tarif:3:-` | 569 | betrag_fehlt |
| `sp:tarif:3:01` | 572 | betrag_fehlt |
| `sp:tarif:3:02` | 572 | betrag_fehlt |
| `sp:tarif:3:05` | 572 | betrag_fehlt |
| `sp:tarif:3:09` | 572 | betrag_fehlt |
| `sp:tarif:3:10` | 573 | betrag_fehlt |
| `sp:tarif:3:11` | 573 | betrag_fehlt |
| `sp:tarif:3:12` | 573 | betrag_fehlt |
| `sp:tarif:3:13` | 573 | betrag_fehlt |
| `sp:tarif:3:14` | 573 | betrag_fehlt |
| `sp:tarif:3:15` | 573 | betrag_fehlt |
| `sp:tarif:4:-` | 569 | betrag_fehlt |
| `sp:tarif:4:01` | 572 | betrag_fehlt |
| `sp:tarif:4:06` | 572 | betrag_fehlt |
| `sp:tarif:4:08` | 572 | betrag_fehlt |
| `sp:tarif:4:11` | 573 | betrag_fehlt |
| `sp:tarif:4:12` | 573 | betrag_fehlt |
| `sp:tarif:4:13` | 573 | betrag_fehlt |
| `sp:tarif:4:14` | 573 | betrag_fehlt |
| `sp:tarif:5:-` | 569 | betrag_fehlt |
| `sp:tarif:5:01` | 572 | betrag_fehlt |
| `sp:tarif:5:03` | 572 | betrag_fehlt |
| `sp:tarif:5:04` | 572 | betrag_fehlt |
| `sp:tarif:5:05` | 572 | betrag_fehlt |
| `sp:tarif:5:06` | 572 | betrag_fehlt |
| `sp:tarif:5:08` | 572 | betrag_fehlt |
| `sp:tarif:6:-` | 569 | betrag_fehlt |
| `sp:tarif:6:01` | 572 | betrag_fehlt |
| `sp:tarif:6:04` | 572 | betrag_fehlt |
| `sp:tarif:6:05` | 572 | betrag_fehlt |
| `sp:tarif:6:10` | 573 | betrag_fehlt |
| `sp:tarif:6:11` | 573 | betrag_fehlt |
| `sp:tarif:6:12` | 573 | betrag_fehlt |
| `sp:tarif:6:13` | 573 | betrag_fehlt |
| `sp:tarif:7:-` | 569 | betrag_fehlt |
| `sp:tarif:7:01` | 572 | betrag_fehlt |
| `sp:tarif:7:02` | 572 | betrag_fehlt |
| `sp:tarif:7:05` | 572 | betrag_fehlt |
| `sp:tarif:7:09` | 572 | betrag_fehlt |
| `sp:tarif:7:10` | 573 | betrag_fehlt |
| `sp:tarif:7:11` | 573 | betrag_fehlt |
| `sp:tarif:7:12` | 573 | betrag_fehlt |
| `sp:tarif:7:13` | 573 | betrag_fehlt |
| `sp:tarif:7:15` | 573 | betrag_fehlt |
| `sp:tarif:8:-` | 569 | betrag_fehlt |
| `sp:tarif:8:01` | 572 | betrag_fehlt |
| `sp:tarif:8:02` | 572 | betrag_fehlt |
| `sp:tarif:8:03` | 572 | betrag_fehlt |
| `sp:tarif:8:04` | 572 | betrag_fehlt |
| `sp:tarif:8:06` | 572 | betrag_fehlt |
| `sp:tarif:8:08` | 572 | betrag_fehlt |
| `sp:tarif:8:11` | 573 | betrag_fehlt |
| `sp:tarif:8:12` | 573 | betrag_fehlt |
| `sp:tarif:9:-` | 569 | betrag_fehlt |
| `sp:tarif:9:01` | 572 | betrag_fehlt |
| `sp:tarif:9:02` | 572 | betrag_fehlt |
| `sp:tarif:9:03` | 572 | betrag_fehlt |
| `sp:tarif:9:04` | 572 | betrag_fehlt |
| `sp:tarif:9:05` | 572 | betrag_fehlt |
| `sp:tarif:9:06` | 572 | betrag_fehlt |
| `sp:tarif:9:08` | 572 | betrag_fehlt |
| `sp:tarif:9:12` | 573 | betrag_fehlt |
| `sp:tarif:9:13` | 573 | betrag_fehlt |

## Datenschutz-Prüfliste

Belegseiten, deren Text eines der Stichwörter aus `layout.quellenbelege.pruefwoerter`
enthält (Seite, Stichwort, 1-basierter Zeilenindex auf der Seite; bewusst ohne
Textauszug). Namen außerhalb der Personenfelder der Produktseiten werden nicht
automatisch geschwärzt: Wer ein Etikett vor der zu schwärzenden Zeile kennt, trägt es
in `layout.quellenbelege.schwaerzen_nach` ein.

| Seite | Stichwort | Zeile | geschwärzt |
|---|---|---|---|
| 8 | Bürgermeister | 21 | nein |
| 76 | Bürgermeister | 8 | nein |
| 116 | Bürgermeister | 2 | nein |
| 116 | Bürgermeister | 9 | nein |
| 116 | Produktverantwortlicher | 10 | nein |
| 117 | Bürgermeister | 2 | nein |
| 117 | Bürgermeister | 49 | nein |
| 118 | Bürgermeister | 18 | nein |
| 118 | Bürgermeister | 32 | nein |
| 121 | Produktverantwortlicher | 10 | nein |
| 125 | Telefon | 13 | nein |
| 125 | Telefon | 27 | nein |
| 128 | Produktverantwortlicher | 10 | nein |
| 133 | Produktverantwortlicher | 10 | nein |
| 139 | Produktverantwortlicher | 10 | nein |
| 144 | Produktverantwortlicher | 10 | nein |
| 148 | Geschäftsführ | 22 | nein |
| 148 | Produktverantwortlicher | 10 | nein |
| 151 | Geschäftsführ | 13 | nein |
| 154 | Produktverantwortlicher | 10 | nein |
| 154 | Telefon | 13 | nein |
| 157 | Telefon | 39 | nein |
| 160 | Produktverantwortlicher | 10 | nein |
| 168 | Produktverantwortlicher | 10 | nein |
| 174 | Telefon | 33 | nein |
| 177 | Produktverantwortlicher | 10 | nein |
| 189 | Produktverantwortlicher | 10 | nein |
| 194 | Produktverantwortlicher | 10 | nein |
| 200 | Produktverantwortlicher | 10 | nein |
| 205 | Produktverantwortlicher | 10 | nein |
| 211 | Telefon | 23 | nein |
| 217 | Produktverantwortlicher | 10 | nein |
| 225 | Telefon | 42 | nein |
| 228 | Produktverantwortlicher | 10 | nein |
| 233 | Telefon | 35 | nein |
| 234 | Telefon | 27 | nein |
| 237 | Produktverantwortlicher | 10 | nein |
| 243 | Produktverantwortlicher | 10 | nein |
| 252 | Produktverantwortlicher | 10 | nein |
| 256 | Produktverantwortlicher | 10 | nein |
| 260 | Produktverantwortlicher | 10 | nein |
| 264 | Produktverantwortlicher | 10 | nein |
| 269 | Produktverantwortlicher | 10 | nein |
| 279 | Produktverantwortlicher | 10 | nein |
| 282 | Ansprechpartner | 12 | nein |
| 284 | Produktverantwortlicher | 10 | nein |
| 290 | Produktverantwortlicher | 10 | nein |
| 293 | Ansprechpartner | 16 | nein |
| 295 | Produktverantwortlicher | 10 | nein |
| 297 | Ansprechpartner | 16 | nein |
| 299 | Produktverantwortlicher | 10 | nein |
| 302 | Ansprechpartner | 16 | nein |
| 304 | Produktverantwortlicher | 10 | nein |
| 308 | Produktverantwortlicher | 10 | nein |
| 312 | Produktverantwortlicher | 10 | nein |
| 316 | Produktverantwortlicher | 10 | nein |
| 320 | Produktverantwortlicher | 10 | nein |
| 329 | Produktverantwortlicher | 10 | nein |
| 335 | Produktverantwortlicher | 10 | nein |
| 340 | Produktverantwortlicher | 10 | nein |
| 349 | Produktverantwortlicher | 10 | nein |
| 357 | Produktverantwortlicher | 10 | nein |
| 362 | Produktverantwortlicher | 10 | nein |
| 369 | Produktverantwortlicher | 10 | nein |
| 376 | Produktverantwortlicher | 10 | nein |
| 379 | Telefon | 28 | nein |
| 385 | Produktverantwortlicher | 10 | nein |
| 393 | Produktverantwortlicher | 10 | nein |
| 397 | Produktverantwortlicher | 10 | nein |
| 401 | Produktverantwortlicher | 10 | nein |
| 410 | Produktverantwortlicher | 10 | nein |
| 414 | Produktverantwortlicher | 10 | nein |
| 418 | Produktverantwortlicher | 10 | nein |
| 425 | Produktverantwortlicher | 10 | nein |
| 436 | Telefon | 17 | nein |
| 438 | Produktverantwortlicher | 10 | nein |
| 447 | Produktverantwortlicher | 10 | nein |
| 457 | Produktverantwortlicher | 10 | nein |
| 463 | Produktverantwortlicher | 10 | nein |
| 469 | Produktverantwortlicher | 10 | nein |
| 473 | Produktverantwortlicher | 10 | nein |
| 478 | Produktverantwortlicher | 10 | nein |
| 483 | Produktverantwortlicher | 10 | nein |
| 492 | Produktverantwortlicher | 10 | nein |
| 496 | Telefon | 22 | nein |
| 498 | Produktverantwortlicher | 10 | nein |
| 503 | Produktverantwortlicher | 10 | nein |
| 509 | Produktverantwortlicher | 10 | nein |
| 517 | Produktverantwortlicher | 10 | nein |
| 528 | Produktverantwortlicher | 10 | nein |
| 534 | Produktverantwortlicher | 10 | nein |
| 540 | Produktverantwortlicher | 10 | nein |
| 546 | Produktverantwortlicher | 10 | nein |
| 556 | Produktverantwortlicher | 10 | nein |
| 562 | Produktverantwortlicher | 10 | nein |
| 591 | Geschäftsführ | 21 | nein |

## Seiten mit Schwärzung

Seiten, deren Belegbild schwarze Rechtecke über Personenfeldern trägt.

| Seite | Rechtecke |
|---|---|
| 116 | 1 |
| 121 | 1 |
| 128 | 1 |
| 133 | 1 |
| 139 | 1 |
| 144 | 1 |
| 148 | 1 |
| 154 | 1 |
| 160 | 1 |
| 168 | 1 |
| 177 | 1 |
| 189 | 1 |
| 194 | 1 |
| 200 | 1 |
| 205 | 1 |
| 217 | 1 |
| 228 | 1 |
| 237 | 1 |
| 243 | 1 |
| 252 | 1 |
| 256 | 1 |
| 260 | 1 |
| 264 | 1 |
| 269 | 1 |
| 279 | 1 |
| 284 | 1 |
| 290 | 1 |
| 295 | 1 |
| 299 | 1 |
| 304 | 1 |
| 308 | 1 |
| 312 | 1 |
| 316 | 1 |
| 320 | 1 |
| 329 | 1 |
| 335 | 1 |
| 340 | 1 |
| 349 | 1 |
| 357 | 1 |
| 362 | 1 |
| 369 | 1 |
| 376 | 1 |
| 385 | 1 |
| 393 | 1 |
| 397 | 1 |
| 401 | 1 |
| 410 | 1 |
| 414 | 1 |
| 418 | 1 |
| 425 | 1 |
| 438 | 1 |
| 447 | 1 |
| 457 | 1 |
| 463 | 1 |
| 469 | 1 |
| 473 | 1 |
| 478 | 1 |
| 483 | 1 |
| 492 | 1 |
| 498 | 1 |
| 503 | 1 |
| 509 | 1 |
| 517 | 1 |
| 528 | 1 |
| 534 | 1 |
| 540 | 1 |
| 546 | 1 |
| 556 | 1 |
| 562 | 1 |
