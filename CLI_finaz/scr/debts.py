import sqlite3
import io
import subprocess
from pathlib import Path
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console as RichConsole
from ui_toolkit import *
from ui_styles import UI


# ──────────────────────────────────────────────
# PFADE
# ──────────────────────────────────────────────

SKRIPT_DIR  = Path(__file__).parent
PROJEKT_DIR = SKRIPT_DIR.parent
DB_PFAD     = PROJEKT_DIR / "db" / "finac.db"


# ──────────────────────────────────────────────
# DATENBANK – TABELLEN
# ──────────────────────────────────────────────

def _tabellen_erstellen(cursor: sqlite3.Cursor) -> None:
    """Legt die zwei Schulden-Tabellen an falls sie noch nicht existieren."""

    # Liste der Schuldner (eine Zeile = eine Person)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schulden_listen (
            listen_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            person       TEXT    NOT NULL UNIQUE,
            erstellt_am  TEXT    NOT NULL
        )
    """)

    # Einzelne Schulden-Einträge pro Person
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schulden_eintraege (
            eintrag_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            listen_id    INTEGER NOT NULL REFERENCES schulden_listen(listen_id) ON DELETE CASCADE,
            betrag       REAL    NOT NULL,
            grund        TEXT,
            datum        TEXT    NOT NULL
        )
    """)

    # Cascade-Deletes nur mit aktiviertem FK-Support
    cursor.execute("PRAGMA foreign_keys = ON")


def _db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PFAD)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ──────────────────────────────────────────────
# DB LESE-HELFER
# ──────────────────────────────────────────────

def _alle_personen(cursor: sqlite3.Cursor) -> list[tuple]:
    """Gibt [(listen_id, person), ...] zurück."""
    cursor.execute("SELECT listen_id, person FROM schulden_listen ORDER BY person")
    return cursor.fetchall()


def _eintraege_fuer_person(cursor: sqlite3.Cursor, listen_id: int) -> list[tuple]:
    """Gibt [(eintrag_id, betrag, grund, datum), ...] zurück."""
    cursor.execute("""
        SELECT eintrag_id, betrag, grund, datum
        FROM schulden_eintraege
        WHERE listen_id = ?
        ORDER BY datum DESC, eintrag_id DESC
    """, (listen_id,))
    return cursor.fetchall()


def _summe_fuer_person(cursor: sqlite3.Cursor, listen_id: int) -> float:
    cursor.execute("""
        SELECT COALESCE(SUM(betrag), 0.0)
        FROM schulden_eintraege
        WHERE listen_id = ?
    """, (listen_id,))
    return cursor.fetchone()[0]


# ──────────────────────────────────────────────
# UI – DRAW FUNKTIONEN
# ──────────────────────────────────────────────

def _draw_debts_panel(ui: UI, cursor: sqlite3.Cursor) -> None:
    """Panel mit allen Personen und ihrer Gesamtschuld."""
    personen = _alle_personen(cursor)

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold #fa7ff6",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#",         width=4,  justify="right",  style="#808080")
    table.add_column("Person",    width=20, style="bold white")
    table.add_column("Summe (€)", width=14, justify="right")
    table.add_column("Einträge",  width=10, justify="right",  style="#888888")

    gesamt = 0.0
    for listen_id, person in personen:
        summe   = _summe_fuer_person(cursor, listen_id)
        eintraege = _eintraege_fuer_person(cursor, listen_id)
        gesamt += summe
        farbe = "bold green" if summe >= 0 else "bold red"
        table.add_row(
            str(listen_id),
            person,
            Text(f"{summe:>+.2f}", style=farbe),
            str(len(eintraege)),
        )

    if not personen:
        table.add_row("–", "[italic #888888]Keine Listen vorhanden[/]", "", "")

    gesamt_text = Text(
        f"Gesamt offene Schulden:  {gesamt:>+.2f} €",
        style="bold #fa7ff6"
    )

    console.print(Panel(
        Group(Align.center(gesamt_text), table),
        title="[bold green]Schulden-Übersicht[/]",
        border_style="bold blue",
        box=box.ROUNDED,
    ))


