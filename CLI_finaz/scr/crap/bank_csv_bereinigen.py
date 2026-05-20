"""
Verwendung: python bank_csv_bereinigen.py <pfad/zur/bank.csv>

Bereinigt eine Bank-CSV, weist Kategorien zu (via db/categories.json)
und speichert das Ergebnis als <dateiname>_bereinigt.csv.
"""

import sys
import re
import csv
import json
import pandas as pd
from pathlib import Path


SKRIPT_DIR   = Path(__file__).parent
PROJEKT_DIR  = SKRIPT_DIR.parent
CATEGORY_PFAD = PROJEKT_DIR / "db" / "categories.json"

# Spaltennamen der Bank-CSV (ING/Sparkasse-Format)
SPALTE_BUCHUNGSTAG      = "Buchungstag"
SPALTE_VERWENDUNGSZWECK = "Verwendungszweck"
SPALTE_BETRAG           = "Betrag"
SPALTE_NAME_PARTNER     = "Name Zahlungsbeteiligter"
SPALTE_BUCHUNGSTEXT     = "Buchungstext"

PFLICHT_SPALTEN = [SPALTE_BUCHUNGSTAG, SPALTE_BETRAG, SPALTE_VERWENDUNGSZWECK]


def csv_laden(pfad: Path) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "latin-1", "utf-8"):
        try:
            df = pd.read_csv(pfad, sep=";", encoding=encoding, dtype=str, skipinitialspace=True)
            df.columns = df.columns.str.strip()
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Encoding der Datei '{pfad}' konnte nicht erkannt werden.")


def betrag_konvertieren(wert) -> float:
    if pd.isna(wert) or str(wert).strip() == "":
        return 0.0
    bereinigt = re.sub(r"\.", "", str(wert).strip())
    bereinigt = bereinigt.replace(",", ".")
    try:
        return float(bereinigt)
    except ValueError:
        return 0.0


def kategorien_laden() -> dict:
    if not CATEGORY_PFAD.exists():
        print(f"WARNUNG: categories.json nicht gefunden: {CATEGORY_PFAD}")
        return {}
    with open(CATEGORY_PFAD, "r", encoding="utf-8") as f:
        return json.load(f)


def kategorie_zuweisen(zeile: pd.Series, kategorien: dict) -> str:
    suchtext_teile = []
    for spalte in (SPALTE_VERWENDUNGSZWECK, SPALTE_NAME_PARTNER, SPALTE_BUCHUNGSTEXT):
        if spalte in zeile.index and pd.notna(zeile[spalte]):
            suchtext_teile.append(str(zeile[spalte]).lower())
    suchtext = " ".join(suchtext_teile)

    for kategorie, keywords in kategorien.items():
        for keyword in keywords:
            if keyword.lower() in suchtext:
                return kategorie
    return "Sonstiges"


def bereinigen(pfad: Path) -> None:
    print(f"Lade CSV: {pfad}")
    df = csv_laden(pfad)

    fehlende = [s for s in PFLICHT_SPALTEN if s not in df.columns]
    if fehlende:
        print(f"FEHLER: Pflicht-Spalten fehlen: {fehlende}")
        print(f"Vorhandene Spalten: {list(df.columns)}")
        sys.exit(1)

    df = df.apply(lambda col: col.str.strip() if col.dtype == object else col)

    df["betrag"] = df[SPALTE_BETRAG].apply(betrag_konvertieren)
    df["buchungstag"] = df[SPALTE_BUCHUNGSTAG].str.strip()
    df["verwendungszweck"] = df[SPALTE_VERWENDUNGSZWECK].fillna("").str.strip()

    df["_datum"] = pd.to_datetime(df["buchungstag"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["_datum"])
    df = df.sort_values("_datum", ascending=True).reset_index(drop=True)

    heute = pd.Timestamp.today().normalize()
    heute_count = (df["_datum"] == heute).sum()
    if heute_count > 0:
        print(f"Übersprungen: {heute_count} Buchung(en) vom heutigen Tag ignoriert.")
        df = df[df["_datum"] < heute].reset_index(drop=True)

    kategorien = kategorien_laden()
    print("Weise Kategorien zu ...")
    df["category"] = df.apply(lambda z: kategorie_zuweisen(z, kategorien), axis=1)

    weglassen_count = (df["category"] == "weglassen").sum()
    if weglassen_count > 0:
        print(f"Weglassen: {weglassen_count} Buchung(en) herausgefiltert.")
        df = df[df["category"] != "weglassen"].reset_index(drop=True)

    ergebnis = df[["betrag", "buchungstag", "verwendungszweck", "category"]].copy()

    ausgabe_pfad = pfad.parent / (pfad.stem + "_bereinigt.csv")
    ergebnis.to_csv(ausgabe_pfad, sep=";", index=False, encoding="utf-8-sig",
                    quoting=csv.QUOTE_NONNUMERIC)

    print(f"Fertig: {len(ergebnis)} Einträge gespeichert → {ausgabe_pfad}")
    kategorien_stats = ergebnis["category"].value_counts()
    print("\nKategorien-Übersicht:")
    for kat, anzahl in kategorien_stats.items():
        print(f"  {kat:<30} {anzahl}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Verwendung: python bank_csv_bereinigen.py <pfad/zur/bank.csv>")
        sys.exit(1)

    csv_pfad = Path(sys.argv[1]).resolve()
    if not csv_pfad.exists():
        print(f"FEHLER: Datei nicht gefunden: {csv_pfad}")
        sys.exit(1)
    if csv_pfad.suffix.lower() != ".csv":
        print(f"FEHLER: Keine CSV-Datei: {csv_pfad.name}")
        sys.exit(1)

    bereinigen(csv_pfad)
