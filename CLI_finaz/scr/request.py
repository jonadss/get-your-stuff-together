import sqlite3
from pathlib import Path
from tabulate import tabulate


# ──────────────────────────────────────────────
# PFAD  (relativ zu diesem Skript)
# ──────────────────────────────────────────────

SKRIPT_DIR = Path(__file__).parent          
PROJEKT_DIR = SKRIPT_DIR.parent             
DB_PFAD = PROJEKT_DIR / "db" / "finac.db"


# ──────────────────────────────────────────────
# Auswertung-FUNKTIONEN
# ──────────────────────────────────────────────

def overview(database: sqlite3.Connection) -> None:

    cursor = database.cursor()
    cursor.execute("""
        SELECT buchungs_id, buchungstag, betrag, saldo_nach_buchung, verwendungszweck, category
        FROM transaktionen
        ORDER BY
            SUBSTR(buchungstag, 7, 4) DESC,  
            SUBSTR(buchungstag, 4, 2) DESC,  
            SUBSTR(buchungstag, 1, 2) DESC,  
            buchungs_id
    """)

    return cursor.fetchall()


def bank_balance(database: sqlite3.Connection) -> float:
    cursor = database.cursor()
    cursor.execute("""
        SELECT saldo_nach_buchung
        FROM transaktionen
        ORDER BY
            SUBSTR(buchungstag, 7, 4) DESC,  
            SUBSTR(buchungstag, 4, 2) DESC,  
            SUBSTR(buchungstag, 1, 2) DESC,  
            buchungs_id DESC -- Hier war das Komma zu viel
        LIMIT 1                           
    """)
    row = cursor.fetchone()

    print(f"\n{'─' * 70}")
    if row:
        saldo = row[0]
        return saldo
    else:
        print("  Noch keine Daten in der Datenbank.")
        return 0.0


#Test funktionen 
def test(database: sqlite3.Connection):
    cursor = database.cursor()
    x = 1
  
    cursor.execute("""
        SELECT buchungs_id, verwendungszweck
        FROM transaktionen
        """)
    row = cursor.fetchall()
    print(row[0])


# ──────────────────────────────────────────────
# EINSTIEGSPUNKT
# ──────────────────────────────────────────────


    

def start_saldo_request():
    if not DB_PFAD.exists():
        print(f"\nFEHLER: Datenbank nicht gefunden: '{DB_PFAD}'")
        return None
    try:
        with sqlite3.connect(DB_PFAD) as conn:
            return bank_balance(conn)
    except sqlite3.OperationalError as e:
        print(f"\nFEHLER: Tabelle nicht gefunden – bitte zuerst Daten importieren. ({e})")
        return None