def _draw_person_table(ui: UI, person: str, eintraege: list[tuple]) -> None:
    """Detailtabelle für eine einzelne Person – via less scrollbar."""
    breite = console.width

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold #fa7ff6",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("ID",        width=6,  justify="right", style="#808080")
    table.add_column("Datum",     width=12, justify="center", style="italic white")
    table.add_column("Betrag (€)",width=14, justify="right")
    table.add_column("Grund",     ratio=1,  style="#888888")

    summe = 0.0
    for eintrag_id, betrag, grund, datum in eintraege:
        farbe  = "bold green" if betrag >= 0 else "bold red"
        summe += betrag
        max_len = max(20, breite - 60)
        grund_roh   = str(grund or "–")
        grund_kurz  = grund_roh[:max_len] + "…" if len(grund_roh) > max_len else grund_roh
        table.add_row(
            str(eintrag_id),
            str(datum),
            Text(f"{betrag:>+.2f}", style=farbe),
            grund_kurz,
        )

    if not eintraege:
        table.add_row("–", "–", "–", "[italic #888888]Keine Einträge[/]")

    titel = Text(
        f"Schulden – {person}  |  Summe: {summe:>+.2f} €  |  {len(eintraege)} Einträge",
        style="#fa7ff6"
    )

    panel = Panel(
        Group(Align.center(titel), table),
        title="[bold green]Finanz-App[/]",
        border_style="bold blue",
        box=box.ROUNDED,
    )

    buf = io.StringIO()
    tmp = RichConsole(file=buf, width=breite, highlight=False, force_terminal=True)
    tmp.print(panel)
    inhalt = buf.getvalue()

    subprocess.run(
        ["less", "-R", "-S", "--prompt= Scrollen: Pfeiltasten | q = zurück"],
        input=inhalt, text=True
    )


# ──────────────────────────────────────────────
# HILFS-INPUT-FUNKTION
# ──────────────────────────────────────────────

def _eingabe_betrag(ui: UI) -> float | None:
    """Fragt nach einem Betrag mit Fehlerabfang. Gibt None zurück bei Abbruch."""
    while True:
        try:
            raw = prompt("  Betrag (€) – negativ = ich schulde, positiv = mir wird geschuldet: ").strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if raw == "":
            ui.draw_header("[yellow]Kein Betrag eingegeben.[/yellow]")
            continue

        # Deutsches Komma erlauben
        raw = raw.replace(",", ".")
        try:
            betrag = float(raw)
            return betrag
        except ValueError:
            ui.draw_header(f"[red]Ungültige Eingabe '[bold]{raw}[/bold]' – bitte eine Zahl eingeben (z.B. -35.50 oder 100).[/red]")


# ──────────────────────────────────────────────
# EDIT – PERSON EINTRÄGE BEARBEITEN
# ──────────────────────────────────────────────

