import sqlite3
from pathlib import Path


#Import
SKRIPT_DIR = Path(__file__).parent         
PROJEKT_DIR = SKRIPT_DIR.parent    
DB_PFAD = PROJEKT_DIR / "db" / "transaktion.db"


# ──────────────────────────────────────────────
# update verwendungszweck
# ──────────────────────────────────────────────
def update_verwendung_to_kategorie(database):  
    search_data_test = ["EDEKA","Penny"]    
    cursor = database.cursor()
    cursor.execute("""
        SELECT buchungs_id, verwendungszweck
        FROM transaktionen
        ORDER BY buchungs_id                          
    """)
    row = cursor.fetchall()

    if row:
        for x in range(len(row)):
            id, zweck = row[x]
            if any(wort in zweck for wort in search_data_test):
                cursor.execute("""  
                UPDATE transaktionen
                SET verwendungszweck = "Lebensmittel"
                WHERE buchungs_id = ?
                """, (id,))         
    else:
        print("  Noch keine Daten in der Datenbank.")
        print(f"{'─' * 70}\n")
        return 0.0




#main
if __name__ == "__main__":
    if not DB_PFAD.exists():
        print(f"\nFEHLER: Datenbank nicht gefunden: '{DB_PFAD}'")
        print("Bitte zuerst conv_csv-sql_lite.py ausführen.\n")
        raise SystemExit(1)

    with sqlite3.connect(DB_PFAD) as conn:
  
        test(conn)
