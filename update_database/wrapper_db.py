import sqlite3


DB_PFAD = PROJEKT_DIR / "db" / "transaktion.db"


def test():  
    
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





if __name__ == "__main__":
    if not DB_PFAD.exists():
        print(f"\nFEHLER: Datenbank nicht gefunden: '{DB_PFAD}'")
        print("Bitte zuerst conv_csv-sql_lite.py ausführen.\n")
        raise SystemExit(1)

    with sqlite3.connect(DB_PFAD) as conn:
  
        test(conn)



food = [edeka]