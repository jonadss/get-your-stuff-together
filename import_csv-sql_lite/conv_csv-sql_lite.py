import sqlite3
import pandas as pd
import re

def initialisiere_tabelle(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaktionen (
            buchungs_id INTEGER PRIMARY KEY AUTOINCREMENT,
            buchungstag TEXT,
            uhrzeit TEXT,
            betrag REAL,
            saldo_nach_buchung REAL,
            waehrung TEXT,
            zahlungsbeteiligter TEXT,
            verwendungszweck TEXT,
            UNIQUE(buchungstag, uhrzeit, betrag, zahlungsbeteiligter, verwendungszweck)
        )
    ''')
    conn.commit()

def extrahiere_zeit(text):
    if not text or pd.isna(text):
        return "00:00:00"
    match = re.search(r'(\d{2}:\d{2}:\d{2})', str(text))
    return match.group(1) if match else "00:00:00"

def import_bank_csv(csv_pfad, db_pfad):
    try:
        conn = sqlite3.connect(db_pfad)
        initialisiere_tabelle(conn)
        
        # WICHTIG: Wir füllen NaN sofort mit leerem Text
        df = pd.read_csv(csv_pfad, sep=';', encoding='utf-8-sig', dtype=str).fillna("")

        neu = 0
        alt = 0

        def clean_num(val):
            if val == "": return 0.0
            return float(val.replace('.', '').replace(',', '.'))

        for _, row in df.iterrows():
            # Daten extrahieren
            tag = row['Buchungstag']
            zweck = row['Verwendungszweck']
            uhrzeit = extrahiere_zeit(zweck)
            betrag = clean_num(row['Betrag'])
            saldo = clean_num(row['Saldo nach Buchung'])
            beteiligter = row['Name Zahlungsbeteiligter']
            waehrung = row['Waehrung']

            # INSERT OR IGNORE nutzt den UNIQUE Constraint
            sql = '''INSERT OR IGNORE INTO transaktionen 
                     (buchungstag, uhrzeit, betrag, saldo_nach_buchung, waehrung, zahlungsbeteiligter, verwendungszweck)
                     VALUES (?, ?, ?, ?, ?, ?, ?)'''
            
            cur = conn.cursor()
            cur.execute(sql, (tag, uhrzeit, betrag, saldo, waehrung, beteiligter, zweck))
            
            if cur.rowcount > 0:
                neu += 1
            else:
                alt += 1

        conn.commit()
        conn.close()
        print(f"Ergebnis: {neu} neue Buchungen, {alt} Duplikate ignoriert.")

    except Exception as e:
        print(f"Fehler: {e}")


# --- Start ---
if __name__ == "__main__":
    meine_csv = 'import_csv-sql_lite/csv/kontoauszug copy.csv' 
    meine_db = 'db/transaktion.db'

    try:
        # Versuch, den Import auszuführen
        import_bank_csv(meine_csv, meine_db)
        
    except FileNotFoundError:
        print(f"Fehler: Die Datei '{meine_csv}' wurde im Ordner nicht gefunden.")
    except KeyError as e:
        print(f"Fehler: Eine erwartete Spalte fehlt in der CSV: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


