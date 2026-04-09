
import sqlite3
import pandas as pd
import re
import os
import sys
from pathlib import Path
from datetime import datetime


from ui_toolkit import *
from ui_styles import UI

import json



# ──────────────────────────────────────────────
# PFADE  (relativ zum Skript-Verzeichnis)
# ──────────────────────────────────────────────

SKRIPT_DIR = Path(__file__).parent                          
PROJEKT_DIR = SKRIPT_DIR.parent                             

CSV_PFAD = SKRIPT_DIR
DB_PFAD  = PROJEKT_DIR / "db" / "finac.db"


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
        return

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
    ui = UI()
    ui.draw_import_bericht(CSV_PFAD, DB_PFAD, gesamt, neu, start)




def main_import():
    ui = UI()
    start = datetime.now()
    ui.draw_import_start(CSV_PFAD, DB_PFAD)

    DB_PFAD.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = csv_laden(CSV_PFAD)
    except FileNotFoundError as e:
        print(f"\nFEHLER: {e}")
        return

    try:
        df = daten_bereinigen(df)
    except KeyError as e:
        print(f"\nFEHLER (Spalten): {e}")
        return

    try:
        with sqlite3.connect(DB_PFAD) as conn:
            tabelle_erstellen(conn.cursor())

            # ID vor Import merken
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(buchungs_id) FROM transaktionen")
            id_vor = cursor.fetchone()[0] or 0

            gesamt, neu = zeilen_importieren(df, conn)


            cursor.execute("SELECT MAX(buchungs_id) FROM transaktionen")
            id_nach = cursor.fetchone()[0] or 0

     
            if neu > 0:
                log_import_eintragen(id_vor + 1, id_nach, neu, CSV_PFAD)

            bericht_ausgeben(gesamt, neu, start)

    except sqlite3.OperationalError as e:
        print(f"\nFEHLER (Datenbank): {e}")
        return




###########################################################
###################User Interaktion########################
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





CSV_PFAD = SKRIPT_DIR  

def user_interaktion():
    global CSV_PFAD  
    
    SKRIPT_DIR  = Path(__file__).parent
    PROJEKT_DIR = SKRIPT_DIR.parent

    gewaehlter_pfad = waehle_csv_interaktiv(PROJEKT_DIR)

    ui = UI()
    if gewaehlter_pfad:
        CSV_PFAD = gewaehlter_pfad  
        ui.draw_header(f"[green]Ausgewählt:[/green] {CSV_PFAD}")
        return CSV_PFAD
    else:
        ui.draw_header("[red]Keine Datei ausgewählt.[/red]")
        return None


def clear_database():
  
    ui = UI()
    try:
        if not DB_PFAD.exists():
            ui.draw_header("[yellow]Datenbank existiert nicht.[/yellow]")
            return False

        with sqlite3.connect(DB_PFAD) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transaktionen")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='transaktionen'")
            conn.commit()
            ui.draw_header(f"[green]Datenbank geleert – alle Transaktionen gelöscht.[/green]")
            return True

    except sqlite3.OperationalError as e:
        ui.draw_header(f"[red]FEHLER (Datenbank):[/red] {e}")
        return False
    except Exception as e:
        ui.draw_header(f"[red]FEHLER:[/red] {e}")
        return False
        return False




LOG_PFAD = PROJEKT_DIR / "db" / "import_log.json"


# ──────────────────────────────────────────────
# LOG FUNKTIONEN
# ──────────────────────────────────────────────

