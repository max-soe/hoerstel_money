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

import polars as pl

from ostbevern.konfiguration import Jahrgang, layout_liste, layout_text
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import PLAN_SPALTEN, zerlege_spaltenkopf
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
    """Gedruckte Zeile des IKVS-Wörterbuchs: Nummer (None = ungedruckt), gedruckte
    Bezeichnungen (die erste ist die Regelform, weitere sind gedruckte Varianten) und
    kanonische Zeilennummer in `ostbevern.zeilen.ZEILEN`."""

    gedruckt: str | None
    bezeichnungen: tuple[str, ...]
    kanonisch: str

    @property
    def bezeichnung(self) -> str:
        return self.bezeichnungen[0]


@dataclass(frozen=True)
class IkvsPlanzeile:
    """Eine gelesene Planzeile: kanonische Zeilennummer, gedruckte Bezeichnung, Beträge."""

    zeile: str
    bezeichnung: str
    werte: tuple[int, ...]
    pdf_seite: int


def _z(gedruckt: str | None, *bezeichnungen: str, kanonisch: str | None = None) -> IkvsZeile:
    if kanonisch is None:
        if gedruckt is None:
            raise ValueError("ungedruckte Zeile braucht eine kanonische Nummer")
        kanonisch = f"{int(gedruckt):02d}"
    return IkvsZeile(gedruckt=gedruckt, bezeichnungen=bezeichnungen, kanonisch=kanonisch)


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
        _z(None, "Änderung des Bestandes an fremden Finanzmitteln", kanonisch="40"),
        _z("40", "Liquide Mittel (= Zeilen 38 und 39)", kanonisch="41"),
    ),
    # Teilpläne (PB und Produkt, Hörstel 2026 S. 111-566): nur belegte Zeilen sind gedruckt,
    # die Bezeichnungen stehen in einer schmalen Spalte. Weitere Bezeichnungen je Zeile sind
    # gedruckte Varianten. Teilergebnisplan
    # Z. 26 ist das Ergebnis vor internen Leistungsbeziehungen (kanonisch 26), Teilfinanzplan
    # Z. 32 der Finanzmittelüberschuss/-fehlbetrag, den nur die PB-Teilfinanzpläne drucken.
    "teilergebnisplan": (
        _z("1", "Steuern und ähnliche Abgaben"),
        _z("2", "Zuwendungen und allgemeine Umlagen"),
        _z("3", "Sonstige Transfererträge"),
        _z("4", "Öffentlich-rechtliche Leistungsentgelte"),
        _z("5", "Privatrechtliche Leistungsentgelte"),
        _z("6", "Kostenerstattungen und -umlagen, Leistungsbeteiligungen"),
        _z("7", "Sonstige ordentliche Erträge"),
        _z("8", "Aktivierte Eigenleistungen"),
        _z("10", "Ordentliche Erträge"),
        _z("11", "Personalaufwendungen"),
        _z("12", "Versorgungsaufwendungen"),
        _z("13", "Aufwendungen für Sach- und Dienstleistungen"),
        _z("14", "Bilanzielle Abschreibungen"),
        _z("15", "Transferaufwendungen"),
        _z("16", "Sonstige ordentliche Aufwendungen"),
        _z("17", "Ordentliche Aufwendungen"),
        _z("18", "Ordentliches Ergebnis (Zeilen 10 und 17)"),
        _z("19", "Finanzerträge"),
        _z("20", "Zinsen und sonstige Finanzaufwendungen"),
        _z("21", "Finanzergebnis (= Zeilen 19 und 20)"),
        _z("22", "Ergebnis aus laufender Verwaltungstätigkeit (Zeilen 18 und 21)"),
        _z(
            "26",
            "Ergebnis - vor Berücksichtigung der internen Leistungsbeziehungen "
            "(= Zeilen 22 und 25)",
        ),
        _z("27", "Erträge aus internen Leistungsbeziehungen"),
        _z("28", "Aufwendungen aus internen Leistungsbeziehungen"),
        _z("29", "Ergebnis (= Zeilen 26, 27 und 28)"),
        _z("31", "Teilergebnis nach Abzug globaler Minderaufwand (= Zeilen 29 und 30)"),
    ),
    "teilfinanzplan": (
        _z(
            "17",
            "Saldo aus laufender Verwaltungstätigkeit",
            "Saldo aus der Verwaltungstätigkeit",
            "Saldo aus Verwaltungstätigkeit",
        ),
        _z("18", "Zuwendungen für Investitionsmaßnahmen"),
        _z(
            "19",
            "Einzahlungen aus der Veräußerung von Sachanlagen",
            "Einzahlungen aus Veräußerung von Sachanlagen",
        ),
        _z(
            "21",
            "Einzahlungen aus Beiträgen und ähnlichen Entgelten",
            "Beiträge und ähnliche Entgelte",
        ),
        _z("22", "Sonstige Investitionseinzahlungen"),
        _z(
            "23",
            "Einzahlungen aus Investitionstätigkeit",
        ),
        _z("24", "Auszahlungen für den Erwerb von Grundstücken und Gebäuden"),
        _z("25", "Auszahlungen für Baumaßnahmen"),
        _z("26", "Auszahlungen für den Erwerb von beweglichem Anlagevermögen"),
        _z("27", "Auszahlungen für den Erwerb von Finanzanlagen"),
        _z("28", "Auszahlungen von aktivierbaren Zuwendungen"),
        _z("29", "Sonstige Investitionsauszahlungen"),
        _z(
            "30",
            "Auszahlungen aus Investitionstätigkeit",
        ),
        _z(
            "31",
            "Saldo aus Investitionstätigkeit",
        ),
        _z("32", "Finanzmittelüberschuss /-fehlbetrag"),
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
    """Spaltengeometrie eines Tabellenkopfs: Untergrenze (Wortmitte) je Spalte, aufsteigend."""

    grenzen: tuple[float, ...]

    @classmethod
    def aus_mitten(cls, mitten: Sequence[float]) -> _Spalten:
        halbe_abstaende = [(b - a) / 2 for a, b in zip(mitten, mitten[1:], strict=False)]
        grenzen = [mitten[0] - halbe_abstaende[0]] + [
            mitte + halb for mitte, halb in zip(mitten, halbe_abstaende, strict=False)
        ]
        return cls(grenzen=tuple(grenzen))

    def index(self, wort: Wort) -> int | None:
        mitte = (wort.x0 + wort.x1) / 2
        treffer = None
        for index, grenze in enumerate(self.grenzen):
            if mitte >= grenze:
                treffer = index
        return treffer


def _lies_tabellenkopf(
    zeilen: Sequence[Textzeile], index: int, gedruckte_spalten: Sequence[str], pdf_seite: int
) -> tuple[_Spalten, int] | None:
    """Erkennt einen Tabellenkopf ab Position `index` und liefert (Geometrie, Zeilenanzahl).

    Der Kopf besteht aus den Bezeichnungen ("Ergebnis", "Ansatz", "Plan") und Jahreszahlen der
    gedruckten Spalten, verteilt auf eine bis drei Textzeilen: einzeilig ("Ergebnis 2024
    Ansatz 2025 ...", Teilpläne), zweizeilig (Bezeichnungen über Jahren, Gesamtpläne) oder
    dreizeilig ("Ergebnis" / übrige Spalten / "2024", z. B. S. 511). Bezeichnungen und Jahre
    werden je nach x-Position einander zugeordnet; die Spaltenmitte ist die Mitte beider
    Wörter. Ein Kopf mit den erwarteten Bezeichnungen, aber anderen Jahren bricht ab.
    """
    bezeichnungen = [kopf.split()[0] for kopf in gedruckte_spalten]
    jahre = [kopf.split()[1] for kopf in gedruckte_spalten]
    erlaubt = set(bezeichnungen) | set(jahre)
    anzahl = len(gedruckte_spalten)

    woerter: list[Wort] = []
    for zeilenanzahl in range(1, 4):
        if index + zeilenanzahl > len(zeilen):
            return None
        neue = zeilen[index + zeilenanzahl - 1].woerter
        if not neue or any(not (w.text in erlaubt or w.text.isdigit()) for w in neue):
            return None
        woerter.extend(neue)
        bezeichnung_woerter = sorted(
            (w for w in woerter if not w.text.isdigit()), key=lambda w: w.x0
        )
        jahr_woerter = sorted((w for w in woerter if w.text.isdigit()), key=lambda w: w.x0)
        if len(bezeichnung_woerter) != anzahl or len(jahr_woerter) != anzahl:
            continue
        gelesen = [
            f"{b.text} {j.text}" for b, j in zip(bezeichnung_woerter, jahr_woerter, strict=True)
        ]
        if gelesen != list(gedruckte_spalten):
            raise IkvsFehler(
                f"S. {pdf_seite}: Spaltenköpfe {gelesen} weichen von {list(gedruckte_spalten)} ab"
            )
        mitten = [
            (min(b.x0, j.x0) + max(b.x1, j.x1)) / 2
            for b, j in zip(bezeichnung_woerter, jahr_woerter, strict=True)
        ]
        return _Spalten.aus_mitten(mitten), zeilenanzahl
    return None


class _OffeneZeile:
    """Eine im Aufbau befindliche Planzeile (Bezeichnung und Beträge über mehrere Textzeilen)."""

    def __init__(self, eintrag: IkvsZeile, spaltenanzahl: int, pdf_seite: int) -> None:
        self.eintrag = eintrag
        self.bezeichnung_teile: list[str] = []
        self.werte: list[int | None] = [None] * spaltenanzahl
        self.minus: list[bool] = [False] * spaltenanzahl
        self.pdf_seite = pdf_seite

    @property
    def nummer(self) -> str:
        return self.eintrag.gedruckt or self.eintrag.bezeichnung

    @property
    def bezeichnung(self) -> str:
        return " ".join(self.bezeichnung_teile)

    def passt(self, weitere: str) -> bool:
        kandidat = normalisiere(self.bezeichnung + weitere)
        return any(normalisiere(b).startswith(kandidat) for b in self.eintrag.bezeichnungen)

    def nimm_wert(self, spalte: int, text: str) -> None:
        if text == _MINUS:
            if self.minus[spalte] or self.werte[spalte] is not None:
                raise IkvsFehler(
                    f"S. {self.pdf_seite}, Zeile {self.nummer}: Minuszeichen ohne Betrag in "
                    f"Spalte {spalte + 1}"
                )
            self.minus[spalte] = True
            return
        if self.werte[spalte] is not None:
            raise IkvsFehler(
                f"S. {self.pdf_seite}, Zeile {self.nummer}: zwei Beträge in Spalte {spalte + 1}"
            )
        betrag = lies_ikvs_betrag(text)
        if self.minus[spalte]:
            if betrag < 0 or text == _LEERWERT:
                raise IkvsFehler(
                    f"S. {self.pdf_seite}, Zeile {self.nummer}: doppeltes Minuszeichen in "
                    f"Spalte {spalte + 1}"
                )
            betrag = -betrag
        self.werte[spalte] = betrag

    def schliesse(self) -> IkvsPlanzeile:
        gelesen = normalisiere(self.bezeichnung)
        if gelesen not in {normalisiere(b) for b in self.eintrag.bezeichnungen}:
            raise IkvsFehler(
                f"S. {self.pdf_seite}, Zeile {self.nummer}: Bezeichnung {self.bezeichnung!r} "
                f"passt nicht zum Wörterbuch ({self.eintrag.bezeichnung!r})"
            )
        if any(wert is None for wert in self.werte):
            raise IkvsFehler(
                f"S. {self.pdf_seite}, Zeile {self.nummer}: {self.werte.count(None)} Beträge fehlen"
            )
        return IkvsPlanzeile(
            zeile=self.eintrag.kanonisch,
            bezeichnung=self.bezeichnung,
            werte=tuple(wert for wert in self.werte if wert is not None),
            pdf_seite=self.pdf_seite,
        )


class _Tabellenleser:
    """Liest Planzeilen Textzeile für Textzeile gegen ein IKVS-Zeilen-Wörterbuch.

    Eine Zeile beginnt mit "NN -". Folgezeilen gehören zur offenen Zeile, solange die
    zusammengesetzte Bezeichnung ein Präfix einer Wörterbuchbezeichnung bleibt; sonst wird
    eine ungedruckte Zeile über ihre Bezeichnung erkannt. Ein einzelnes "-" in der
    Betragszone ist das Vorzeichen des Betrags derselben Spalte.
    """

    def __init__(self, plantyp: str) -> None:
        woerterbuch = IKVS_ZEILEN.get(plantyp)
        if woerterbuch is None:
            raise IkvsFehler(f"Kein IKVS-Zeilen-Wörterbuch für Plantyp {plantyp!r}")
        self._nach_nummer = {e.gedruckt: e for e in woerterbuch if e.gedruckt is not None}
        self._ungedruckt = [e for e in woerterbuch if e.gedruckt is None]
        self._offen: _OffeneZeile | None = None
        self.gelesen: list[IkvsPlanzeile] = []

    def schliesse(self) -> None:
        if self._offen is not None:
            self.gelesen.append(self._offen.schliesse())
            self._offen = None

    def lies(self, zeile: Textzeile, spalten: _Spalten, pdf_seite: int) -> None:
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
            self.schliesse()
            eintrag = self._nach_nummer.get(texte[0])
            if eintrag is None:
                raise IkvsFehler(f"S. {pdf_seite}: unbekannte Zeilennummer {texte[0]!r}")
            self._offen = _OffeneZeile(eintrag, len(spalten.grenzen), pdf_seite)
            texte = texte[2:]
        elif texte:
            weitere = " ".join(texte)
            if self._offen is None or not self._offen.passt(weitere):
                passende = [
                    e
                    for e in self._ungedruckt
                    if any(
                        normalisiere(b).startswith(normalisiere(weitere)) for b in e.bezeichnungen
                    )
                ]
                if len(passende) != 1:
                    raise IkvsFehler(
                        f"S. {pdf_seite}: unerwartete Zeile ohne Zeilennummer: {zeile.text!r}"
                    )
                self.schliesse()
                self._offen = _OffeneZeile(passende[0], len(spalten.grenzen), pdf_seite)

        if self._offen is None:
            raise IkvsFehler(f"S. {pdf_seite}: Beträge ohne Zeile: {zeile.text!r}")
        if texte:
            self._offen.bezeichnung_teile.append(" ".join(texte))
        for spalte, wort in wert_woerter:
            self._offen.nimm_wert(spalte, wort.text)


def lies_ikvs_plantabelle(
    zeilen: Sequence[Textzeile],
    *,
    plantyp: str,
    gedruckte_spalten: Sequence[str],
    pdf_seite: int,
) -> list[IkvsPlanzeile]:
    """Liest eine Gesamtplan-Seite im IKVS-Layout gegen das IKVS-Zeilen-Wörterbuch."""
    for index in range(len(zeilen)):
        kopf = _lies_tabellenkopf(zeilen, index, gedruckte_spalten, pdf_seite)
        if kopf is not None:
            spalten, anzahl = kopf
            start = index + anzahl
            break
    else:
        raise IkvsFehler(f"S. {pdf_seite}: kein Tabellenkopf {list(gedruckte_spalten)} gefunden")

    leser = _Tabellenleser(plantyp)
    for zeile in zeilen[start:]:
        if zeile.text == str(pdf_seite):
            break
        leser.lies(zeile, spalten, pdf_seite)
    leser.schliesse()
    return leser.gelesen


def _pruefe_spaltenabbildung(gedruckte_spalten: Sequence[str], spalten: Sequence[str]) -> None:
    if len(gedruckte_spalten) != len(spalten):
        raise IkvsFehler(
            f"{len(gedruckte_spalten)} gedruckte, aber {len(spalten)} kanonische Spalten"
        )
    for gedruckt, kanonisch in zip(gedruckte_spalten, spalten, strict=True):
        if gedruckt.split()[-1] != str(zerlege_spaltenkopf(kanonisch)[1]):
            raise IkvsFehler(f"Spalte {gedruckt!r} passt nicht zu {kanonisch!r}")


def _datensaetze(
    planzeilen: Sequence[IkvsPlanzeile],
    *,
    plantyp: str,
    ebene: str,
    code: str | None,
    spalten: Sequence[str],
    synthetisch: bool = False,
) -> list[dict[str, object]]:
    gesehen: set[str] = set()
    zeilen_definition = ZEILEN[plantyp]
    datensaetze: list[dict[str, object]] = []
    for planzeile in planzeilen:
        if planzeile.zeile in gesehen:
            raise IkvsFehler(
                f"{plantyp} {code or ebene}: Zeile {planzeile.zeile} kommt zweimal vor"
            )
        gesehen.add(planzeile.zeile)
        definition = zeilen_definition[planzeile.zeile]
        for spaltenkopf, betrag in zip(spalten, planzeile.werte, strict=True):
            wertart, jahr = zerlege_spaltenkopf(spaltenkopf)
            datensaetze.append(
                {
                    "ebene": ebene,
                    "code": code,
                    "synthetisch": synthetisch,
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
    _pruefe_spaltenabbildung(gedruckte_spalten, spalten)

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
    return _datensaetze(planzeilen, plantyp=plantyp, ebene="GESAMT", code=None, spalten=spalten)


@dataclass(frozen=True)
class IkvsTeilplan:
    """Ein gelesener Teilergebnis- oder Teilfinanzplan eines PB oder Produkts."""

    plantyp: str
    code: str
    name: str
    pdf_seite: int
    zeilen: tuple[IkvsPlanzeile, ...]


class _OffenerTeilplan:
    def __init__(self, plantyp: str, code: str, name: str, pdf_seite: int) -> None:
        self.plantyp = plantyp
        self.code = code
        self.name_teile = [name]
        self.pdf_seite = pdf_seite
        self.leser = _Tabellenleser(plantyp)
        self.hat_kopf = False

    def schliesse(self) -> IkvsTeilplan:
        if not self.hat_kopf:
            raise IkvsFehler(f"S. {self.pdf_seite}: {self.plantyp} {self.code} ohne Tabellenkopf")
        self.leser.schliesse()
        return IkvsTeilplan(
            plantyp=self.plantyp,
            code=self.code,
            name=" ".join(self.name_teile),
            pdf_seite=self.pdf_seite,
            zeilen=tuple(self.leser.gelesen),
        )


def lies_ikvs_teilplaene(dokument: PdfDokument, jahrgang: Jahrgang) -> list[IkvsTeilplan]:
    """Liest alle Teilergebnis- und Teilfinanzpläne des Teilplanbereichs (IKVS).

    Ein Abschnitt beginnt mit seinem Titel ("Teilergebnisplan 0111101 - Name"), dessen Name
    umbrechen kann, und endet am nächsten Titel oder an einem Abschnittsende-Muster
    (Investitionsübersicht, Erläuterungen, Trenn- und Produktseiten). Er darf über eine
    Seitengrenze laufen; jede Seite wiederholt dann den Tabellenkopf. Auch eine einzelne
    Planzeile kann auf der Folgeseite weiterlaufen (S. 169/170).
    """
    bereich = jahrgang.seitenbereiche["teilplaene"]
    gedruckte_spalten = layout_liste(jahrgang, "ikvs_teilplaene", "spalten")
    _pruefe_spaltenabbildung(gedruckte_spalten, jahrgang.spalten["ergebnisplan"])
    _pruefe_spaltenabbildung(gedruckte_spalten, jahrgang.spalten["finanzplan"])
    titel_muster = {
        plantyp: re.compile(layout_text(jahrgang, "ikvs_teilplaene", f"{plantyp}_muster"))
        for plantyp in ("teilergebnisplan", "teilfinanzplan")
    }
    ende_muster = re.compile(layout_text(jahrgang, "ikvs_teilplaene", "abschnitt_ende_muster"))

    teilplaene: list[IkvsTeilplan] = []
    offen: _OffenerTeilplan | None = None
    for pdf_seite in range(bereich.von, bereich.bis + 1):
        zeilen = [z for z in dokument.zeilen(pdf_seite)[1:] if z.text != str(pdf_seite)]
        spalten: _Spalten | None = None
        index = 0
        while index < len(zeilen):
            zeile = zeilen[index]
            treffer = next(
                (
                    (plantyp, m)
                    for plantyp, muster in titel_muster.items()
                    if (m := muster.match(zeile.text))
                ),
                None,
            )
            if treffer is not None or ende_muster.match(zeile.text):
                if offen is not None:
                    teilplaene.append(offen.schliesse())
                    offen = None
                if treffer is not None:
                    plantyp, m = treffer
                    offen = _OffenerTeilplan(plantyp, m.group(1), m.group(2), pdf_seite)
                spalten = None
                index += 1
                continue
            if offen is None:
                index += 1
                continue
            kopf = _lies_tabellenkopf(zeilen, index, gedruckte_spalten, pdf_seite)
            if kopf is not None:
                spalten, anzahl = kopf
                offen.hat_kopf = True
                index += anzahl
                continue
            if spalten is None:
                if offen.hat_kopf:
                    raise IkvsFehler(
                        f"S. {pdf_seite}: Zeile vor dem Tabellenkopf in {offen.plantyp} "
                        f"{offen.code}: {zeile.text!r}"
                    )
                offen.name_teile.append(zeile.text)
                index += 1
                continue
            offen.leser.lies(zeile, spalten, pdf_seite)
            index += 1
    if offen is not None:
        teilplaene.append(offen.schliesse())
    return teilplaene


def teilplan_datensaetze(
    teilplaene: Sequence[IkvsTeilplan], hierarchie: pl.DataFrame, jahrgang: Jahrgang
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Baut Teilergebnis- und Teilfinanzplan-Datensätze (PB, PG, Produkt) im Langformat.

    Jeder PB und jedes Produkt braucht genau einen Teilergebnis- und einen Teilfinanzplan,
    deren Titelname zur Hierarchie passt (D-08). Zwei abgeleitete, als `synthetisch`
    markierte Zeilenarten ergänzen die gedruckten Werte:
    - PB-Teilfinanzpläne drucken Z. 32 (Finanzmittelüberschuss), aber nicht Z. 17 (Saldo
      aus laufender Verwaltungstätigkeit); Z. 17 = Z. 32 - Z. 31.
    - Produktgruppen haben keinen eigenen Teilplan; ihre Werte sind die Summe ihrer
      Produkte (Mitgliedschaft aus `hierarchie.eltern_code`).
    """
    knoten = {
        zeile["code"]: zeile
        for zeile in hierarchie.filter(pl.col("ebene").is_in(["PB", "P"])).iter_rows(named=True)
    }
    gesehen: dict[tuple[str, str], int] = {}
    teile: dict[str, list[dict[str, object]]] = {"ergebnisplan": [], "finanzplan": []}
    for teilplan in teilplaene:
        eintrag = knoten.get(teilplan.code)
        if eintrag is None:
            raise IkvsFehler(
                f"S. {teilplan.pdf_seite}: {teilplan.plantyp} {teilplan.code} gehört zu keinem "
                "PB oder Produkt der Hierarchie"
            )
        schluessel = (teilplan.plantyp, teilplan.code)
        if schluessel in gesehen:
            raise IkvsFehler(
                f"{teilplan.plantyp} {teilplan.code} kommt auf S. {gesehen[schluessel]} und "
                f"S. {teilplan.pdf_seite} vor"
            )
        gesehen[schluessel] = teilplan.pdf_seite
        if normalisiere(teilplan.name) != normalisiere(eintrag["name"]):
            raise IkvsFehler(
                f"S. {teilplan.pdf_seite}: Titel {teilplan.name!r} passt nicht zum Namen "
                f"{eintrag['name']!r} von {teilplan.code}"
            )
        datei = "ergebnisplan" if teilplan.plantyp == "teilergebnisplan" else "finanzplan"
        spalten = jahrgang.spalten[datei]
        teile[datei] += _datensaetze(
            teilplan.zeilen,
            plantyp=teilplan.plantyp,
            ebene=eintrag["ebene"],
            code=teilplan.code,
            spalten=spalten,
        )
        gedruckt = {z.zeile: z for z in teilplan.zeilen}
        if teilplan.plantyp == "teilfinanzplan" and "17" not in gedruckt and "32" in gedruckt:
            z31 = gedruckt.get("31")
            werte = tuple(
                a - (z31.werte[i] if z31 else 0) for i, a in enumerate(gedruckt["32"].werte)
            )
            abgeleitet = IkvsPlanzeile(
                zeile="17",
                bezeichnung="abgeleitet: Z. 32 - Z. 31",
                werte=werte,
                pdf_seite=gedruckt["32"].pdf_seite,
            )
            teile[datei] += _datensaetze(
                [abgeleitet],
                plantyp=teilplan.plantyp,
                ebene=eintrag["ebene"],
                code=teilplan.code,
                spalten=spalten,
                synthetisch=True,
            )

    for code, eintrag in knoten.items():
        for plantyp in ("teilergebnisplan", "teilfinanzplan"):
            if (plantyp, code) not in gesehen:
                raise IkvsFehler(f"{eintrag['ebene']} {code}: kein {plantyp} gefunden")

    ergebnis: list[pl.DataFrame] = []
    for datei in ("ergebnisplan", "finanzplan"):
        df = pl.DataFrame(teile[datei], schema=PLAN_SPALTEN)
        ergebnis.append(pl.concat([df, _pg_summen(df, hierarchie)]))
    return ergebnis[0], ergebnis[1]


def _pg_summen(teil_df: pl.DataFrame, hierarchie: pl.DataFrame) -> pl.DataFrame:
    """PG-Zeilen als Summe der Produktzeilen je Zeile, Jahr und Wertart (synthetisch)."""
    produkte = hierarchie.filter(pl.col("ebene") == "P").select(
        pl.col("code"), pl.col("eltern_code").alias("pg")
    )
    pg_seiten = hierarchie.filter(pl.col("ebene") == "PG").select(
        pl.col("code").alias("pg"), pl.col("pdf_seite_start").alias("pdf_seite")
    )
    summen = (
        teil_df.filter(pl.col("ebene") == "P")
        .join(produkte, on="code", how="inner")
        .group_by(["pg", "zeile", "zeile_kanonisch", "zeile_name", "ist_summe", "jahr", "wertart"])
        .agg(pl.col("betrag").sum())
        .join(pg_seiten, on="pg", how="inner")
    )
    return summen.select(
        pl.lit("PG").alias("ebene"),
        pl.col("pg").alias("code"),
        pl.lit(True).alias("synthetisch"),
        "zeile",
        "zeile_kanonisch",
        "zeile_name",
        pl.lit(None, dtype=pl.Utf8).alias("operator"),
        "ist_summe",
        "jahr",
        "wertart",
        "betrag",
        "pdf_seite",
    ).cast(PLAN_SPALTEN)
