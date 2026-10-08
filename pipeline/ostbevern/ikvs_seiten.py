"""Schritt 01 im IKVS-Layout: Seitenklassifikation und Hierarchie (z. B. Stadt Hörstel).

Das IKVS-Layout hat keine laufende Kopfzeile. Der Teilplanbereich ist eine Folge von
Abschnitten: eine Trennseite "Produktbereich" mit Code und Name, die Teilergebnis- und
Teilfinanzpläne des Produktbereichs, dann je Produkt eine Trennseite "Produkt", die
Produktinformationen, Teilergebnis- und Teilfinanzplan, ggf. die Investitionsübersicht und
die Erläuterungen. Der Kontext (PB, Produkt) wird deshalb von Seite zu Seite fortgeschrieben;
jeder gedruckte Titel wird gegen diesen Kontext geprüft (D-08).

Seitentyp ist der Titel in der ersten Inhaltszeile; eine Seite ohne Titel dort setzt den
letzten Abschnitt der Vorseite fort. Trennseiten erhalten den Typ "trennseite".

Produktgruppen haben im IKVS-Layout keine eigenen Teilpläne. Code und Name stehen nur im
Feld "Produktgruppe" der Produktinformationen; in `hierarchie.csv` sind sie deshalb als
`synthetisch` markiert (die PG-Planwerte bildet Schritt 02 als Summe ihrer Produkte).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from ostbevern.ikvs import normalisiere
from ostbevern.konfiguration import Jahrgang, Seitenbereich, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import HIERARCHIE_SPALTEN

TRENNSEITE = "trennseite"
_PB_FELD_BEGINN = "Produktbe-"
_PB_FELD_ENDE = "reich"
_PG_FELD_BEGINN = "Produkt-"
_PG_FELD_ENDE = "gruppe"


class IkvsSeitenFehler(ValueError):
    """Wird ausgelöst, wenn eine Teilplanseite nicht zum fortgeschriebenen Kontext passt."""


@dataclass(frozen=True)
class IkvsSeite:
    """Eine klassifizierte PDF-Seite (gleiche Felder wie `ostbevern.seiten.Seite`)."""

    pdf_seite: int
    typ: str
    pb: str | None
    pg: str | None
    produkt: str | None


@dataclass
class _Knoten:
    name: str
    pdf_seite_start: int
    eltern_code: str | None


def _kapitel_fuer_seite(pdf_seite: int, seitenbereiche: dict[str, Seitenbereich]) -> str | None:
    for name, bereich in seitenbereiche.items():
        if bereich.von <= pdf_seite <= bereich.bis:
            return name
    return None


def _inhaltszeilen(dokument: PdfDokument, pdf_seite: int) -> list[Textzeile]:
    """Zeilen ohne Kopfzeile ("Haushaltsplan 2026 Hörstel") und ohne Seitenzahl."""
    return [z for z in dokument.zeilen(pdf_seite)[1:] if z.text != str(pdf_seite)]


def _feldwert(zeilen: Sequence[Textzeile], beginn: str, ende: str) -> str | None:
    """Text eines zweizeilig beschrifteten Feldes ("Produkt-" / Wert / "gruppe")."""
    texte = [z.text for z in zeilen]
    if beginn not in texte:
        return None
    start = texte.index(beginn) + 1
    teile: list[str] = []
    for text in texte[start:]:
        if text == ende:
            return " ".join(teile)
        teile.append(text)
    return None


def _gleich(a: str, b: str) -> bool:
    return normalisiere(a) == normalisiere(b)


class _Klassifizierer:
    def __init__(self, jahrgang: Jahrgang) -> None:
        kopfzeilen = jahrgang.kopfzeilen
        self.pb_muster = re.compile(kopfzeilen.produktbereich)
        self.pg_muster = re.compile(kopfzeilen.produktgruppe)
        self.produkt_muster = re.compile(kopfzeilen.produkt)
        self.titel_muster = {
            typ: re.compile(layout_text(jahrgang, "ikvs_teilplaene", f"{typ}_muster"))
            for typ in ("teilergebnisplan", "teilfinanzplan", "investitionen", "erlaeuterungen")
        }
        self.pb: str | None = None
        self.produkt: str | None = None
        self.pb_knoten: dict[str, _Knoten] = {}
        self.p_knoten: dict[str, _Knoten] = {}
        self.pg_knoten: dict[str, _Knoten] = {}
        self.pg_von_produkt: dict[str, str] = {}

    def _titel(self, zeile: Textzeile, pdf_seite: int) -> str | None:
        """Typ eines Abschnittstitels in `zeile` (geprüft gegen den Kontext) oder None."""
        for typ, muster in self.titel_muster.items():
            treffer = muster.match(zeile.text)
            if treffer is None:
                continue
            if typ == "erlaeuterungen":
                return typ
            code = treffer.group(1)
            erwartet = self.produkt or self.pb
            if code != erwartet:
                raise IkvsSeitenFehler(
                    f"S. {pdf_seite}: Titel {zeile.text!r} passt nicht zum Kontext {erwartet!r}"
                )
            if typ == "investitionen":
                return "investitionen_produkt" if self.produkt else "investitionen_pb"
            return typ
        return None

    def _trennseite(self, zeilen: Sequence[Textzeile], pdf_seite: int) -> None:
        text = " ".join(z.text for z in zeilen)
        if zeilen[0].text == "Produktbereich":
            treffer = self.pb_muster.match(text)
            if treffer is None:
                raise IkvsSeitenFehler(f"S. {pdf_seite}: unlesbare PB-Trennseite {text!r}")
            code, name = treffer.groups()
            if code in self.pb_knoten:
                raise IkvsSeitenFehler(f"S. {pdf_seite}: Produktbereich {code} doppelt")
            self.pb, self.produkt = code, None
            # Startseite ist die Planseite mit dem Kopf "Produktbereich NN Name" (wie im
            # Inhaltsverzeichnis), nicht die Trennseite; gesetzt in `klassifiziere`.
            self.pb_knoten[code] = _Knoten(name=name, pdf_seite_start=0, eltern_code=None)
            return
        treffer = self.produkt_muster.match(text)
        if treffer is None:
            raise IkvsSeitenFehler(f"S. {pdf_seite}: unlesbare Produkt-Trennseite {text!r}")
        code, name = treffer.groups()
        if self.pb is None or not code.startswith(self.pb):
            raise IkvsSeitenFehler(
                f"S. {pdf_seite}: Produkt {code} passt nicht zum Produktbereich {self.pb!r}"
            )
        if code in self.p_knoten:
            raise IkvsSeitenFehler(f"S. {pdf_seite}: Produkt {code} doppelt")
        self.produkt = code
        # Startseite sind die Produktinformationen, gesetzt in `_produktinformationen`.
        self.p_knoten[code] = _Knoten(name=name, pdf_seite_start=0, eltern_code=None)

    def _produktinformationen(self, zeilen: Sequence[Textzeile], pdf_seite: int) -> None:
        treffer = self.produkt_muster.match(zeilen[0].text)
        assert treffer is not None
        code, name = treffer.groups()
        # Maßgeblich ist der Name der Produktinformationen (so auch in den Teilplantiteln);
        # die Trennseite kürzt mitunter anders ("und" statt "u.", S. 555/556).
        if code != self.produkt:
            raise IkvsSeitenFehler(
                f"S. {pdf_seite}: Produktinformationen {code} {name!r} passen nicht zum "
                f"Kontext {self.produkt!r}"
            )
        pb_feld = _feldwert(zeilen, _PB_FELD_BEGINN, _PB_FELD_ENDE)
        pb_name = self.pb_knoten[self.pb].name if self.pb else ""
        if pb_feld is None or not _gleich(pb_feld, f"{self.pb} {pb_name}"):
            raise IkvsSeitenFehler(
                f"S. {pdf_seite}: Feld Produktbereich {pb_feld!r} passt nicht zu {self.pb!r}"
            )
        pg_feld = _feldwert(zeilen, _PG_FELD_BEGINN, _PG_FELD_ENDE)
        pg_treffer = self.pg_muster.match(pg_feld or "")
        if pg_treffer is None:
            raise IkvsSeitenFehler(f"S. {pdf_seite}: Feld Produktgruppe {pg_feld!r} unlesbar")
        pg_code, pg_name = pg_treffer.groups()
        if not (code.startswith(pg_code) and pg_code.startswith(self.pb or "-")):
            raise IkvsSeitenFehler(
                f"S. {pdf_seite}: Produktgruppe {pg_code} passt nicht zu Produkt {code}"
            )
        vorhanden = self.pg_knoten.get(pg_code)
        if vorhanden is None:
            self.pg_knoten[pg_code] = _Knoten(
                name=pg_name,
                pdf_seite_start=pdf_seite,
                eltern_code=self.pb,
            )
        elif not _gleich(vorhanden.name, pg_name):
            raise IkvsSeitenFehler(
                f"S. {pdf_seite}: Produktgruppe {pg_code} heißt {pg_name!r}, vorher "
                f"{vorhanden.name!r}"
            )
        if code in self.pg_von_produkt:
            raise IkvsSeitenFehler(f"S. {pdf_seite}: Produktinformationen {code} doppelt")
        self.pg_von_produkt[code] = pg_code
        self.p_knoten[code].name = name
        self.p_knoten[code].pdf_seite_start = pdf_seite
        self.p_knoten[code].eltern_code = pg_code

    def klassifiziere(
        self, zeilen: Sequence[Textzeile], pdf_seite: int, letzter_typ: str | None
    ) -> tuple[str, str | None]:
        """Liefert (Seitentyp, Typ des letzten Abschnitts der Seite)."""
        if not zeilen:
            return letzter_typ or "unbekannt", letzter_typ
        erste = zeilen[0].text
        # Trennseiten: "Produktbereich" bzw. "Produkt" allein in einer Zeile, darunter Code und
        # Name; auf S. 111 steht davor noch die Kapitelüberschrift.
        trenner = [i for i, z in enumerate(zeilen) if z.text in ("Produktbereich", "Produkt")]
        if trenner:
            self._trennseite(zeilen[trenner[0] :], pdf_seite)
            return TRENNSEITE, TRENNSEITE

        typ: str | None
        rest = zeilen
        if self.produkt_muster.match(erste):
            self._produktinformationen(zeilen, pdf_seite)
            typ, rest = "produktinformationen", zeilen[1:]
        elif (treffer := self.pb_muster.match(erste)) is not None:
            code, name = treffer.groups()
            if (
                self.produkt is not None
                or code != self.pb
                or not _gleich(name, self.pb_knoten[code].name)
            ):
                raise IkvsSeitenFehler(
                    f"S. {pdf_seite}: Kopf {erste!r} passt nicht zum Kontext {self.pb!r}"
                )
            if self.pb_knoten[code].pdf_seite_start == 0:
                self.pb_knoten[code].pdf_seite_start = pdf_seite
            rest = zeilen[1:]
            typ = self._titel(rest[0], pdf_seite) if rest else None
        else:
            typ = self._titel(zeilen[0], pdf_seite)

        letzter = typ
        for zeile in rest:
            titel = self._titel(zeile, pdf_seite)
            if titel is not None:
                letzter = titel
        if typ is None:
            typ = letzter_typ or "unbekannt"
            letzter = letzter or letzter_typ
        return typ, letzter


def klassifiziere_dokument_ikvs(
    dokument: PdfDokument, jahrgang: Jahrgang
) -> tuple[tuple[IkvsSeite, ...], pl.DataFrame]:
    """Klassifiziert alle Seiten und baut die Hierarchie PB → PG → Produkt (IKVS)."""
    if dokument.seitenanzahl != jahrgang.anzahlen.pdf_seiten:
        raise IkvsSeitenFehler(
            f"PDF hat {dokument.seitenanzahl} Seiten, Jahrgangsdatei erwartet "
            f"{jahrgang.anzahlen.pdf_seiten}"
        )
    klassifizierer = _Klassifizierer(jahrgang)
    roh: list[tuple[int, str, str | None, str | None]] = []
    letzter_typ: str | None = None
    for pdf_seite in range(1, dokument.seitenanzahl + 1):
        kapitel = _kapitel_fuer_seite(pdf_seite, dict(jahrgang.seitenbereiche))
        if kapitel != "teilplaene":
            roh.append((pdf_seite, kapitel or "sonstige", None, None))
            continue
        typ, letzter_typ = klassifizierer.klassifiziere(
            _inhaltszeilen(dokument, pdf_seite), pdf_seite, letzter_typ
        )
        roh.append((pdf_seite, typ, klassifizierer.pb, klassifizierer.produkt))

    pb_knoten = klassifizierer.pb_knoten
    p_knoten = klassifizierer.p_knoten
    if len(pb_knoten) != jahrgang.anzahlen.produktbereiche:
        raise IkvsSeitenFehler(
            f"{len(pb_knoten)} Produktbereiche gefunden, erwartet "
            f"{jahrgang.anzahlen.produktbereiche}"
        )
    if len(p_knoten) != jahrgang.anzahlen.produkte:
        raise IkvsSeitenFehler(
            f"{len(p_knoten)} Produkte gefunden, erwartet {jahrgang.anzahlen.produkte}"
        )
    ohne_info = sorted(set(p_knoten) - set(klassifizierer.pg_von_produkt))
    if ohne_info:
        raise IkvsSeitenFehler(f"Produkte ohne Produktinformationen: {', '.join(ohne_info)}")
    ohne_planseite = sorted(c for c, k in pb_knoten.items() if k.pdf_seite_start == 0)
    if ohne_planseite:
        raise IkvsSeitenFehler(f"Produktbereiche ohne Planseite: {', '.join(ohne_planseite)}")

    seiten = tuple(
        IkvsSeite(
            pdf_seite=pdf_seite,
            typ=typ,
            pb=pb,
            pg=klassifizierer.pg_von_produkt.get(produkt) if produkt else None,
            produkt=produkt,
        )
        for pdf_seite, typ, pb, produkt in roh
    )

    zeilen: list[dict[str, object]] = []
    for ebene, knoten, synthetisch in (
        ("PB", pb_knoten, False),
        ("PG", klassifizierer.pg_knoten, True),
        ("P", p_knoten, False),
    ):
        for code, eintrag in knoten.items():
            zeilen.append(
                {
                    "ebene": ebene,
                    "code": code,
                    "name": eintrag.name,
                    "eltern_code": eintrag.eltern_code,
                    "pdf_seite_start": eintrag.pdf_seite_start,
                    "synthetisch": synthetisch,
                }
            )
    return seiten, pl.DataFrame(zeilen, schema=HIERARCHIE_SPALTEN)
