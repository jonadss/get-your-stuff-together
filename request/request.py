
import sqlite3
import pandas as pd

conn = sqlite3.connect('db/transaktion.db')
cursor = conn.cursor()

cursor.execute("""  SELECT buchungs_id FROM transaktionen
                    ORDER BY buchungs_id     DESC""")
inhalt = cursor.fetchall()

for inhalt in inhalt:
    print(inhalt)
