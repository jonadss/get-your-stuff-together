import sqlite3
from pathlib import Path
from tabulate import tabulate


# ──────────────────────────────────────────────
# PFAD  (relativ zu diesem Skript)
# ──────────────────────────────────────────────

SKRIPT_DIR = Path(__file__).parent          # .../import_csv-sql_lite/
PROJEKT_DIR = SKRIPT_DIR.parent             # .../get-your-stuff-together/
DB_PFAD = PROJEKT_DIR / "db" / "transaktion.db"


# ──────────────────────────────────────────────
# ABFRAGE-FUNKTIONEN
# ──────────────────────────────────────────────

def overview(database: sqlite3.Connection) -> None:
    """
    Zeigt alle Transaktionen chronologisch – neueste Buchung oben.

    Sortierung:
      1. Datum DESC             → neuestes Datum zuerst
      2. buchungs_id            → innerhalb desselben Tages
    """
    cursor = database.cursor()
    cursor.execute("""
        SELECT buchungs_id, buchungstag, betrag, saldo_nach_buchung, verwendungszweck
        FROM transaktionen
        ORDER BY
            SUBSTR(buchungstag, 7, 4) DESC,  
            SUBSTR(buchungstag, 4, 2) DESC,  
            SUBSTR(buchungstag, 1, 2) DESC,  
            buchungs_id                       
                                             
                                             
    """)
    content = cursor.fetchall()
    headers = ["ID", "Datum", "Betrag (€)", "Saldo (€)", "Verwendungszweck"]

    print(f"\n{'─' * 70}")
    print(f"  Transaktions-Übersicht  –  {len(content)} Einträge  (neueste oben)")
    print(f"{'─' * 70}")
    print(tabulate(
        content,
        headers=headers,
        tablefmt="outline",
        floatfmt=".2f",
    ))


def bank_balance(database: sqlite3.Connection) -> float:
    """
    Liest den Kontostand der letzten Buchung (höchste buchungs_id).
    Gibt den Saldo als float zurück und gibt ihn auf der Konsole aus.
    """
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
        print(f"  Aktueller Kontostand : {saldo:>12.2f} €")
        print(f"{'─' * 70}\n")
        return saldo
    else:
        print("  Noch keine Daten in der Datenbank.")
        print(f"{'─' * 70}\n")
        return 0.0


def test(database: sqlite3.Connection):
    cursor = database.cursor()
    cursor.execute("""
        SELECT verwendungszweck
        FROM transaktionen
        ORDER BY
            SUBSTR(buchungstag, 7, 4) DESC,  
            SUBSTR(buchungstag, 4, 2) DESC,  
            SUBSTR(buchungstag, 1, 2) DESC,  
            buchungs_id
        """)
       
    row = cursor.fetchone()
    print(row[0])


# ──────────────────────────────────────────────
# EINSTIEGSPUNKT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if not DB_PFAD.exists():
        print(f"\nFEHLER: Datenbank nicht gefunden: '{DB_PFAD}'")
        print("Bitte zuerst conv_csv-sql_lite.py ausführen.\n")
        raise SystemExit(1)

    with sqlite3.connect(DB_PFAD) as conn:
        overview(conn)
        bank_balance(conn)



