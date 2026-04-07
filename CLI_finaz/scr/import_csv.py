
import sqlite3
import pandas as pd
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

from ui_toolkit import *
from ui_styles import UI


# ──────────────────────────────────────────────
# PFADE  (relativ zum Skript-Verzeichnis)
# ──────────────────────────────────────────────

SKRIPT_DIR = Path(__file__).parent                          
PROJEKT_DIR = SKRIPT_DIR.parent                             

CSV_PFAD = SKRIPT_DIR
DB_PFAD  = PROJEKT_DIR / "db" / "transaktion.db"


# ──────────────────────────────────────────────
# SPALTENNAMEN DER CSV
# ──────────────────────────────────────────────

SPALTE_KONTOBEZEICHNUNG  = "Bezeichnung Auftragskonto"
SPALTE_IBAN_KONTO        = "IBAN Auftragskonto"
SPALTE_BIC_KONTO         = "BIC Auftragskonto"
SPALTE_BANKNAME          = "Bankname Auftragskonto"
SPALTE_BUCHUNGSTAG       = "Buchungstag"
SPALTE_VALUTADATUM       = "Valutadatum"
SPALTE_NAME_PARTNER      = "Namefrom ui_toolkit import * Zahlungsbeteiligter"
SPALTE_IBAN_PARTNER      = "IBAN Zahlungsbeteiligter"
SPALTE_BIC_PARTNER       = "BIC (SWIFT-Code) Zahlungsbeteiligter"
SPALTE_BUCHUNGSTEXT      = "Buchungstext"
SPALTE_VERWENDUNGSZWECK  = "Verwendungszweck"
SPALTE_BETRAG            = "Betrag"
SPALTE_WAEHRUNG          = "Waehrung"
SPALTE_SALDO             = "Saldo nach Buchung"
SPALTE_BEMERKUNG         = "Bemerkung"
SPALTE_GEKENNZEICHNET    = "Gekennzeichneter Umsatz"
SPALTE_GLAEUBIGER_ID     = "Glaeubiger ID"
SPALTE_MANDATSREFERENZ   = "Mandatsreferenz"

# Pflicht-Spalten die für den Import zwingend vorhanden sein müssen
PFLICHT_SPALTEN = [
    SPALTE_BUCHUNGSTAG,
    SPALTE_BETRAG,
    SPALTE_SALDO,
    SPALTE_WAEHRUNG,
]


# ──────────────────────────────────────────────
# HILFSFUNKTIONEN
# ──────────────────────────────────────────────

def deutschen_betrag_konvertieren(wert) -> float:
    if pd.isna(wert) or str(wert).strip() == "":
        return 0.0
    bereinigt = re.sub(r"\.", "", str(wert).strip())
    bereinigt = bereinigt.replace(",", ".")
    try:
        return float(bereinigt)
    except ValueError:
        return 0.0

#Liest eine optionale Spalte aus
def opt(zeile, spalte: str) -> str:
    if spalte not in zeile.index:
        return ""
    val = zeile[spalte]
    return "" if pd.isna(val) or str(val).strip() in ("nan", "") else str(val).strip()

#maybe auslagern
def tabelle_erstellen(cursor: sqlite3.Cursor) -> None:
    """
    Erstellt die Tabelle 'transaktionen' falls sie noch nicht existiert.
    UNIQUE-Fingerabdruck: buchungstag + verwendungszweck + betrag
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaktionen (
            buchungs_id          INTEGER  PRIMARY KEY AUTOINCREMENT,

            -- Auftragskonto
            kontobezeichnung     TEXT,
            iban_konto           TEXT,
            bic_konto            TEXT,
            bankname             TEXT,

            -- Buchungsdaten
            buchungstag          TEXT     NOT NULL,
            valutadatum          TEXT,

            -- Zahlungsbeteiligter
            name_partner         TEXT,
            iban_partner         TEXT,
            bic_partner          TEXT,

            -- Transaktion
            buchungstext         TEXT,
            verwendungszweck     TEXT,
            betrag               REAL     NOT NULL,
            waehrung             TEXT,
            saldo_nach_buchung   REAL,

            -- Zusatzfelder
            bemerkung            TEXT,
            gekennzeichnet       TEXT,
            glaeubiger_id        TEXT,
            mandatsreferenz      TEXT,

            UNIQUE (buchungstag, verwendungszweck, betrag)
        )
    """)


