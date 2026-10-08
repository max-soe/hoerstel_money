"""Leser für Haushaltspläne im IKVS-Layout (Word-Export, z. B. Stadt Hörstel).

Das IKVS-Layout unterscheidet sich vom ProFIS+-Layout (`ostbevern.plaene`) grundlegend:
kein "Nr."-Spaltenkopf und kein Eurozeichen, Zeilen der Form "01 - Bezeichnung", in einer
schmalen Spalte umbrochene Bezeichnungen (die Beträge stehen dann in einer eigenen
Zwischenzeile), "--" für leere Werte, Ist-Ergebnisse mit Cent und ein im Betrag
umbrochenes Minuszeichen ("-" am Ende der ersten Zeile, Betrag eine Zeile tiefer).

Beträge sind rechtsbündig in ihren Spalten gesetzt, die Jahreszahlen im Spaltenkopf
zentriert. Jedes Betragswort wird deshalb über seine Mitte der Spalte zugeordnet, deren
Bereich zwischen den Mitten der benachbarten Jahreszahlen liegt.

Das Zeilen-Wörterbuch dieses Moduls hält die gedruckten Bezeichnungen und ordnet jede
gedruckte Zeilennummer der kanonischen Zeilennummer aus `ostbevern.zeilen.ZEILEN` zu
(fachliche Regel, keine Jahrgangswerte). So bleiben Prüfregeln, Formeln und App-Daten
unabhängig vom Layout.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from ostbevern.konfiguration import Jahrgang, layout_liste
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import zerlege_spaltenkopf
from ostbevern.zeilen import ZEILEN, plantyp_fuer

SOFTWARE = "ikvs"

# Betrag im IKVS-Layout: Tausenderpunkte, optional Cent nach Komma, optional Minus.
_BETRAG_MUSTER = re.compile(r"^-?\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?$")
_LEERWERT = "--"
_MINUS = "-"
_ZEILENNUMMER_MUSTER = re.compile(r"^\d{1,2}$")
_WHITESPACE_MUSTER = re.compile(r"\s+")


class IkvsFehler(ValueError):
    """Wird ausgelöst, wenn eine IKVS-Planseite nicht eindeutig lesbar ist."""


@dataclass(frozen=True)
class IkvsZeile:
    """Gedruckte Zeile des IKVS-Wörterbuchs: Nummer (None = ungedruckt), Bezeichnung,
    kanonische Zeilennummer in `ostbevern.zeilen.ZEILEN`."""

    gedruckt: str | None
    bezeichnung: str
    kanonisch: str


@dataclass(frozen=True)
class IkvsPlanzeile:
    """Eine gelesene Planzeile: kanonische Zeilennummer, gedruckte Bezeichnung, Beträge."""

    zeile: str
    bezeichnung: str
    werte: tuple[int, ...]
    pdf_seite: int


def _z(gedruckt: str | None, bezeichnung: str, kanonisch: str | None = None) -> IkvsZeile:
    if kanonisch is None:
        if gedruckt is None:
            raise ValueError("ungedruckte Zeile braucht eine kanonische Nummer")
        kanonisch = f"{int(gedruckt):02d}"
    return IkvsZeile(gedruckt=gedruckt, bezeichnung=bezeichnung, kanonisch=kanonisch)


# Gedruckte Bezeichnungen der Gesamtpläne im IKVS-Layout (Muster nach KomHVO NRW, verifiziert
# gegen Hörstel 2026, PDF S. 79-81). Formelhinweise wie "(= Zeilen 9 und 16)" gehören zur
# gedruckten Bezeichnung. Der Gesamtfinanzplan nummeriert einstellig und druckt die
# fremden Finanzmittel ohne Nummer; "40 - Liquide Mittel" ist kanonisch Zeile 41.
IKVS_ZEILEN: dict[str, tuple[IkvsZeile, ...]] = {
    "gesamtergebnisplan": (
        _z("01", "Steuern und ähnliche Abgaben"),
        _z("02", "Zuwendungen und allgemeine Umlagen"),
        _z("03", "Sonstige Transfererträge"),
        _z("04", "Öffentlich-rechtliche Leistungsentgelte"),
        _z("05", "Privatrechtliche Leistungsentgelte"),
        _z("06", "Kostenerstattungen und -umlagen"),
        _z("07", "Sonstige ordentliche Erträge"),
        _z("08", "Aktivierte Eigenleistungen"),
        _z("09", "Bestandsveränderungen"),
        _z("10", "Ordentliche Erträge"),
        _z("11", "Personalaufwendungen"),
        _z("12", "Versorgungsaufwendungen"),
        _z("13", "Aufwendungen für Sach- und Dienstleistungen"),
        _z("14", "Bilanzielle Abschreibungen"),
        _z("15", "Transferaufwendungen"),
        _z("16", "Sonstige ordentliche Aufwendungen"),
        _z("17", "Ordentliche Aufwendungen"),
        _z("18", "Ordentliches Ergebnis"),
        _z("19", "Finanzerträge"),
        _z("20", "Zinsen und sonstige Finanzaufwendungen"),
        _z("21", "Finanzergebnis"),
        _z("22", "Ergebnis aus laufender Verwaltungstätigkeit"),
        _z("23", "Außerordentliche Erträge"),
        _z("24", "Außerordentliche Aufwendungen"),
        _z("25", "Außerordentliches Ergebnis"),
        _z("26", "Jahresergebnis"),
        _z("27", "globaler Minderaufwand"),
        _z("28", "Jahresergebnis nach Abzug globaler Minderaufwand"),
        _z("29", "Nachrichtlich: Verrechnete Erträge bei Vermögensgegenständen"),
        _z("30", "Nachrichtlich : Verrechnete Erträge bei Finanzanlagen"),
        _z("31", "Nachrichtlich: Verrechnete Aufwendungen bei Vermögensgegenständen"),
        _z("32", "Nachrichtlich : Verrechnete Aufwendungen bei Finanzanlagen"),
        _z("33", "Verrechnungssaldo"),
    ),
    "gesamtfinanzplan": (
        _z("1", "Steuern und ähnliche Abgaben"),
        _z("2", "Zuwendungen und allgemeine Umlagen"),
        _z("3", "Sonstige Transfereinzahlungen"),
        _z("4", "Öffentlich-rechtliche Leistungsentgelte"),
        _z("5", "Privatrechtliche Leistungsentgelte"),
        _z("6", "Kostenerstattungen und Kostenumlagen"),
        _z("7", "Sonstige Einzahlungen"),
        _z("8", "Zinsen und sonstige Finanzeinzahlungen"),
        _z("9", "Einzahlungen aus laufender Verwaltungstätigkeit"),
        _z("10", "Personalauszahlungen"),
        _z("11", "Versorgungsauszahlungen"),
        _z("12", "Auszahlungen für Sach- und Dienstleistungen"),
        _z("13", "Zinsen und Sonstige Finanzauszahlungen"),
        _z("14", "Transferauszahlungen"),
        _z("15", "Sonstige Auszahlungen"),
        _z("16", "Auszahlungen aus laufender Verwaltungstätigkeit*"),
        _z("17", "Saldo aus laufender Verwaltungstätigkeit (= Zeilen 9 und 16)"),
        _z("18", "Zuwendungen für Investitionsmaßnahmen"),
        _z("19", "Einzahlungen aus der Veräußerung von Sachanlagen"),
        _z("20", "Einzahlungen aus der Veräußerung von Finanzanlagen"),
        _z("21", "Einzahlungen aus Beiträgen und ähnlichen Entgelten"),
        _z("22", "Sonstige Investitionseinzahlungen"),
        _z("23", "Einzahlungen aus Investitionstätigkeit"),
        _z("24", "Auszahlungen für den Erwerb von Grundstücken und Gebäuden"),
        _z("25", "Auszahlungen für Baumaßnahmen"),
        _z("26", "Auszahlungen für den Erwerb von beweglichem Anlagevermögen"),
        _z("27", "Auszahlungen für den Erwerb von Finanzanlagen"),
        _z("28", "Auszahlungen von aktivierbaren Zuwendungen"),
        _z("29", "Sonstige Investitionsauszahlungen"),
        _z("30", "Auszahlungen aus Investitionstätigkeit"),
        _z("31", "Saldo aus Investitionstätigkeit (= Zeilen 23 und 30)"),
        _z("32", "Finanzmittelüberschuss/-fehlbetrag (= Zeilen 17 und 31)"),
        _z(
            "33",
            "Einzahlungen aus der Aufnahme und durch Rückflüsse von Krediten für "
            "Investitionen und diesen wirtschaftlich gleichkommenden Rechtsverhältnissen",
        ),
        _z("34", "Einzahlungen aus der Aufnahme von Krediten zur Liquiditätssicherung"),
        _z(
            "35",
            "Auszahlungen für die Tilgung und Gewährung von Krediten für Investitionen und "
            "diesen wirtschaftlich gleichkommenden Rechtsverhältnissen",
        ),
        _z("36", "Auszahlungen für die Tilgung von Krediten zur Liquiditätssicherung"),
        _z("37", "Saldo aus Finanzierungstätigkeit"),
        _z("38", "Änderung des Bestandes an eigenen Finanzmitteln (= Zeilen 32 und 37)"),
        _z("39", "Anfangsbestand an Finanzmitteln"),
        _z(None, "Änderung des Bestandes an fremden Finanzmitteln", "40"),
        _z("40", "Liquide Mittel (= Zeilen 38 und 39)", "41"),
    ),
}


def normalisiere(text: str) -> str:
    """Vergleichsform einer Bezeichnung: ohne Leerzeichen und Bindestriche (Silbentrennung)."""
    return _WHITESPACE_MUSTER.sub("", text).replace("-", "")


def lies_ikvs_betrag(text: str) -> int:
    """Liest einen IKVS-Betrag als int-Euro: "--" ist 0, Cent werden kaufmännisch gerundet."""
    if text == _LEERWERT:
        return 0
    if not _BETRAG_MUSTER.match(text):
        raise IkvsFehler(f"Kein gültiger IKVS-Betrag: {text!r}")
    dezimal = Decimal(text.replace(".", "").replace(",", "."))
    return int(dezimal.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _ist_wert_wort(text: str) -> bool:
    return text in (_LEERWERT, _MINUS) or bool(_BETRAG_MUSTER.match(text))


@dataclass(frozen=True)
class _Spalten:
    """Spaltengeometrie aus der Jahreszeile des Tabellenkopfs."""

    grenzen: tuple[float, ...]  # Untergrenze je Spalte (Wortmitte), aufsteigend

    def index(self, wort: Wort) -> int | None:
        mitte = (wort.x0 + wort.x1) / 2
        treffer = None
        for index, grenze in enumerate(self.grenzen):
            if mitte >= grenze:
                treffer = index
        return treffer


def _finde_tabellenkopf(
    zeilen: Sequence[Textzeile], gedruckte_spalten: Sequence[str], pdf_seite: int
) -> tuple[int, _Spalten]:
    """Sucht die zweizeilige Kopfzeile ("Ergebnis Ansatz ..." über "2024 2025 ...")."""
    bezeichnungen = [kopf.split()[0] for kopf in gedruckte_spalten]
    for index in range(len(zeilen) - 1):
        oben = [w.text for w in zeilen[index].woerter]
        if oben != bezeichnungen:
            continue
        jahreswoerter = zeilen[index + 1].woerter
        gelesen = [
            f"{bezeichnung} {wort.text}"
            for bezeichnung, wort in zip(bezeichnungen, jahreswoerter, strict=False)
        ]
        if len(jahreswoerter) != len(bezeichnungen) or gelesen != list(gedruckte_spalten):
            raise IkvsFehler(
                f"S. {pdf_seite}: Spaltenköpfe {gelesen} weichen von {list(gedruckte_spalten)} ab"
            )
        mitten = [(w.x0 + w.x1) / 2 for w in jahreswoerter]
        halbe_abstaende = [(b - a) / 2 for a, b in zip(mitten, mitten[1:], strict=False)]
        grenzen = [mitten[0] - halbe_abstaende[0]] + [
            mitte + halb for mitte, halb in zip(mitten, halbe_abstaende, strict=False)
        ]
        return index + 2, _Spalten(grenzen=tuple(grenzen))
    raise IkvsFehler(f"S. {pdf_seite}: kein Tabellenkopf {list(gedruckte_spalten)} gefunden")


class _OffeneZeile:
    """Eine im Aufbau befindliche Planzeile (Bezeichnung und Beträge über mehrere Textzeilen)."""

    def __init__(self, eintrag: IkvsZeile, spaltenanzahl: int, pdf_seite: int) -> None:
        self.eintrag = eintrag
        self.bezeichnung_teile: list[str] = []
        self.werte: list[int | None] = [None] * spaltenanzahl
        self.minus: list[bool] = [False] * spaltenanzahl
        self.pdf_seite = pdf_seite

    @property
    def bezeichnung(self) -> str:
        return " ".join(self.bezeichnung_teile)

    def passt(self, weitere: str) -> bool:
        kandidat = normalisiere(self.bezeichnung + weitere)
        return normalisiere(self.eintrag.bezeichnung).startswith(kandidat)

    def nimm_wert(self, spalte: int, text: str) -> None:
        nummer = self.eintrag.gedruckt or self.eintrag.bezeichnung
        if text == _MINUS:
            if self.minus[spalte] or self.werte[spalte] is not None:
                raise IkvsFehler(
                    f"S. {self.pdf_seite}, Zeile {nummer}: Minuszeichen ohne Betrag in "
                    f"Spalte {spalte + 1}"
                )
            self.minus[spalte] = True
            return
        if self.werte[spalte] is not None:
            raise IkvsFehler(
                f"S. {self.pdf_seite}, Zeile {nummer}: zwei Beträge in Spalte {spalte + 1}"
            )
        betrag = lies_ikvs_betrag(text)
        if self.minus[spalte]:
            if betrag < 0 or text == _LEERWERT:
                raise IkvsFehler(
                    f"S. {self.pdf_seite}, Zeile {nummer}: doppeltes Minuszeichen in "
                    f"Spalte {spalte + 1}"
                )
            betrag = -betrag
        self.werte[spalte] = betrag

    def schliesse(self) -> IkvsPlanzeile:
        nummer = self.eintrag.gedruckt or self.eintrag.bezeichnung
        if normalisiere(self.bezeichnung) != normalisiere(self.eintrag.bezeichnung):
            raise IkvsFehler(
                f"S. {self.pdf_seite}, Zeile {nummer}: Bezeichnung {self.bezeichnung!r} passt "
                f"nicht zum Wörterbuch ({self.eintrag.bezeichnung!r})"
            )
        if any(wert is None for wert in self.werte):
            raise IkvsFehler(
                f"S. {self.pdf_seite}, Zeile {nummer}: {self.werte.count(None)} Beträge fehlen"
            )
        return IkvsPlanzeile(
            zeile=self.eintrag.kanonisch,
            bezeichnung=self.bezeichnung,
            werte=tuple(wert for wert in self.werte if wert is not None),
            pdf_seite=self.pdf_seite,
        )


def lies_ikvs_plantabelle(
    zeilen: Sequence[Textzeile],
    *,
    plantyp: str,
    gedruckte_spalten: Sequence[str],
    pdf_seite: int,
) -> list[IkvsPlanzeile]:
    """Liest eine Gesamtplan-Seite im IKVS-Layout gegen das IKVS-Zeilen-Wörterbuch."""
    woerterbuch = IKVS_ZEILEN.get(plantyp)
    if woerterbuch is None:
        raise IkvsFehler(f"Kein IKVS-Zeilen-Wörterbuch für Plantyp {plantyp!r}")
    nach_nummer = {e.gedruckt: e for e in woerterbuch if e.gedruckt is not None}
    ungedruckt = [e for e in woerterbuch if e.gedruckt is None]

    start, spalten = _finde_tabellenkopf(zeilen, gedruckte_spalten, pdf_seite)
    gelesen: list[IkvsPlanzeile] = []
    offen: _OffeneZeile | None = None

    def schliesse_offene() -> None:
        nonlocal offen
        if offen is not None:
            gelesen.append(offen.schliesse())
            offen = None

    for zeile in zeilen[start:]:
        if zeile.text == str(pdf_seite):
            break
        bezeichnung_woerter: list[Wort] = []
        wert_woerter: list[tuple[int, Wort]] = []
        for wort in zeile.woerter:
            spalte = spalten.index(wort)
            if spalte is None:
                bezeichnung_woerter.append(wort)
            elif _ist_wert_wort(wort.text):
                wert_woerter.append((spalte, wort))
            else:
                raise IkvsFehler(
                    f"S. {pdf_seite}: Text {wort.text!r} in der Betragszone: {zeile.text!r}"
                )

        texte = [w.text for w in bezeichnung_woerter]
        if len(texte) >= 2 and _ZEILENNUMMER_MUSTER.match(texte[0]) and texte[1] == "-":
            schliesse_offene()
            eintrag = nach_nummer.get(texte[0])
            if eintrag is None:
                raise IkvsFehler(f"S. {pdf_seite}: unbekannte Zeilennummer {texte[0]!r}")
            offen = _OffeneZeile(eintrag, len(spalten.grenzen), pdf_seite)
            texte = texte[2:]
        elif texte:
            weitere = " ".join(texte)
            if offen is None or not offen.passt(weitere):
                passende = [
                    e
                    for e in ungedruckt
                    if normalisiere(e.bezeichnung).startswith(normalisiere(weitere))
                ]
                if len(passende) != 1:
                    raise IkvsFehler(
                        f"S. {pdf_seite}: unerwartete Zeile ohne Zeilennummer: {zeile.text!r}"
                    )
                schliesse_offene()
                offen = _OffeneZeile(passende[0], len(spalten.grenzen), pdf_seite)

        if offen is None:
            raise IkvsFehler(f"S. {pdf_seite}: Beträge ohne Zeile: {zeile.text!r}")
        if texte:
            offen.bezeichnung_teile.append(" ".join(texte))
        for spalte, wort in wert_woerter:
            offen.nimm_wert(spalte, wort.text)

    schliesse_offene()
    return gelesen


def gesamtplan_datensaetze(
    dokument: PdfDokument, jahrgang: Jahrgang, *, datei: str
) -> list[dict[str, object]]:
    """Liest Gesamtergebnis- oder Gesamtfinanzplan (IKVS) als Datensätze im Plan-Langformat.

    Die gedruckten Spaltenköpfe stehen unter `[layout.ikvs_gesamtplaene] {datei}_spalten`;
    sie werden positionsweise auf die kanonischen `[spalten] {datei}` abgebildet (z. B.
    gedruckt "Ansatz 2027" = kanonisch "Planung 2027", mittelfristige Finanzplanung).
    """
    plantyp = plantyp_fuer(datei, "GESAMT")
    bereich = jahrgang.seitenbereiche[plantyp]
    gedruckte_spalten = layout_liste(jahrgang, "ikvs_gesamtplaene", f"{datei}_spalten")
    spalten = jahrgang.spalten[datei]
    if len(gedruckte_spalten) != len(spalten):
        raise IkvsFehler(
            f"{datei}: {len(gedruckte_spalten)} gedruckte, aber {len(spalten)} kanonische Spalten"
        )
    for gedruckt, kanonisch in zip(gedruckte_spalten, spalten, strict=True):
        if zerlege_spaltenkopf(gedruckt)[1] != zerlege_spaltenkopf(kanonisch)[1]:
            raise IkvsFehler(f"{datei}: Spalte {gedruckt!r} passt nicht zu {kanonisch!r}")

    planzeilen: list[IkvsPlanzeile] = []
    for pdf_seite in range(bereich.von, bereich.bis + 1):
        planzeilen.extend(
            lies_ikvs_plantabelle(
                dokument.zeilen(pdf_seite),
                plantyp=plantyp,
                gedruckte_spalten=gedruckte_spalten,
                pdf_seite=pdf_seite,
            )
        )

    gesehen: set[str] = set()
    zeilen_definition = ZEILEN[plantyp]
    datensaetze: list[dict[str, object]] = []
    for planzeile in planzeilen:
        if planzeile.zeile in gesehen:
            raise IkvsFehler(f"{plantyp}: Zeile {planzeile.zeile} kommt zweimal vor")
        gesehen.add(planzeile.zeile)
        definition = zeilen_definition[planzeile.zeile]
        for spaltenkopf, betrag in zip(spalten, planzeile.werte, strict=True):
            wertart, jahr = zerlege_spaltenkopf(spaltenkopf)
            datensaetze.append(
                {
                    "ebene": "GESAMT",
                    "code": None,
                    "synthetisch": False,
                    "zeile": planzeile.zeile,
                    "zeile_kanonisch": definition.kanonisch,
                    "zeile_name": definition.name,
                    "operator": None,
                    "ist_summe": definition.ist_summe,
                    "jahr": jahr,
                    "wertart": wertart,
                    "betrag": betrag,
                    "pdf_seite": planzeile.pdf_seite,
                }
            )
    return datensaetze
