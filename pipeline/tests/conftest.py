"""Gemeinsame Fixtures für Pipeline-Tests (Phase 3).

Session-scoped, damit das teure PDF-Lesen/Klassifizieren nur einmal pro Testlauf
passiert, nicht einmal je Testdatei.
"""

from __future__ import annotations

import os

# Die bestehenden Tests sind Regressionstests für das ProFIS+-Layout und laufen gegen den
# Ostbevern-Referenzstand unter pipeline/referenz/ostbevern/ (Jahrgang, daten/, App-Daten;
# PDF unter raw_data/ostbevern/). Muss vor dem ersten Import von ostbevern.konfiguration
# gesetzt sein. Der aktive Hörsteler Jahrgang (IKVS) wird in den test_ikvs*.py ausdrücklich
# geladen und schreibt nur in temporäre Verzeichnisse.
os.environ.setdefault("PIPELINE_REFERENZ", "referenz/ostbevern")

import polars as pl
import pytest

from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_jahrgang
from ostbevern.pdf import PdfDokument
from ostbevern.schema import SEITEN_SPALTEN
from ostbevern.seiten import baue_hierarchie, klassifiziere_dokument


@pytest.fixture(scope="session")
def jahrgang() -> Jahrgang:
    return lade_jahrgang(STANDARD_JAHR)


@pytest.fixture(scope="session")
def pdf_klassifikation(jahrgang: Jahrgang) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Klassifiziert das PDF in-memory (D-07): Seiten und Hierarchie ohne daten/ zu lesen."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        seiten, koepfe = klassifiziere_dokument(dokument, jahrgang)
        seiten_df = pl.DataFrame(
            [
                {
                    "pdf_seite": seite.pdf_seite,
                    "typ": seite.typ,
                    "pb": seite.pb,
                    "pg": seite.pg,
                    "produkt": seite.produkt,
                }
                for seite in seiten
            ],
            schema=SEITEN_SPALTEN,
        )
        hierarchie_df = baue_hierarchie(seiten, koepfe, jahrgang)
    return seiten_df, hierarchie_df
