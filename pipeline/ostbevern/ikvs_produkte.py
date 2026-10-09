"""Produktinformationen, Kennzahlen und Erläuterungen im IKVS-Layout (z. B. Stadt Hörstel).

Produktinformationen (Seitentyp "produktinformationen", ggf. zwei Seiten je Produkt):
Feldbeschriftungen stehen allein auf einer Zeile ("Produktverantwortlicher", "Beschreibung",
"Auftragsgrundlage", "Zielgruppe", "Stellenplan", "Kennzahlen", "Ergänzende Erläuterungen");
der Inhalt folgt bis zur nächsten Beschriftung. Der Produktverantwortliche ist ein
Personenname und wird verworfen, bevor ein Datensatz entsteht (D-09). Die Beschreibung ist
meist eine Liste ("- ..."); Listenpunkte gehen nach `leistungen`, übriger Text nach
`beschreibung`. Felder, die das IKVS-Layout nicht kennt (Fachbereich, Gremium,
Bindungsgrad, Klassifizierung, Ziele), bleiben null. "Ergänzende Erläuterungen" (freie
Tabellen und Texte) werden nicht übernommen.

Die Tabellen "Stellenplan" (Vollzeitstellen je Planjahr) und "Kennzahlen" (Ist und Plan)
gehen als Gruppen nach `grundzahlen.csv`; `hinweis` = "Planwert" kennzeichnet Planwerte.
Tabellenzeilen werden über den vertikalen Abstand gebildet (umbrochene Bezeichnungen mit
den Werten in einer Zwischenzeile).

Erläuterungen (Seitentyp "erlaeuterungen"): Jede Überschrift steht unmittelbar über einer
Zeile "Ansatz 2025 = X €, Ansatz 2026 = Y €". Eine Überschrift, die eine Teilergebnisplan-
Zeile benennt, eröffnet einen Block mit dieser Zeile (`zu_zeilen`); Sachkonto-Überschriften
darunter gehören zum selben Block. Der Haushaltsjahr-Ansatz wird `betrag` der
Überschriftszeile; Text und Listenpunkte folgen als eigene Positionen ohne Betrag. Text vor
der ersten Überschrift ist ein allgemeiner Block ohne `zu_zeilen`.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from ostbevern.ikvs import (
    IKVS_ZEILEN,
    lies_tabellenkopf,
    normalisiere,
    verbinde_teile,
)
from ostbevern.konfiguration import Jahrgang, layout_liste, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import ERLAEUTERUNGEN_SPALTEN, GRUNDZAHLEN_SPALTEN
from ostbevern.zahlen import ZahlenFehler, lies_kennzahl
from ostbevern.zeilen import ZEILEN

# Zeilen derselben Tabellenzeile liegen ~4,7 pt auseinander, Tabellenzeilen ~13 pt.
_ZEILENABSTAND_TABELLE = 9.0
_LEERWERTE = ("--", "-")
_LISTENPUNKT = re.compile(r"^[-•]\s+")


class IkvsProdukteFehler(ValueError):
    """Wird ausgelöst, wenn Produktinformationen oder Erläuterungen nicht lesbar sind."""


@dataclass(frozen=True)
class _Felder:
    verantwortlich: str
    beschreibung: str
    auftragsgrundlage: str
    zielgruppe: str
    stellenplan: str
    kennzahlen: str
    ergaenzend: str


def _felder(jahrgang: Jahrgang) -> _Felder:
    def text(schluessel: str) -> str:
        return layout_text(jahrgang, "ikvs_produktinformationen", schluessel)

    return _Felder(
        verantwortlich=text("verantwortlich"),
        beschreibung=text("beschreibung"),
        auftragsgrundlage=text("auftragsgrundlage"),
        zielgruppe=text("zielgruppe"),
        stellenplan=text("stellenplan"),
        kennzahlen=text("kennzahlen"),
        ergaenzend=text("ergaenzend"),
    )


def _inhaltszeilen(dokument: PdfDokument, pdf_seite: int) -> list[Textzeile]:
    return [z for z in dokument.zeilen(pdf_seite)[1:] if z.text != str(pdf_seite)]


def _seiten_je_produkt(seiten: pl.DataFrame, typ: str) -> dict[str, list[int]]:
    ergebnis: dict[str, list[int]] = {}
    for zeile in (
        seiten.filter((pl.col("typ") == typ) & pl.col("produkt").is_not_null())
        .sort("pdf_seite")
        .iter_rows(named=True)
    ):
        ergebnis.setdefault(zeile["produkt"], []).append(zeile["pdf_seite"])
    return ergebnis


@dataclass(frozen=True)
class IkvsProduktinfo:
    code: str
    beschreibung: str | None
    leistungen: tuple[str, ...]
    auftragsgrundlage: str | None
    zielgruppe: str | None
    pdf_seiten: tuple[int, ...]


@dataclass(frozen=True)
class IkvsGrundzahl:
    produkt: str
    position: int
    gruppe: str
    bezeichnung: str
    jahr: int
    wert: float
    nachkommastellen: int
    hinweis: str | None
    pdf_seite: int


def _abschnitte(
    zeilen: Sequence[tuple[Textzeile, int]], felder: _Felder
) -> dict[str, list[tuple[Textzeile, int]]]:
    """Teilt die Zeilen der Produktinformationen nach Feldbeschriftungen auf."""
    beschriftungen = {
        felder.verantwortlich,
        felder.beschreibung,
        felder.auftragsgrundlage,
        felder.zielgruppe,
        felder.stellenplan,
        felder.kennzahlen,
        felder.ergaenzend,
    }
    abschnitte: dict[str, list[tuple[Textzeile, int]]] = {}
    aktuell: str | None = None
    for zeile, seite in zeilen:
        if zeile.text in beschriftungen:
            # "Ergänzende Erläuterungen" darf mehrfach vorkommen (S. 349); es wird nicht
            # übernommen. Jedes andere Feld genau einmal.
            if zeile.text in abschnitte and zeile.text != felder.ergaenzend:
                raise IkvsProdukteFehler(f"S. {seite}: Feld {zeile.text!r} doppelt")
            aktuell = zeile.text
            abschnitte.setdefault(aktuell, [])
        elif aktuell is not None:
            abschnitte[aktuell].append((zeile, seite))
    return abschnitte


def _fliesstext(zeilen: Sequence[tuple[Textzeile, int]]) -> str | None:
    text = verbinde_teile([z.text for z, _ in zeilen])
    return text or None


def _beschreibung(zeilen: Sequence[tuple[Textzeile, int]]) -> tuple[str | None, list[str]]:
    """Listenpunkte ("- ...") werden Leistungen, übriger Text die Beschreibung."""
    leistungen: list[list[str]] = []
    frei: list[str] = []
    for zeile, _ in zeilen:
        text = zeile.text
        if _LISTENPUNKT.match(text):
            leistungen.append([_LISTENPUNKT.sub("", text)])
        elif leistungen:
            leistungen[-1].append(text)
        else:
            frei.append(text)
    return (verbinde_teile(frei) or None), [verbinde_teile(teile) for teile in leistungen]


def _tabelle(
    zeilen: Sequence[tuple[Textzeile, int]],
    gedruckte_spalten: Sequence[str],
    *,
    produkt: str,
    gruppe: str,
    praefix: re.Pattern[str],
    start_position: int,
) -> list[IkvsGrundzahl]:
    """Liest eine Kennzahlentabelle (Kopf aus `gedruckte_spalten`, Zeilen mit sechs Werten)."""
    if not zeilen:
        return []
    nur_zeilen = [z for z, _ in zeilen]
    kopf = lies_tabellenkopf(nur_zeilen, 0, gedruckte_spalten, zeilen[0][1])
    if kopf is None:
        raise IkvsProdukteFehler(
            f"S. {zeilen[0][1]}: {gruppe} von Produkt {produkt} ohne Tabellenkopf "
            f"{list(gedruckte_spalten)}"
        )
    spalten, anzahl = kopf
    jahre = [int(k.split()[1]) for k in gedruckte_spalten]
    planwert = [k.split()[0] != "Ist" for k in gedruckte_spalten]

    gruppen: list[list[tuple[Textzeile, int]]] = []
    for zeile, seite in zeilen[anzahl:]:
        if (
            gruppen
            and gruppen[-1][-1][1] == seite
            and zeile.top - gruppen[-1][-1][0].top <= _ZEILENABSTAND_TABELLE
        ):
            gruppen[-1].append((zeile, seite))
        else:
            gruppen.append([(zeile, seite)])

    ergebnis: list[IkvsGrundzahl] = []
    for position, gruppe_zeilen in enumerate(gruppen, start=start_position):
        seite = gruppe_zeilen[0][1]
        beschriftung: list[str] = []
        werte: dict[int, str] = {}
        for zeile, _ in gruppe_zeilen:
            teile: list[str] = []
            for wort in zeile.woerter:
                spalte = spalten.index(wort)
                if spalte is None:
                    teile.append(wort.text)
                elif spalte in werte:
                    raise IkvsProdukteFehler(
                        f"S. {seite}: {gruppe} {produkt}: zwei Werte in Spalte {spalte + 1}"
                    )
                else:
                    werte[spalte] = wort.text
            if teile:
                beschriftung.append(" ".join(teile))
        bezeichnung = praefix.sub("", verbinde_teile(beschriftung))
        if not bezeichnung or len(werte) != len(gedruckte_spalten):
            raise IkvsProdukteFehler(
                f"S. {seite}: {gruppe} {produkt}: Zeile {bezeichnung!r} mit {len(werte)} von "
                f"{len(gedruckte_spalten)} Werten"
            )
        for spalte, text in sorted(werte.items()):
            if text in _LEERWERTE:
                continue
            try:
                wert, stellen = lies_kennzahl(text)
            except ZahlenFehler as fehler:
                raise IkvsProdukteFehler(
                    f"S. {seite}: {gruppe} {produkt}: {bezeichnung!r}: {fehler}"
                ) from fehler
            ergebnis.append(
                IkvsGrundzahl(
                    produkt=produkt,
                    position=position,
                    gruppe=gruppe,
                    bezeichnung=bezeichnung,
                    jahr=jahre[spalte],
                    wert=wert,
                    nachkommastellen=stellen,
                    hinweis="Planwert" if planwert[spalte] else None,
                    pdf_seite=seite,
                )
            )
    return ergebnis


def lies_ikvs_produktinformationen(
    dokument: PdfDokument, jahrgang: Jahrgang, seiten: pl.DataFrame
) -> tuple[list[IkvsProduktinfo], list[IkvsGrundzahl]]:
    """Liest Produktinformationen und Kennzahlentabellen aller Produkte."""
    felder = _felder(jahrgang)
    stellenplan_spalten = layout_liste(jahrgang, "ikvs_produktinformationen", "stellenplan_spalten")
    kennzahlen_spalten = layout_liste(jahrgang, "ikvs_produktinformationen", "kennzahlen_spalten")
    praefix = re.compile(
        layout_text(jahrgang, "ikvs_produktinformationen", "kennzahl_praefix_muster")
    )

    infos: list[IkvsProduktinfo] = []
    grundzahlen: list[IkvsGrundzahl] = []
    for produkt, pdf_seiten in sorted(_seiten_je_produkt(seiten, "produktinformationen").items()):
        zeilen = [(z, s) for s in pdf_seiten for z in _inhaltszeilen(dokument, s)]
        abschnitte = _abschnitte(zeilen, felder)
        if felder.verantwortlich not in abschnitte:
            raise IkvsProdukteFehler(
                f"S. {pdf_seiten[0]}: Produkt {produkt} ohne Feld {felder.verantwortlich!r}"
            )
        # D-09: den Personennamen nie weiterreichen.
        del abschnitte[felder.verantwortlich]
        beschreibung, leistungen = _beschreibung(abschnitte.get(felder.beschreibung, []))
        infos.append(
            IkvsProduktinfo(
                code=produkt,
                beschreibung=beschreibung,
                leistungen=tuple(leistungen),
                auftragsgrundlage=_fliesstext(abschnitte.get(felder.auftragsgrundlage, [])),
                zielgruppe=_fliesstext(abschnitte.get(felder.zielgruppe, [])),
                pdf_seiten=tuple(pdf_seiten),
            )
        )
        stellen = _tabelle(
            abschnitte.get(felder.stellenplan, []),
            stellenplan_spalten,
            produkt=produkt,
            gruppe=felder.stellenplan,
            praefix=praefix,
            start_position=1,
        )
        grundzahlen += stellen
        grundzahlen += _tabelle(
            abschnitte.get(felder.kennzahlen, []),
            kennzahlen_spalten,
            produkt=produkt,
            gruppe=felder.kennzahlen,
            praefix=praefix,
            start_position=max((g.position for g in stellen), default=0) + 1,
        )
    return infos, grundzahlen


@dataclass(frozen=True)
class IkvsErlaeuterung:
    produkt: str
    block: int
    position: int
    zu_zeilen: tuple[str, ...]
    betrag: int | None
    text: str
    pdf_seite: int


def _teilergebnisplan_zeilen() -> list[tuple[str, str]]:
    """(normalisierte Bezeichnung, Zeilennummer) aller Teilergebnisplan-Zeilen: gedruckte
    IKVS-Bezeichnungen ohne Formelhinweis und kanonische Namen."""
    paare: list[tuple[str, str]] = []
    for eintrag in IKVS_ZEILEN["teilergebnisplan"]:
        for bezeichnung in eintrag.bezeichnungen:
            ohne_formel = re.sub(r"\s*\((?:=\s*)?Zeilen[^)]*\)$", "", bezeichnung)
            paare.append((normalisiere(ohne_formel), eintrag.kanonisch))
    for zeile, definition in ZEILEN["teilergebnisplan"].items():
        paare.append((normalisiere(definition.name), zeile))
    return paare


def _zeile_fuer_ueberschrift(ueberschrift: str, paare: Sequence[tuple[str, str]]) -> str | None:
    """Teilergebnisplan-Zeile einer Überschrift: gleiche Bezeichnung oder ein Präfix davon
    ("Bilanzielle Abschreibung" = Z. 14 "Bilanzielle Abschreibungen")."""
    schluessel = normalisiere(ueberschrift)
    treffer = {zeile for bezeichnung, zeile in paare if bezeichnung == schluessel}
    if not treffer:
        treffer = {
            zeile
            for bezeichnung, zeile in paare
            if bezeichnung.startswith(schluessel) and len(schluessel) >= 10
        }
    return treffer.pop() if len(treffer) == 1 else None


class _Sammler:
    """Baut die Erläuterungspositionen eines Produkts auf (Block, Position, Absätze)."""

    def __init__(self, produkt: str, pdf_seite: int, ziel: list[IkvsErlaeuterung]) -> None:
        self.produkt = produkt
        self.ziel = ziel
        self.block = 0
        self.position = 0
        self.zu_zeilen: tuple[str, ...] = ()
        self.absatz: list[str] = []
        self.absatz_seite = pdf_seite

    def _neu(self, betrag: int | None, text: str, pdf_seite: int) -> None:
        self.position += 1
        self.ziel.append(
            IkvsErlaeuterung(
                self.produkt, self.block, self.position, self.zu_zeilen, betrag, text, pdf_seite
            )
        )

    def schreibe_absatz(self) -> None:
        if self.absatz:
            self._neu(None, verbinde_teile(self.absatz), self.absatz_seite)
            self.absatz = []

    def text(self, text: str, pdf_seite: int) -> None:
        if not self.absatz:
            self.absatz_seite = pdf_seite
        self.absatz.append(text)

    def ueberschrift(self, text: str, zeile_nr: str | None, betrag: int, pdf_seite: int) -> None:
        """Eine Teilergebnisplan-Überschrift eröffnet einen Block; eine Sachkonto-Überschrift
        bleibt im laufenden Block (vor der ersten Planzeile: eigener Block ohne Zeile)."""
        self.schreibe_absatz()
        if zeile_nr is not None or self.block == 0 or not self.zu_zeilen:
            self.block += 1
            self.zu_zeilen = (zeile_nr,) if zeile_nr is not None else ()
        self._neu(betrag, text, pdf_seite)


def lies_ikvs_erlaeuterungen(
    dokument: PdfDokument, jahrgang: Jahrgang, seiten: pl.DataFrame
) -> list[IkvsErlaeuterung]:
    """Liest die Erläuterungsseiten aller Produkte (Blöcke je Teilergebnisplan-Zeile)."""
    titel = layout_text(jahrgang, "ikvs_erlaeuterungen", "titel")
    ansatz_muster = re.compile(layout_text(jahrgang, "ikvs_erlaeuterungen", "ansatz_muster"))
    paare = _teilergebnisplan_zeilen()

    erlaeuterungen: list[IkvsErlaeuterung] = []
    for produkt, pdf_seiten in sorted(_seiten_je_produkt(seiten, "erlaeuterungen").items()):
        zeilen = [
            (z, s) for s in pdf_seiten for z in _inhaltszeilen(dokument, s) if z.text != titel
        ]
        ansatz_index = {
            i: m for i, (z, _) in enumerate(zeilen) if (m := ansatz_muster.match(z.text))
        }
        ueberschriften = {i - 1 for i in ansatz_index}
        if any(i < 0 or i in ansatz_index for i in ueberschriften):
            raise IkvsProdukteFehler(
                f"S. {pdf_seiten[0]}: Erläuterungen {produkt}: Ansatzzeile ohne Überschrift"
            )

        sammler = _Sammler(produkt, pdf_seiten[0], erlaeuterungen)
        if zeilen and 0 not in ueberschriften:
            sammler.block = 1
        for index, (zeile, seite) in enumerate(zeilen):
            if index in ansatz_index:
                continue
            text = zeile.text
            if index in ueberschriften:
                zeile_nr = _zeile_fuer_ueberschrift(text, paare)
                betrag = _ansatz_haushaltsjahr(
                    ansatz_index[index + 1], jahrgang.haushaltsjahr, seite
                )
                sammler.ueberschrift(text, zeile_nr, betrag, seite)
                continue
            if _LISTENPUNKT.match(text):
                sammler.schreibe_absatz()
                text = _LISTENPUNKT.sub("", text)
            sammler.text(text, seite)
        sammler.schreibe_absatz()
    return erlaeuterungen


def _ansatz_haushaltsjahr(treffer: re.Match[str], haushaltsjahr: int, pdf_seite: int) -> int | None:
    """Ansatz des Haushaltsjahres aus einer Ansatzzeile ("Ansatz Vorjahr = X €, Ansatz
    Haushaltsjahr = Y €"); der zweite Wert steht immer für das spätere Jahr.

    - Vorjahr/Haushaltsjahr (Regelfall): Y.
    - Zweimal das Vorjahr gedruckt (Tippfehler, z. B. S. 173 "Ansatz 2025 = 442.860 €,
      Ansatz 2025 = 498.890 €") oder ein verschriebenes erstes Jahr (S. 559 "20245"): Y.
    - Vorvorjahr/Vorjahr (Erläuterungen ausgelaufener Produkte, S. 282/314): kein
      Haushaltsjahr-Ansatz, None.
    """
    jahr1, jahr2 = treffer.group("jahr1"), int(treffer.group("jahr2"))
    betrag = int(treffer.group("betrag2").replace(".", ""))
    if jahr2 == haushaltsjahr:
        return betrag
    if jahr2 == haushaltsjahr - 1 and jahr1 == str(haushaltsjahr - 1):
        return betrag
    if jahr2 == haushaltsjahr - 1 and jahr1 == str(haushaltsjahr - 2):
        return None
    raise IkvsProdukteFehler(f"S. {pdf_seite}: Ansatzzeile {treffer.group(0)!r} nicht deutbar")


def grundzahlen_df(grundzahlen: Sequence[IkvsGrundzahl]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "produkt": g.produkt,
                "position": g.position,
                "gruppe": g.gruppe,
                "bezeichnung": g.bezeichnung,
                "einheit": None,
                "jahr": g.jahr,
                "wert": g.wert,
                "nachkommastellen": g.nachkommastellen,
                "hinweis": g.hinweis,
                "pdf_seite": g.pdf_seite,
            }
            for g in grundzahlen
        ],
        schema=GRUNDZAHLEN_SPALTEN,
    )


def erlaeuterungen_df(erlaeuterungen: Sequence[IkvsErlaeuterung]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "produkt": e.produkt,
                "block": e.block,
                "position": e.position,
                "zu_zeilen": "|".join(e.zu_zeilen) or None,
                "betrag": e.betrag,
                "text": e.text,
                "pdf_seite": e.pdf_seite,
            }
            for e in erlaeuterungen
        ],
        schema=ERLAEUTERUNGEN_SPALTEN,
    )


def produkte_datensaetze(
    infos: Sequence[IkvsProduktinfo],
    erlaeuterungen: Sequence[IkvsErlaeuterung],
    hierarchie: pl.DataFrame,
) -> list[dict[str, object]]:
    """produkte.json-Datensätze (PRODUKT_SCHLUESSEL) für alle Produkte der Hierarchie."""
    knoten = {z["code"]: z for z in hierarchie.filter(pl.col("ebene") == "P").iter_rows(named=True)}
    pg_eltern = {
        z["code"]: z["eltern_code"]
        for z in hierarchie.filter(pl.col("ebene") == "PG").iter_rows(named=True)
    }
    info_je_code = {info.code: info for info in infos}
    fehlend = sorted(set(knoten) - set(info_je_code))
    if fehlend:
        raise IkvsProdukteFehler(f"Produkte ohne Produktinformationen: {', '.join(fehlend)}")
    erlaeuterungen_je_code: dict[str, list[IkvsErlaeuterung]] = {}
    for erlaeuterung in erlaeuterungen:
        erlaeuterungen_je_code.setdefault(erlaeuterung.produkt, []).append(erlaeuterung)

    datensaetze: list[dict[str, object]] = []
    for code, eintrag in sorted(knoten.items()):
        info = info_je_code[code]
        eigene = erlaeuterungen_je_code.get(code, [])
        seiten = sorted(set(info.pdf_seiten) | {e.pdf_seite for e in eigene})
        datensaetze.append(
            {
                "code": code,
                "name": eintrag["name"],
                "pb": pg_eltern[eintrag["eltern_code"]],
                "pg": eintrag["eltern_code"],
                "fachbereich": None,
                "gremium": None,
                "beschreibung": info.beschreibung,
                "leistungen": list(info.leistungen),
                "auftragsgrundlage": info.auftragsgrundlage,
                "bindungsgrad": None,
                "bindungsgrad_original": None,
                "klassifizierung": None,
                "zielgruppe": info.zielgruppe,
                "ziele": None,
                "erlaeuterungen": [
                    {
                        "block": e.block,
                        "position": e.position,
                        "zu_zeilen": list(e.zu_zeilen),
                        "betrag": e.betrag,
                        "text": e.text,
                        "pdf_seite": e.pdf_seite,
                    }
                    for e in eigene
                ],
                "pdf_seiten": seiten,
            }
        )
    return datensaetze
