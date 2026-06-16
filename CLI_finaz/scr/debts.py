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
    """
    Vollständige Schulden-Übersicht:
    - Gesamtsumme + aufgeteilt in Forderungen / Schulden
    - Pro Person: alle Einträge mit Datum, Betrag, Grund
    """
    personen  = _alle_personen(cursor)
    breite    = console.width

    # ── Gesamtsummen berechnen ───────────────────────────────────────────────
    gesamt       = 0.0
    gesamt_ford  = 0.0   # positiv = mir wird geschuldet
    gesamt_schuld = 0.0  # negativ = ich schulde

    personen_daten = []  # [(person, summe, eintraege), ...]
    for listen_id, person in personen:
        summe     = _summe_fuer_person(cursor, listen_id)
        eintraege = _eintraege_fuer_person(cursor, listen_id)
        gesamt   += summe
        if summe >= 0:
            gesamt_ford   += summe
        else:
            gesamt_schuld += summe
        personen_daten.append((person, summe, eintraege))

    # ── Kopf-Gruppe ──────────────────────────────────────────────────────────
    kopf = Table.grid(expand=True, padding=(0, 2))
    kopf.add_column(justify="center", ratio=1)
    kopf.add_column(justify="center", ratio=1)
    kopf.add_column(justify="center", ratio=1)

    kopf.add_row(
        Text(f"Total outstanding:  {gesamt:>+.2f} €",   style="bold #fa7ff6"),
        Text(f"Receivables:  {gesamt_ford:>+.2f} €",   style="bold green"),
        Text(f"Debts:  {gesamt_schuld:>+.2f} €",       style="bold red"),
    )

    # ── Pro-Person-Tabellen ──────────────────────────────────────────────────
    alle_gruppen = [Align.center(kopf), Text("")]  # Abstand nach Kopf

    if not personen_daten:
        alle_gruppen.append(
            Align.center(Text("No lists found", style="italic #888888"))
        )
    else:
        for person, summe, eintraege in personen_daten:
            farbe_summe = "bold green" if summe >= 0 else "bold red"

            # Person-Header
            person_header = Text(
                f"  {person}  –  Total: {summe:>+.2f} €  ({len(eintraege)} entries)",
                style=f"bold white"
            )

            # Eintrags-Tabelle
            ptable = Table(
                box=box.SIMPLE,
                show_header=True,
                header_style="#808080",
                expand=True,
                padding=(0, 1),
                show_edge=False,
            )
            ptable.add_column("ID",        width=5,  justify="right", style="#555555")
            ptable.add_column("Date",      width=12, justify="center", style="italic #aaaaaa")
            ptable.add_column("Amount (€)",width=13, justify="right")
            ptable.add_column("Reason",    ratio=1,  style="#888888")

            if eintraege:
                for eintrag_id, betrag, grund, datum in eintraege:
                    farbe    = "bold green" if betrag >= 0 else "bold red"
                    max_len  = max(20, breite - 55)
                    grund_roh  = str(grund or "–")
                    grund_kurz = grund_roh[:max_len] + "…" if len(grund_roh) > max_len else grund_roh
                    ptable.add_row(
                        str(eintrag_id),
                        str(datum),
                        Text(f"{betrag:>+.2f}", style=farbe),
                        grund_kurz,
                    )
            else:
                ptable.add_row("–", "–", "–", "[italic #555555]No entries[/]")

            alle_gruppen.append(person_header)
            alle_gruppen.append(ptable)
            alle_gruppen.append(Text(""))  # Leerzeile zwischen Personen

    return Panel(
        Group(*alle_gruppen),
        title="[bold green]Debt Overview[/]",
        border_style="bold blue",
        box=box.ROUNDED,
    )


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
    table.add_column("Date",      width=12, justify="center", style="italic white")
    table.add_column("Amount (€)",width=14, justify="right")
    table.add_column("Reason",    ratio=1,  style="#888888")

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
        table.add_row("–", "–", "–", "[italic #888888]No entries[/]")

    titel = Text(
        f"Debts – {person}  |  Total: {summe:>+.2f} €  |  {len(eintraege)} entries",
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
        ["less", "-R", "-S", "--prompt= Scroll: arrow keys | q = back"],
        input=inhalt, text=True
    )