def csv_laden(pfad: Path) -> pd.DataFrame:

    if not pfad.is_file():
        raise FileNotFoundError(f"CSV nicht gefunden: '{pfad}'")

    for encoding in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(
                pfad,
                sep=";",
                encoding=encoding,
                dtype=str,
                skipinitialspace=True,
            )
            df.columns = df.columns.str.strip()
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Encoding der Datei '{pfad}' konnte nicht erkannt werden.")


def daten_bereinigen(df: pd.DataFrame) -> pd.DataFrame:
    """Trimmen → Zahlen konvertieren → NaN füllen → chronologisch sortieren."""

    fehlende = [s for s in PFLICHT_SPALTEN if s not in df.columns]
    if fehlende:
        raise KeyError(
            f"Pflicht-Spalten fehlen in der CSV: {fehlende}\n"
            f"Vorhandene Spalten: {list(df.columns)}"
        )

    # Alle Text-Spalten trimmen
    df = df.apply(lambda col: col.str.strip() if col.dtype == object else col)

    # Zahlen konvertieren
    df["_betrag_float"] = df[SPALTE_BETRAG].apply(deutschen_betrag_konvertieren)
    df["_saldo_float"]  = df[SPALTE_SALDO].apply(deutschen_betrag_konvertieren)

    # Datum parsen → chronologisch sortieren (älteste Buchung zuerst → niedrigste ID)
    df["_datum_parsed"] = pd.to_datetime(
        df[SPALTE_BUCHUNGSTAG], dayfirst=True, errors="coerce"
    )
    df = df.sort_values("_datum_parsed", ascending=True).reset_index(drop=True)

    # Heutige Buchungen ignorieren – könnten noch unvollständig sein
    heute = pd.Timestamp.today().normalize()
    heute_buchungen = (df["_datum_parsed"] == heute).sum()
    if heute_buchungen > 0:
        print(f"  Übersprungen: {heute_buchungen} Buchung(en) vom heutigen Tag ({heute.strftime('%d.%m.%Y')}) ignoriert.")
        df = df[df["_datum_parsed"] < heute].reset_index(drop=True)

    return df