def _edit_person(ui: UI, listen_id: int, person: str) -> None:
    """
    Untermenü für eine einzelne Person.
    Kommandos: add | remove | back | exit
    """
    commands = ["add", "remove", "back", "exit"]

    while True:
        with _db_connect() as conn:
            cur = conn.cursor()
            eintraege = _eintraege_fuer_person(cur, listen_id)

        _draw_person_table(ui, person, eintraege)

        eintrag_ids = [str(e[0]) for e in eintraege]
        completer   = WordCompleter(commands + eintrag_ids, ignore_case=True)

        try:
            user_input = prompt(
                f"edit ({person}) -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        # ── Eintrag hinzufügen ───────────────────────────────────────────────
        elif user_input == "add":
            betrag = _eingabe_betrag(ui)
            if betrag is None:
                continue

            try:
                grund = prompt("  Grund (optional, Enter = leer): ").strip()
            except (KeyboardInterrupt, EOFError):
                continue

            datum = datetime.now().strftime("%d.%m.%Y")

            with _db_connect() as conn:
                conn.execute("""
                    INSERT INTO schulden_eintraege (listen_id, betrag, grund, datum)
                    VALUES (?, ?, ?, ?)
                """, (listen_id, betrag, grund or None, datum))
                conn.commit()

            ui.draw_header(
                f"[green]Eintrag hinzugefügt:[/green] "
                f"[bold]{betrag:+.2f} €[/bold]"
                + (f"  –  {grund}" if grund else "")
            )

        # ── Eintrag entfernen ────────────────────────────────────────────────
        elif user_input == "remove":
            if not eintraege:
                ui.draw_header("[yellow]Keine Einträge vorhanden.[/yellow]")
                continue

            id_completer = WordCompleter(eintrag_ids, ignore_case=True)
            try:
                raw_id = prompt(
                    "  Eintrag-ID zum Löschen: ",
                    completer=id_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not raw_id.isdigit() or raw_id not in eintrag_ids:
                ui.draw_header(f"[red]Ungültige ID '[bold]{raw_id}[/bold]'.[/red]")
                continue

            with _db_connect() as conn:
                conn.execute(
                    "DELETE FROM schulden_eintraege WHERE eintrag_id = ?",
                    (int(raw_id),)
                )
                conn.commit()

            ui.draw_header(f"[green]Eintrag [bold]{raw_id}[/bold] gelöscht.[/green]")

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")


# ──────────────────────────────────────────────
# EDIT – LISTEN VERWALTEN
# ──────────────────────────────────────────────

def _debts_edit(ui: UI) -> None:
    """
    Untermenü zum Anlegen, Löschen und Bearbeiten von Schuldner-Listen.
    Kommandos: new | delete | edit | back | exit
    """
    commands = ["new", "delete", "edit", "back", "exit"]

    while True:
        with _db_connect() as conn:
            cur = conn.cursor()
            _draw_debts_panel(ui, cur)
            personen = _alle_personen(cur)

        personen_namen = [p[1] for p in personen]
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "debts edit -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        # ── Neue Liste ───────────────────────────────────────────────────────
        elif user_input == "new":
            try:
                person = prompt("  Name der Person: ").strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not person:
                ui.draw_header("[yellow]Kein Name eingegeben.[/yellow]")
                continue

            datum = datetime.now().strftime("%d.%m.%Y")
            try:
                with _db_connect() as conn:
                    conn.execute(
                        "INSERT INTO schulden_listen (person, erstellt_am) VALUES (?, ?)",
                        (person, datum)
                    )
                    conn.commit()
                ui.draw_header(f"[green]Liste für '[bold]{person}[/bold]' erstellt.[/green]")
            except sqlite3.IntegrityError:
                ui.draw_header(f"[yellow]Person '[bold]{person}[/bold]' existiert bereits.[/yellow]")

        # ── Liste löschen ────────────────────────────────────────────────────
        elif user_input == "delete":
            if not personen:
                ui.draw_header("[yellow]Keine Listen vorhanden.[/yellow]")
                continue

            del_completer = WordCompleter(personen_namen, ignore_case=True)
            try:
                person = prompt(
                    "  Person löschen: ",
                    completer=del_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            match = [(lid, p) for lid, p in personen if p.lower() == person.lower()]
            if not match:
                ui.draw_header(f"[red]Person '[bold]{person}[/bold]' nicht gefunden.[/red]")
                continue

            listen_id, person_name = match[0]
            with _db_connect() as conn:
                conn.execute(
                    "DELETE FROM schulden_listen WHERE listen_id = ?",
                    (listen_id,)
                )
                conn.commit()
            ui.draw_header(
                f"[green]Liste für '[bold]{person_name}[/bold]' und alle Einträge gelöscht.[/green]"
            )

        # ── Liste bearbeiten ─────────────────────────────────────────────────
        elif user_input == "edit":
            if not personen:
                ui.draw_header("[yellow]Keine Listen vorhanden.[/yellow]")
                continue

            edit_completer = WordCompleter(personen_namen, ignore_case=True)
            try:
                person = prompt(
                    "  Person auswählen: ",
                    completer=edit_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            match = [(lid, p) for lid, p in personen if p.lower() == person.lower()]
            if not match:
                ui.draw_header(f"[red]Person '[bold]{person}[/bold]' nicht gefunden.[/red]")
                continue

            listen_id, person_name = match[0]
            _edit_person(ui, listen_id, person_name)

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")


# ──────────────────────────────────────────────
# SHOW DEBTS
# ──────────────────────────────────────────────

def _show_debts(ui: UI) -> None:
    """
    Untermenü zum Anzeigen von Schulden.
    Kommandos: all | person | back | exit
    """
    commands = ["all", "person", "back", "exit"]

    while True:
        with _db_connect() as conn:
            cur = conn.cursor()
            personen = _alle_personen(cur)

        personen_namen = [p[1] for p in personen]
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "show debts -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        # ── Alle anzeigen ────────────────────────────────────────────────────
        elif user_input == "all":
            with _db_connect() as conn:
                cur = conn.cursor()
                _draw_debts_panel(ui, cur)

        # ── Einzelne Person anzeigen ─────────────────────────────────────────
        elif user_input == "person":
            if not personen:
                ui.draw_header("[yellow]Keine Listen vorhanden.[/yellow]")
                continue

            per_completer = WordCompleter(personen_namen, ignore_case=True)
            try:
                person = prompt(
                    "  Person auswählen: ",
                    completer=per_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            match = [(lid, p) for lid, p in personen if p.lower() == person.lower()]
            if not match:
                ui.draw_header(f"[red]Person '[bold]{person}[/bold]' nicht gefunden.[/red]")
                continue

            listen_id, person_name = match[0]
            with _db_connect() as conn:
                cur = conn.cursor()
                eintraege = _eintraege_fuer_person(cur, listen_id)
            _draw_person_table(ui, person_name, eintraege)

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")


# ──────────────────────────────────────────────
# HAUPTMENÜ
# ──────────────────────────────────────────────

def manage_debts() -> None:
    """
    Einstiegspunkt aus start_balance_overview().
    Kommandos: show debts | debts edit | help | back | exit
    """
    ui = UI()

    # Tabellen anlegen falls noch nicht vorhanden
    try:
        with _db_connect() as conn:
            _tabellen_erstellen(conn.cursor())
            conn.commit()
    except sqlite3.OperationalError as e:
        ui.draw_header(f"[red]FEHLER (Datenbank):[/red] {e}")
        return

    commands = ["show debts", "debts edit", "help", "back", "exit"]

    while True:
        with _db_connect() as conn:
            cur = conn.cursor()
            _draw_debts_panel(ui, cur)

        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "debts -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        elif user_input == "help":
            ui.draw_header(
                "[bold #fa7ff6]show debts[/]   – Schulden anzeigen\n"
                "  [#888888]all[/]            – Übersicht aller Personen mit Gesamtsumme\n"
                "  [#888888]person[/]         – Detailansicht einer einzelnen Person\n\n"
                "[bold #fa7ff6]debts edit[/]   – Listen und Einträge verwalten\n"
                "  [#888888]new[/]            – Neue Schuldner-Liste anlegen\n"
                "  [#888888]delete[/]         – Schuldner-Liste löschen (inkl. alle Einträge)\n"
                "  [#888888]edit[/]           – Person auswählen und Einträge bearbeiten\n"
                "    [#888888]add[/]          – Neuen Schulden-Eintrag hinzufügen\n"
                "    [#888888]remove[/]       – Eintrag per ID löschen\n\n"
                "[bold #fa7ff6]back[/]         – Zurück zur Balance-Übersicht\n"
                "[bold #fa7ff6]exit[/]         – App beenden"
            )

        elif user_input == "show debts":
            _show_debts(ui)

        elif user_input == "debts edit":
            _debts_edit(ui)

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")


# ──────────────────────────────────────────────
# STANDALONE
# ──────────────────────────────────────────────

if __name__ == "__main__":
    manage_debts()