def _log_laden() -> list:
    """Lädt die Import-Logdatei. Gibt leere Liste zurück falls nicht vorhanden."""
    if not LOG_PFAD.exists():
        return []
    try:
        with open(LOG_PFAD, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _log_speichern(log: list) -> None:
    LOG_PFAD.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PFAD, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


MAX_LOG_EINTRAEGE = 10 

def log_import_eintragen(id_von: int, id_bis: int, anzahl: int, csv_pfad: Path) -> None:

    log = _log_laden()
    log.append({
        "zeitstempel":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "csv":          str(csv_pfad),
        "anzahl_neu":   anzahl,
        "id_von":       id_von,
        "id_bis":       id_bis,
        "rueckgaengig": False
    })


    if len(log) > MAX_LOG_EINTRAEGE:
        log = log[-MAX_LOG_EINTRAEGE:]

    _log_speichern(log)



# ──────────────────────────────────────────────
# UNDO LETZTER IMPORT – Logik
# ──────────────────────────────────────────────

def _undo_last_import_logik(conn: sqlite3.Connection) -> tuple[bool, str]:

    log = _log_laden()

    if not log:
        return False, "Kein Import-Log gefunden – noch nie importiert."

  
    letzter_idx = None
    for i in range(len(log) - 1, -1, -1):
        if not log[i]["rueckgaengig"]:
            letzter_idx = i
            break

    if letzter_idx is None:
        return False, "Letzter Import wurde bereits erfolgreich rückgängig gemacht."

    eintrag = log[letzter_idx]
    id_von  = eintrag["id_von"]
    id_bis  = eintrag["id_bis"]

    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM transaktionen
        WHERE buchungs_id BETWEEN ? AND ?
    """, (id_von, id_bis))
    conn.commit()

    geloescht = cursor.rowcount

  
    log[letzter_idx]["rueckgaengig"] = True
    _log_speichern(log)

    return True, (
        f"[green]Letzter Import rückgängig gemacht.[/green]\n"
        f"CSV      : {eintrag['csv']}\n"
        f"Datum    : {eintrag['zeitstempel']}\n"
        f"IDs      : {id_von} – {id_bis}\n"
        f"Gelöscht : {geloescht} Zeilen"
    )



# ──────────────────────────────────────────────
# Starter
# ──────────────────────────────────────────────

def undo_last_import():
    ui = UI()
    try:
        if not DB_PFAD.exists():
            ui.draw_header("[yellow]Datenbank nicht gefunden.[/yellow]")
            return

        with sqlite3.connect(DB_PFAD) as conn:
            erfolg, nachricht = _undo_last_import_logik(conn)
            if erfolg:
                ui.draw_header(nachricht)
            else:
                ui.draw_header(f"[yellow]{nachricht}[/yellow]")

    except sqlite3.OperationalError as e:
        ui.draw_header(f"[red]FEHLER (Datenbank):[/red] {e}")
    except OSError as e:
        ui.draw_header(f"[red]FEHLER (Log-Datei):[/red] {e}")
    except Exception as e:
        ui.draw_header(f"[red]Unbekannter FEHLER:[/red] {e}")


# ──────────────────────────────────────────────
# CSV AUS DB LÖSCHEN – Logik
# ──────────────────────────────────────────────

def _delete_csv_logik(conn: sqlite3.Connection, csv_pfad: Path) -> tuple[bool, str]:

    df = csv_laden(csv_pfad)
    df = daten_bereinigen(df)

    cursor = conn.cursor()
    geloescht = 0

    for _, z in df.iterrows():
        cursor.execute("""
            DELETE FROM transaktionen
            WHERE buchungstag    = ?
              AND verwendungszweck = ?
              AND betrag         = ?
        """, (
            str(z[SPALTE_BUCHUNGSTAG]).strip(),
            opt(z, SPALTE_VERWENDUNGSZWECK),
            z["_betrag_float"],
        ))
        geloescht += cursor.rowcount

    conn.commit()
    return True, (
        f"[green]CSV-Einträge aus Datenbank entfernt.[/green]\n"
        f"CSV      : {csv_pfad}\n"
        f"Gelöscht : {geloescht} Zeilen"
    )




# ──────────────────────────────────────────────
# Starter
# ──────────────────────────────────────────────
def delete_csv_from_db():

    ui = UI()
    try:
        pfad = Path(CSV_PFAD)

        if not pfad.is_file():
            ui.draw_header(f"[yellow]Keine CSV ausgewählt oder Datei nicht gefunden:[/yellow] {pfad}")
            return

        if not DB_PFAD.exists():
            ui.draw_header("[yellow]Datenbank nicht gefunden.[/yellow]")
            return

        with sqlite3.connect(DB_PFAD) as conn:
            erfolg, nachricht = _delete_csv_logik(conn, pfad)
            ui.draw_header(nachricht)

    except FileNotFoundError as e:
        ui.draw_header(f"[red]FEHLER (CSV nicht gefunden):[/red] {e}")
    except KeyError as e:
        ui.draw_header(f"[red]FEHLER (Spalten fehlen):[/red] {e}")
    except sqlite3.OperationalError as e:
        ui.draw_header(f"[red]FEHLER (Datenbank):[/red] {e}")
    except Exception as e:
        ui.draw_header(f"[red]Unbekannter FEHLER:[/red] {e}")