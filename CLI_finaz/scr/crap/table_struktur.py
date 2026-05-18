import sqlite3

#NICHT EINGEBUNDEN

# ──────────────────────────────────────────────
# Database for all transaction
# ──────────────────────────────────────────────
def tabel_create_transaction(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction (
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

