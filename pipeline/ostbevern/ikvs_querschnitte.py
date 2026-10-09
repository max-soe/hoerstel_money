"""Haushaltsquerschnitte im IKVS-Layout (z. B. Stadt Hörstel, S. 85-110).

Kontrollquelle wie `ostbevern.querschnitte`: Je Produktgruppe (und einmal für den
Gesamthaushalt) druckt das PDF einen Block "Haushaltsquerschnitt - Ergebnishaushalt" und
einen Block "Haushaltsquerschnitt - Finanzplanung" mit einer Wertezeile "Plan 2026". Die
Spaltenköpfe sind mehrzeilig und alphabetisch sortiert; gedruckt werden nur belegte
Spalten, ihre Anzahl wechselt deshalb von Block zu Block.

Spalten werden geometrisch erkannt: Wörter einer Zeile mit kleinem Abstand bilden eine
Phrase, Phrasen verschiedener Zeilen mit überlappendem x-Bereich eine Spalte. Der
zusammengesetzte Spaltentext wird über `[layout.ikvs_querschnitte]` einer Kennzahl
zugeordnet; die Beträge werden in x-Reihenfolge den Spalten zugeordnet.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from ostbevern.ikvs import lies_ikvs_betrag, normalisiere, verbinde_teile
from ostbevern.konfiguration import Jahrgang, layout_liste, layout_text
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import QUERSCHNITTE_SPALTEN

_PHRASEN_ABSTAND = 8.0
_BETRAG_ODER_LEER = re.compile(r"^(--|-?\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)$")


class IkvsQuerschnitteFehler(ValueError):
    """Wird ausgelöst, wenn ein Querschnitt-Block nicht eindeutig lesbar ist (D-08)."""


@dataclass
class _Phrase:
    woerter: list[Wort]

    @property
    def x0(self) -> float:
        return self.woerter[0].x0

    @property
    def x1(self) -> float:
        return self.woerter[-1].x1

    @property
    def top(self) -> float:
        return self.woerter[0].top

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.woerter)


def _phrasen(zeile: Textzeile) -> list[_Phrase]:
    phrasen: list[_Phrase] = []
    for wort in sorted(zeile.woerter, key=lambda w: w.x0):
        if phrasen and wort.x0 - phrasen[-1].x1 <= _PHRASEN_ABSTAND:
            phrasen[-1].woerter.append(wort)
        else:
            phrasen.append(_Phrase([wort]))
    return phrasen


def spalten_aus_kopf(kopfzeilen: Sequence[Textzeile]) -> list[str]:
    """Spaltentexte eines mehrzeiligen Kopfs in x-Reihenfolge (Phrasen nach Überlappung)."""
    phrasen = [p for zeile in kopfzeilen for p in _phrasen(zeile)]
    gruppen: list[list[_Phrase]] = []
    for phrase in phrasen:
        treffer = [g for g in gruppen if any(p.x0 < phrase.x1 and phrase.x0 < p.x1 for p in g)]
        neu = [phrase]
        for gruppe in treffer:
            neu += gruppe
            gruppen.remove(gruppe)
        gruppen.append(neu)
    gruppen.sort(key=lambda g: min(p.x0 for p in g))
    return [
        verbinde_teile([p.text for p in sorted(g, key=lambda p: (p.top, p.x0))]) for g in gruppen
    ]


def _ist_wertezeile(zeile: Textzeile) -> bool:
    return any(_BETRAG_ODER_LEER.match(w.text) for w in zeile.woerter if w.text != "2026")


@dataclass(frozen=True)
class _Block:
    knoten: str  # PG-Code oder "" für den Gesamthaushalt
    plan: str
    kopf: tuple[Textzeile, ...]
    werte: tuple[Wort, ...]
    pdf_seite: int


class _OffenerBlock:
    def __init__(self, knoten: str, plan: str, pdf_seite: int) -> None:
        self.knoten = knoten
        self.plan = plan
        self.pdf_seite = pdf_seite
        self.kopf: list[Textzeile] = []
        self.werte: list[Wort] = []

    def schliesse(self) -> _Block:
        """Ein Block ohne Kopf und Werte ist leer (alle Kennzahlen 0, z. B. S. 91)."""
        if bool(self.kopf) != bool(self.werte):
            raise IkvsQuerschnitteFehler(
                f"S. {self.pdf_seite}: Querschnitt-Block {self.plan} mit Kopf, aber ohne Werte "
                "oder umgekehrt"
            )
        return _Block(self.knoten, self.plan, tuple(self.kopf), tuple(self.werte), self.pdf_seite)


def lies_ikvs_querschnitte(
    dokument: PdfDokument, jahrgang: Jahrgang, hierarchie: pl.DataFrame
) -> pl.DataFrame:
    """Liest alle Querschnitt-Blöcke als Langformat nach QUERSCHNITTE_SPALTEN.

    PG-Blöcke tragen `pb` aus der Hierarchie; der Gesamthaushalt hat `pb` und `pg` null
    und `gesamtsumme` = true. Jede Produktgruppe der Hierarchie braucht genau einen
    Ergebnis- und einen Finanzplanungsblock (D-08).
    """
    bereich = jahrgang.seitenbereiche["querschnitte"]
    pg_muster = re.compile(layout_text(jahrgang, "ikvs_querschnitte", "produktgruppe_muster"))
    gesamt_titel = layout_text(jahrgang, "ikvs_querschnitte", "gesamt_titel")
    plan_titel = {
        layout_text(jahrgang, "ikvs_querschnitte", "ergebnisplan_titel"): "ergebnisplan",
        layout_text(jahrgang, "ikvs_querschnitte", "finanzplan_titel"): "finanzplan",
    }
    wertezeile_beginn = set(layout_liste(jahrgang, "ikvs_querschnitte", "wertezeile_woerter"))
    kennzahlen: dict[str, dict[str, str]] = {}
    for plan in ("ergebnisplan", "finanzplan"):
        gedruckt = layout_liste(jahrgang, "ikvs_querschnitte", f"{plan}_spalten")
        schluessel = layout_liste(jahrgang, "ikvs_querschnitte", f"{plan}_kennzahlen")
        if len(gedruckt) != len(schluessel):
            raise IkvsQuerschnitteFehler(
                f"[layout.ikvs_querschnitte] {plan}: {len(gedruckt)} Spalten, "
                f"{len(schluessel)} Kennzahlen"
            )
        kennzahlen[plan] = {normalisiere(t): k for t, k in zip(gedruckt, schluessel, strict=True)}

    pg_eltern = {
        z["code"]: z["eltern_code"]
        for z in hierarchie.filter(pl.col("ebene") == "PG").iter_rows(named=True)
    }

    bloecke: list[_Block] = []
    knoten: str | None = None
    for pdf_seite in range(bereich.von, bereich.bis + 1):
        zeilen = [z for z in dokument.zeilen(pdf_seite)[1:] if z.text != str(pdf_seite)]
        offen: _OffenerBlock | None = None
        for zeile in zeilen:
            text = zeile.text
            treffer = pg_muster.match(text)
            if treffer is not None or text == gesamt_titel or text in plan_titel:
                if offen is not None:
                    bloecke.append(offen.schliesse())
                    offen = None
                if text in plan_titel:
                    if knoten is None:
                        raise IkvsQuerschnitteFehler(
                            f"S. {pdf_seite}: Querschnitt-Block ohne Produktgruppe"
                        )
                    offen = _OffenerBlock(knoten, plan_titel[text], pdf_seite)
                else:
                    knoten = treffer.group(1) if treffer is not None else ""
                continue
            if offen is None or all(w.text in wertezeile_beginn for w in zeile.woerter):
                continue
            if _ist_wertezeile(zeile):
                offen.werte += [w for w in zeile.woerter if _BETRAG_ODER_LEER.match(w.text)]
            elif offen.werte:
                raise IkvsQuerschnitteFehler(f"S. {pdf_seite}: Text nach den Werten: {text!r}")
            else:
                offen.kopf.append(zeile)
        if offen is not None:
            bloecke.append(offen.schliesse())

    datensaetze: list[dict[str, object]] = []
    gesehen: set[tuple[str, str]] = set()
    for block in bloecke:
        if (block.knoten, block.plan) in gesehen:
            raise IkvsQuerschnitteFehler(
                f"S. {block.pdf_seite}: Querschnitt {block.knoten or 'Gesamthaushalt'} "
                f"{block.plan} doppelt"
            )
        gesehen.add((block.knoten, block.plan))
        if block.knoten and block.knoten not in pg_eltern:
            raise IkvsQuerschnitteFehler(
                f"S. {block.pdf_seite}: Produktgruppe {block.knoten} fehlt in der Hierarchie"
            )
        spalten = spalten_aus_kopf(block.kopf)
        werte = sorted(block.werte, key=lambda w: w.x0)
        if len(spalten) != len(werte):
            raise IkvsQuerschnitteFehler(
                f"S. {block.pdf_seite}: {len(spalten)} Spalten {spalten}, aber {len(werte)} Werte"
            )
        for spalte, wort in zip(spalten, werte, strict=True):
            kennzahl = kennzahlen[block.plan].get(normalisiere(spalte))
            if kennzahl is None:
                raise IkvsQuerschnitteFehler(
                    f"S. {block.pdf_seite}: unbekannte Querschnitt-Spalte {spalte!r}"
                )
            datensaetze.append(
                {
                    "pb": pg_eltern.get(block.knoten),
                    "pg": block.knoten or None,
                    "gesamtsumme": not block.knoten,
                    "plan": block.plan,
                    "kennzahl": kennzahl,
                    "betrag": lies_ikvs_betrag(wort.text),
                    "pdf_seite": block.pdf_seite,
                }
            )

    fehlend = sorted(
        f"{pg} {plan}"
        for pg in pg_eltern
        for plan in ("ergebnisplan", "finanzplan")
        if (pg, plan) not in gesehen
    )
    if fehlend:
        raise IkvsQuerschnitteFehler(f"Querschnitte fehlen: {', '.join(fehlend)}")
    return pl.DataFrame(datensaetze, schema=QUERSCHNITTE_SPALTEN)
