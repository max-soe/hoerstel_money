"""Investitionsübersichten im IKVS-Layout (z. B. Stadt Hörstel, "Investitionsübersicht B").

Je Produkt mit Investitionen druckt der Teilplanbereich nach dem Teilfinanzplan eine
Tabelle mit den Spalten Ergebnis 2024, Ansatz 2025, Ansatz 2026, VE (ohne Jahr) und Plan
2027-2029. Sie beginnt mit einer Summenzeile des Produkts ("0111102 - Name", Saldo), dann
folgt je Maßnahme eine Saldozeile ("111.02-004 - Name") mit den Zeilen "Einzahlung" und/oder
"Auszahlung". Namen sind in einer schmalen Spalte umbrochen, die Beträge stehen in einer
der Namenszeilen; eine Maßnahme kann auf der Folgeseite weiterlaufen.

Anders als ProFIS+ nennt das IKVS-Layout keine Sachkonten: `konto`, `konto_name` und `art`
bleiben leer. Geprüft wird je Maßnahme Saldo = Einzahlung - Auszahlung und je Produkt die
Summenzeile = Σ Maßnahmen-Saldi (Toleranz 1 € je Wert für die Cent-Rundung der
Ist-Ergebnisse). Ausgegeben werden nur gedruckte Werte; "--" (kein Wert) entfällt.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field

import polars as pl

from ostbevern.ikvs import (
    Spalten,
    ist_wert_wort,
    lies_ikvs_betrag,
    lies_tabellenkopf,
    pruefe_spaltenabbildung,
    verbinde_teile,
)
from ostbevern.konfiguration import Jahrgang, layout_liste, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import INVESTITIONEN_SPALTEN, VE_FAELLIGKEITEN_SPALTEN, zerlege_spaltenkopf

_RICHTUNGEN = {"Einzahlung": "einzahlung", "Auszahlung": "auszahlung"}
_LEERWERT = "--"
_MINUS = "-"
# Toleranz der Saldo-Gegenproben: die Ist-Ergebnisse sind mit Cent gedruckt und werden je
# Wert kaufmännisch gerundet, Summen gerundeter Werte weichen deshalb um wenige Euro ab.
_RUNDUNGSTOLERANZ_JE_WERT = 1


class IkvsInvestitionenFehler(ValueError):
    """Wird ausgelöst, wenn eine Investitionsübersicht nicht eindeutig lesbar ist (D-08)."""


@dataclass
class _Werte:
    """Sieben Spaltenwerte einer Zeile; None = "--" (nicht gedruckt)."""

    anzahl: int
    werte: list[int | None] = field(default_factory=list)
    gesetzt: list[bool] = field(default_factory=list)
    minus: list[bool] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.werte = [None] * self.anzahl
        self.gesetzt = [False] * self.anzahl
        self.minus = [False] * self.anzahl

    def nimm(self, spalte: int, text: str, ort: str) -> None:
        if text == _MINUS:
            if self.minus[spalte] or self.gesetzt[spalte]:
                raise IkvsInvestitionenFehler(f"{ort}: Minuszeichen ohne Betrag")
            self.minus[spalte] = True
            return
        if self.gesetzt[spalte]:
            raise IkvsInvestitionenFehler(f"{ort}: zwei Beträge in Spalte {spalte + 1}")
        self.gesetzt[spalte] = True
        if text == _LEERWERT:
            return
        betrag = lies_ikvs_betrag(text)
        self.werte[spalte] = -betrag if self.minus[spalte] else betrag

    @property
    def leer(self) -> bool:
        return not any(self.gesetzt)

    @property
    def vollstaendig(self) -> bool:
        return all(self.gesetzt)

    def als_zahlen(self) -> list[int]:
        return [w or 0 for w in self.werte]


@dataclass
class _Eintrag:
    kennung: str
    ist_produkt: bool
    name_teile: list[str]
    pdf_seite: int
    saldo: _Werte
    richtungen: dict[str, tuple[_Werte, int]] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return verbinde_teile(self.name_teile) if self.name_teile else ""


@dataclass(frozen=True)
class IkvsMassnahme:
    produkt: str
    massnahme_id: str
    massnahme_name: str
    pdf_seite: int
    saldo: tuple[int, ...]
    richtungen: dict[str, tuple[tuple[int | None, ...], int]]


def lies_ikvs_investitionen(dokument: PdfDokument, jahrgang: Jahrgang) -> list[IkvsMassnahme]:
    """Liest alle Investitionsübersichten des Teilplanbereichs (IKVS)."""
    bereich = jahrgang.seitenbereiche["teilplaene"]
    gedruckte_spalten = layout_liste(jahrgang, "ikvs_investitionen", "spalten")
    pruefe_spaltenabbildung(gedruckte_spalten, jahrgang.spalten["investitionen"])
    titel_muster = re.compile(layout_text(jahrgang, "ikvs_teilplaene", "investitionen_muster"))
    ende_muster = [
        re.compile(layout_text(jahrgang, "ikvs_teilplaene", schluessel))
        for schluessel in (
            "abschnitt_ende_muster",
            "teilergebnisplan_muster",
            "teilfinanzplan_muster",
        )
    ]
    massnahme_muster = re.compile(layout_text(jahrgang, "ikvs_investitionen", "massnahme_muster"))
    anzahl = len(gedruckte_spalten)

    massnahmen: list[IkvsMassnahme] = []
    produkt: str | None = None
    eintraege: list[_Eintrag] = []
    offen: _Eintrag | None = None

    def schliesse_uebersicht() -> None:
        nonlocal produkt, eintraege, offen
        if produkt is not None:
            massnahmen.extend(_pruefe_uebersicht(produkt, eintraege, anzahl))
        produkt, eintraege, offen = None, [], None

    for pdf_seite in range(bereich.von, bereich.bis + 1):
        zeilen = [z for z in dokument.zeilen(pdf_seite)[1:] if z.text != str(pdf_seite)]
        spalten: Spalten | None = None
        index = 0
        while index < len(zeilen):
            zeile = zeilen[index]
            titel = titel_muster.match(zeile.text)
            if titel is not None or any(m.match(zeile.text) for m in ende_muster):
                schliesse_uebersicht()
                if titel is not None:
                    produkt = titel.group(1)
                spalten = None
                index += 1
                continue
            if produkt is None:
                index += 1
                continue
            kopf = lies_tabellenkopf(zeilen, index, gedruckte_spalten, pdf_seite)
            if kopf is not None:
                spalten, schritte = kopf
                index += schritte
                continue
            if spalten is None:
                raise IkvsInvestitionenFehler(
                    f"S. {pdf_seite}: Zeile vor dem Tabellenkopf der Investitionsübersicht "
                    f"{produkt}: {zeile.text!r}"
                )
            offen = _lies_zeile(
                zeile, spalten, pdf_seite, offen, eintraege, massnahme_muster, produkt, anzahl
            )
            index += 1
    schliesse_uebersicht()
    return massnahmen


def _lies_zeile(
    zeile: Textzeile,
    spalten: Spalten,
    pdf_seite: int,
    offen: _Eintrag | None,
    eintraege: list[_Eintrag],
    massnahme_muster: re.Pattern[str],
    produkt: str,
    anzahl: int,
) -> _Eintrag | None:
    ort = f"S. {pdf_seite}, Investitionsübersicht {produkt}"
    beschriftung: list[str] = []
    werte: list[tuple[int, str]] = []
    for wort in zeile.woerter:
        spalte = spalten.index(wort)
        if spalte is None:
            beschriftung.append(wort.text)
        elif ist_wert_wort(wort.text):
            werte.append((spalte, wort.text))
        else:
            raise IkvsInvestitionenFehler(f"{ort}: Text {wort.text!r} in der Betragszone")

    ziel: _Werte
    if (
        len(beschriftung) >= 2
        and beschriftung[1] == "-"
        and (beschriftung[0] == produkt or massnahme_muster.match(beschriftung[0]))
    ):
        offen = _Eintrag(
            kennung=beschriftung[0],
            ist_produkt=beschriftung[0] == produkt,
            name_teile=[" ".join(beschriftung[2:])] if beschriftung[2:] else [],
            pdf_seite=pdf_seite,
            saldo=_Werte(anzahl),
        )
        eintraege.append(offen)
        ziel = offen.saldo
    elif beschriftung and " ".join(beschriftung) in _RICHTUNGEN:
        if offen is None or offen.ist_produkt:
            raise IkvsInvestitionenFehler(f"{ort}: {zeile.text!r} ohne Maßnahme")
        richtung = _RICHTUNGEN[" ".join(beschriftung)]
        if richtung in offen.richtungen:
            raise IkvsInvestitionenFehler(f"{ort}: {offen.kennung} {richtung} doppelt")
        ziel = _Werte(anzahl)
        offen.richtungen[richtung] = (ziel, pdf_seite)
    else:
        if offen is None or offen.richtungen:
            raise IkvsInvestitionenFehler(f"{ort}: unerwartete Zeile {zeile.text!r}")
        if beschriftung:
            offen.name_teile.append(" ".join(beschriftung))
        ziel = offen.saldo
    for spalte, text in werte:
        ziel.nimm(spalte, text, f"{ort}, {offen.kennung if offen else ''}")
    return offen


def _pruefe_uebersicht(
    produkt: str, eintraege: Sequence[_Eintrag], anzahl: int
) -> list[IkvsMassnahme]:
    if not eintraege or not eintraege[0].ist_produkt:
        raise IkvsInvestitionenFehler(f"Investitionsübersicht {produkt}: Summenzeile fehlt")
    summe, *massnahmen = eintraege
    if any(e.ist_produkt for e in massnahmen) or not massnahmen:
        raise IkvsInvestitionenFehler(
            f"Investitionsübersicht {produkt}: keine oder doppelte Summenzeile"
        )
    for eintrag in eintraege:
        if not eintrag.saldo.vollstaendig:
            raise IkvsInvestitionenFehler(
                f"S. {eintrag.pdf_seite}: {eintrag.kennung} Saldo unvollständig"
            )
        for richtung, (werte, seite) in eintrag.richtungen.items():
            if not werte.vollstaendig:
                raise IkvsInvestitionenFehler(
                    f"S. {seite}: {eintrag.kennung} {richtung} unvollständig"
                )

    ergebnis: list[IkvsMassnahme] = []
    saldo_summe = [0] * anzahl
    for eintrag in massnahmen:
        if not eintrag.richtungen:
            raise IkvsInvestitionenFehler(
                f"S. {eintrag.pdf_seite}: Maßnahme {eintrag.kennung} ohne Ein- oder Auszahlung"
            )
        ein = eintrag.richtungen.get("einzahlung", (_Werte(anzahl), 0))[0].als_zahlen()
        aus = eintrag.richtungen.get("auszahlung", (_Werte(anzahl), 0))[0].als_zahlen()
        saldo = eintrag.saldo.als_zahlen()
        for spalte in range(anzahl):
            if abs(saldo[spalte] - (ein[spalte] - aus[spalte])) > _RUNDUNGSTOLERANZ_JE_WERT:
                raise IkvsInvestitionenFehler(
                    f"S. {eintrag.pdf_seite}: Maßnahme {eintrag.kennung} Spalte {spalte + 1}: "
                    f"Saldo {saldo[spalte]} ≠ Einzahlung {ein[spalte]} - Auszahlung "
                    f"{aus[spalte]}"
                )
            saldo_summe[spalte] += saldo[spalte]
        ergebnis.append(
            IkvsMassnahme(
                produkt=produkt,
                massnahme_id=eintrag.kennung,
                massnahme_name=eintrag.name,
                pdf_seite=eintrag.pdf_seite,
                saldo=tuple(saldo),
                richtungen={
                    richtung: (tuple(werte.werte), seite)
                    for richtung, (werte, seite) in eintrag.richtungen.items()
                },
            )
        )
    gedruckt = summe.saldo.als_zahlen()
    toleranz = _RUNDUNGSTOLERANZ_JE_WERT * len(massnahmen)
    for spalte in range(anzahl):
        if abs(gedruckt[spalte] - saldo_summe[spalte]) > toleranz:
            raise IkvsInvestitionenFehler(
                f"S. {summe.pdf_seite}: Summenzeile {produkt} Spalte {spalte + 1}: "
                f"{gedruckt[spalte]} ≠ Σ Maßnahmen {saldo_summe[spalte]}"
            )
    return ergebnis


def investitionen_datensaetze(
    massnahmen: Sequence[IkvsMassnahme], jahrgang: Jahrgang
) -> pl.DataFrame:
    """investitionen.csv im Langformat: je Maßnahme, Richtung und gedrucktem Wert."""
    spalten = [zerlege_spaltenkopf(k) for k in jahrgang.spalten["investitionen"]]
    datensaetze: list[dict[str, object]] = []
    gesehen: set[tuple[str, str]] = set()
    for massnahme in massnahmen:
        schluessel = (massnahme.produkt, massnahme.massnahme_id)
        if schluessel in gesehen:
            raise IkvsInvestitionenFehler(
                f"Maßnahme {massnahme.massnahme_id} kommt in Produkt {massnahme.produkt} "
                "doppelt vor"
            )
        gesehen.add(schluessel)
        for richtung, (werte, pdf_seite) in sorted(massnahme.richtungen.items()):
            for (wertart, jahr), betrag in zip(spalten, werte, strict=True):
                if betrag is None:
                    continue
                datensaetze.append(
                    {
                        "produkt": massnahme.produkt,
                        "massnahme_id": massnahme.massnahme_id,
                        "massnahme_name": massnahme.massnahme_name,
                        "konto": None,
                        "konto_name": None,
                        "richtung": richtung,
                        "art": None,
                        "jahr": jahr,
                        "wertart": wertart,
                        "betrag": betrag,
                        "pdf_seite": pdf_seite,
                    }
                )
    return pl.DataFrame(datensaetze, schema=INVESTITIONEN_SPALTEN)


class IkvsVeFehler(ValueError):
    """Die VE-Übersicht passt nicht zu den Investitionsübersichten."""


def ve_faelligkeiten_aus_uebersicht(
    ve_uebersicht: pl.DataFrame, investitionen: pl.DataFrame
) -> pl.DataFrame:
    """VE-Fälligkeiten (VE_FAELLIGKEITEN_SPALTEN) aus der abgeschriebenen VE-Übersicht.

    Das IKVS-Layout druckt die Fälligkeiten nur in der Übersicht (Hörstel S. 586), nicht je
    Maßnahme. Jede Zeile der Übersicht nennt ihr Produkt; die Maßnahme ist die Maßnahme
    dieses Produkts, deren VE in der Investitionsübersicht genau der Summe der Fälligkeiten
    entspricht. Gibt es keine solche Maßnahme (Hörstel: Neubau eines Verwaltungsgebäudes,
    5.100 T€, nur in der VE-Übersicht und der Satzung), bleibt `massnahme_id` leer; zwei
    passende Maßnahmen brechen ab. Beträge in Euro (Übersicht in T€ × 1000), `konto` leer.
    """
    einzel = ve_uebersicht.filter(~pl.col("ist_gesamt"))
    for zeile in ve_uebersicht.filter(
        pl.col("ist_gesamt") & pl.col("faellig_jahr").is_not_null()
    ).iter_rows(named=True):
        summe = einzel.filter(pl.col("faellig_jahr") == zeile["faellig_jahr"])["betrag_teur"].sum()
        if summe != zeile["betrag_teur"]:
            raise IkvsVeFehler(
                f"VE-Übersicht fällig {zeile['faellig_jahr']}: Einzelzeilen {summe} T€, "
                f"Summenzeile {zeile['betrag_teur']} T€"
            )
    ve_je_massnahme = investitionen.filter(pl.col("wertart") == "ve")
    zeilen: list[dict[str, object]] = []
    for position in sorted(einzel["position"].unique().to_list()):
        teil = einzel.filter(pl.col("position") == position)
        produkt = teil["produkt"][0]
        gesamt_euro = int(teil["betrag_teur"].sum()) * 1000
        kandidaten = (
            ve_je_massnahme.filter(
                (pl.col("produkt") == produkt) & (pl.col("betrag") == gesamt_euro)
            )["massnahme_id"]
            .unique()
            .to_list()
        )
        if len(kandidaten) > 1:
            raise IkvsVeFehler(
                f"VE-Übersicht Position {position} ({produkt}, {gesamt_euro} €): mehrere "
                f"Maßnahmen mit gleicher VE {sorted(kandidaten)}"
            )
        massnahme_id = kandidaten[0] if kandidaten else None
        for z in teil.iter_rows(named=True):
            zeilen.append(
                {
                    "produkt": produkt,
                    "massnahme_id": massnahme_id,
                    "konto": None,
                    "jahr": z["faellig_jahr"],
                    "betrag": z["betrag_teur"] * 1000,
                    "pdf_seite": z["quelle"],
                }
            )
    return pl.DataFrame(zeilen, schema=VE_FAELLIGKEITEN_SPALTEN)