def zeilen_importieren(df: pd.DataFrame, conn: sqlite3.Connection) -> tuple:
    """INSERT OR IGNORE – Datenbank entscheidet per Fingerabdruck über Duplikate."""
    cursor = conn.cursor()
    neu    = 0

    for _, z in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO transaktionen (
                kontobezeichnung, iban_konto, bic_konto, bankname,
                buchungstag, valutadatum,
                name_partner, iban_partner, bic_partner,
                buchungstext, verwendungszweck,
                betrag, waehrung, saldo_nach_buchung,
                bemerkung, gekennzeichnet, glaeubiger_id, mandatsreferenz
            ) VALUES (
                ?,?,?,?,
                ?,?,
                ?,?,?,
                ?,?,
                ?,?,?,
                ?,?,?,?
            )
        """, (
            opt(z, SPALTE_KONTOBEZEICHNUNG),
            opt(z, SPALTE_IBAN_KONTO),
            opt(z, SPALTE_BIC_KONTO),
            opt(z, SPALTE_BANKNAME),

            opt(z, SPALTE_BUCHUNGSTAG),
            opt(z, SPALTE_VALUTADATUM),

            opt(z, SPALTE_NAME_PARTNER),
            opt(z, SPALTE_IBAN_PARTNER),
            opt(z, SPALTE_BIC_PARTNER),

            opt(z, SPALTE_BUCHUNGSTEXT),
            opt(z, SPALTE_VERWENDUNGSZWECK),

            z["_betrag_float"],
            opt(z, SPALTE_WAEHRUNG),
            z["_saldo_float"],

            opt(z, SPALTE_BEMERKUNG),
            opt(z, SPALTE_GEKENNZEICHNET),
            opt(z, SPALTE_GLAEUBIGER_ID),
            opt(z, SPALTE_MANDATSREFERENZ),
        ))
        if cursor.rowcount == 1:
            neu += 1

    conn.commit()
    return len(df), neu


def bericht_ausgeben(gesamt: int, neu: int, start: datetime) -> None:
    """Konsolenausgabe nach dem Import."""
    duplikate  = gesamt - neu
    db_groesse = os.path.getsize(DB_PFAD) / 1024

    print(f"\n{'=' * 54}")
    print(f"  Finance-to-SQLite Import abgeschlossen")
    print(f"{'=' * 54}")
    print(f"  CSV       : {CSV_PFAD}")
    print(f"  Datenbank : {DB_PFAD}  ({db_groesse:.1f} KB)")
    print(f"  {'-' * 50}")
    print(f"  CSV-Zeilen gesamt   : {gesamt:>6}")
    print(f"  Neu importiert      : {neu:>6}")
    print(f"  Duplikate ignoriert : {duplikate:>6}")
    print(f"  {'-' * 50}")
    print(f"{'=' * 54}\n")




def main():
    start = datetime.now()
    print(f"\nStarte Import ...")
    print(f"  Quelle    : {CSV_PFAD}")
    print(f"  Ziel      : {DB_PFAD}")

    # DB-Ordner anlegen falls nicht vorhanden
    DB_PFAD.parent.mkdir(parents=True, exist_ok=True)

    # CSV laden
    try:
        df = csv_laden(CSV_PFAD)
        print(f"  {len(df)} Zeilen gelesen.")
    except FileNotFoundError as e:
        print(f"\nFEHLER: {e}")
        sys.exit(1)

    # Bereinigen & sortieren
    try:
        df = daten_bereinigen(df)
        print(f"  Bereinigt und chronologisch sortiert.")
    except KeyError as e:
        print(f"\nFEHLER (Spalten): {e}")
        sys.exit(1)

    # In DB schreiben
    try:
        with sqlite3.connect(DB_PFAD) as conn:
            tabelle_erstellen(conn.cursor())
            gesamt, neu = zeilen_importieren(df, conn)
            bericht_ausgeben(gesamt, neu, start)
    except sqlite3.OperationalError as e:
        print(f"\nFEHLER (Datenbank): {e}")
        sys.exit(1)



###########################################################
###########################################################
###########################################################
##########################User Interaktion#################
###########################################################
###########################################################
###########################################################

def waehle_csv_interaktiv(start_dir):

    ui = UI()
    aktueller_pfad = Path(start_dir).resolve()

    while True:
        try:
            eintraege = sorted(
                list(aktueller_pfad.iterdir()),
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
        except PermissionError:
            ui.draw_header(f"[red]Zugriff verweigert:[/red] {aktueller_pfad}")
            aktueller_pfad = aktueller_pfad.parent
            continue

        # ── Panel zeichnen ───────────────────────────────────────────────────
        ui.draw_file_browser(aktueller_pfad, eintraege)

        # ── Autovervollständigung ────────────────────────────────────────────
        verfuegbare_namen = [e.name for e in eintraege]
        if aktueller_pfad.parent != aktueller_pfad:
            verfuegbare_namen.append("..")
        verfuegbare_namen.append("exit")

        completer = WordCompleter(verfuegbare_namen, ignore_case=True)

        # ── Eingabe ──────────────────────────────────────────────────────────
        try:
            user_input = prompt(
                "importer -- wähle Datei: ",
                completer=completer,
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if user_input.lower() == "exit":
            return None

        if user_input == "":
            aktueller_pfad = aktueller_pfad.parent
            continue

        neuer_pfad = (aktueller_pfad / user_input).resolve()

        if not neuer_pfad.exists():
            ui.draw_header(f"[red]Nicht gefunden:[/red] '{user_input}'")
            continue

        if neuer_pfad.is_dir():
            aktueller_pfad = neuer_pfad

        elif neuer_pfad.is_file():
            if neuer_pfad.suffix.lower() == ".csv":
                return neuer_pfad
            else:
                ui.draw_header(f"[red]Keine CSV-Datei:[/red] {neuer_pfad.name}")






def user_interaktion():
    SKRIPT_DIR  = Path(__file__).parent
    PROJEKT_DIR = SKRIPT_DIR.parent

    CSV_PFAD = waehle_csv_interaktiv(PROJEKT_DIR)

    ui = UI()
    if CSV_PFAD:
        ui.draw_header(f"[green]Ausgewählt:[/green] {CSV_PFAD}")
        return CSV_PFAD
    else:
        ui.draw_header(f"[red]Keine Datei ausgewählt.[/red]")

        return None



def return_csv_pfad():
    return CSV_PFAD