# ──────────────────────────────────────────────
# HILFS-INPUT-FUNKTION
# ──────────────────────────────────────────────

def _eingabe_betrag(ui: UI) -> float | None:
    """Fragt nach einem Betrag mit Fehlerabfang. Gibt None zurück bei Abbruch."""
    while True:
        try:
            raw = prompt("  Amount (€) – negative = I owe, positive = I am owed: ").strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if raw == "":
            ui.draw_header("[yellow]No amount entered.[/yellow]")
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
            #ui.draw_exit_panel()
            return

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        
        elif user_input == "add":
            betrag = _eingabe_betrag(ui)
            if betrag is None:
                continue

            try:
                grund = prompt("  Reason (optional, Enter = skip): ").strip()
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
                f"[green]Entry added:[/green] "
                f"[bold]{betrag:+.2f} €[/bold]"
                + (f"  –  {grund}" if grund else "")
            )


        elif user_input == "remove":
            if not eintraege:
                ui.draw_header("[yellow]No entries found.[/yellow]")
                continue


            auswahl_map = {}  # display string → eintrag_id
            for eintrag_id, betrag, grund, datum in eintraege:
                vorzeichen = "+" if betrag >= 0 else ""
                grund_kurz = str(grund or "–")[:30]
                key = f"{eintrag_id}  {datum}  {vorzeichen}{betrag:.2f}€  {grund_kurz}"
                auswahl_map[key] = eintrag_id

            console.print(
                Panel(
                    "\n".join(
                        f"  [#808080]{k}[/]" for k in auswahl_map
                    ),
                    title="[bold #fa7ff6]Select entry[/]",
                    border_style="blue",
                    box=box.ROUNDED,
                )
            )

            id_completer = WordCompleter(list(auswahl_map.keys()), ignore_case=True)
            try:
                auswahl = prompt(
                    "  Entry to delete (Tab = suggestions): ",
                    completer=id_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue


            if auswahl.isdigit() and int(auswahl) in auswahl_map.values():
                del_id = int(auswahl)
            elif auswahl in auswahl_map:
                del_id = auswahl_map[auswahl]
            else:
                ui.draw_header(f"[red]Invalid selection.[/red]")
                continue

            with _db_connect() as conn:
                conn.execute(
                    "DELETE FROM schulden_eintraege WHERE eintrag_id = ?",
                    (del_id,)
                )
                conn.commit()

            ui.draw_header(f"[green]Entry [bold]{del_id}[/bold] deleted.[/green]")

        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")


# ──────────────────────────────────────────────
# EDIT – LISTEN VERWALTEN
# ──────────────────────────────────────────────

def _debts_edit(ui: UI) -> None:
    
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
            #ui.draw_exit_panel()
            return

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        # ── Neue Liste ───────────────────────────────────────────────────────
        elif user_input == "new":
            try:
                person = prompt("  Person's name: ").strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not person:
                ui.draw_header("[yellow]No name entered.[/yellow]")
                continue

            datum = datetime.now().strftime("%d.%m.%Y")
            try:
                with _db_connect() as conn:
                    conn.execute(
                        "INSERT INTO schulden_listen (person, erstellt_am) VALUES (?, ?)",
                        (person, datum)
                    )
                    conn.commit()
                ui.draw_header(f"[green]List for '[bold]{person}[/bold]' created.[/green]")
            except sqlite3.IntegrityError:
                ui.draw_header(f"[yellow]Person '[bold]{person}[/bold]' already exists.[/yellow]")

        # ── delete list ──────────────────────────────────────────────────────
        elif user_input == "delete":
            if not personen:
                ui.draw_header("[yellow]No lists found.[/yellow]")
                continue

            del_completer = WordCompleter(personen_namen, ignore_case=True)
            try:
                person = prompt(
                    "  Person to delete: ",
                    completer=del_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            match = [(lid, p) for lid, p in personen if p.lower() == person.lower()]
            if not match:
                ui.draw_header(f"[red]Person '[bold]{person}[/bold]' not found.[/red]")
                continue

            listen_id, person_name = match[0]
            with _db_connect() as conn:
                conn.execute(
                    "DELETE FROM schulden_listen WHERE listen_id = ?",
                    (listen_id,)
                )
                conn.commit()
            ui.draw_header(
                f"[green]List for '[bold]{person_name}[/bold]' and all entries deleted.[/green]"
            )

        # ── edit list ────────────────────────────────────────────────────────
        elif user_input == "edit":
            if not personen:
                ui.draw_header("[yellow]No lists found.[/yellow]")
                continue

            edit_completer = WordCompleter(personen_namen, ignore_case=True)
            try:
                person = prompt(
                    "  Select person: ",
                    completer=edit_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            match = [(lid, p) for lid, p in personen if p.lower() == person.lower()]
            if not match:
                ui.draw_header(f"[red]Person '[bold]{person}[/bold]' not found.[/red]")
                continue

            listen_id, person_name = match[0]
            _edit_person(ui, listen_id, person_name)

        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")


# ──────────────────────────────────────────────
# SHOW DEBTS
# ──────────────────────────────────────────────

def _show_debts(ui: UI) -> None:
    
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
            #ui.draw_exit_panel()
            return

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        
        elif user_input == "all":
            with _db_connect() as conn:
                cur = conn.cursor()
                _draw_debts_panel(ui, cur)

        
        elif user_input == "person":
            if not personen:
                ui.draw_header("[yellow]No lists found.[/yellow]")
                continue

            per_completer = WordCompleter(personen_namen, ignore_case=True)
            try:
                person = prompt(
                    "  Select person: ",
                    completer=per_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            match = [(lid, p) for lid, p in personen if p.lower() == person.lower()]
            if not match:
                ui.draw_header(f"[red]Person '[bold]{person}[/bold]' not found.[/red]")
                continue

            listen_id, person_name = match[0]
            with _db_connect() as conn:
                cur = conn.cursor()
                eintraege = _eintraege_fuer_person(cur, listen_id)
            _draw_person_table(ui, person_name, eintraege)

        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")


# ──────────────────────────────────────────────
# HAUPTMENÜ
# ──────────────────────────────────────────────

def manage_debts() -> None:
    
    ui = UI()

    # Tabellen anlegen falls noch nicht vorhanden
    try:
        with _db_connect() as conn:
            _tabellen_erstellen(conn.cursor())
            conn.commit()
    except sqlite3.OperationalError as e:
        ui.draw_header(f"[red]ERROR (database):[/red] {e}")
        return

    commands = ["show debts", "debts edit", "help", "back", "exit"]
    
    
    with _db_connect() as conn:
        cur = conn.cursor()
        _draw_debts_panel(ui, cur)

    while True:

        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "debts -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            #ui.draw_exit_panel()
            return

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        elif user_input == "help":
            console.print("\n[bold cyan]Available commands:[/bold cyan]")
            console.print("  [green]show debts[/green]    – show the debts overview")
            console.print("    [green]all[/green]         – summary of all people with totals")
            console.print("    [green]person[/green]      – detailed view for one person")
            console.print("  [green]debts edit[/green]    – manage lists and entries")
            console.print("    [green]new[/green]         – create a new debt list for a person")
            console.print("    [green]delete[/green]      – delete a person's list and all entries")
            console.print("    [green]edit[/green]        – select a person to edit their entries")
            console.print("      [green]add[/green]       – add a new debt entry")
            console.print("      [green]remove[/green]    – delete an entry by ID")
            console.print("  [green]back[/green]          – go back")
            console.print("  [green]exit[/green]          – quit the program\n")

        elif user_input == "show debts":
            _show_debts(ui)

        elif user_input == "debts edit":
            _debts_edit(ui)

        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")


