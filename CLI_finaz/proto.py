"""
Finanz-App — Textual Prototype
"""
import sys, os, math, datetime, random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scr"))

from rich.text import Text
from rich.table import Table
from rich import box as rbox
from textual.app import App, ComposeResult
from textual.widgets import Header, Input, Static, OptionList, ContentSwitcher, Tabs, Tab
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal, VerticalScroll

try:
    from request import overview, start_saldo_request, DB_PFAD
    import sqlite3
    HAS_DB = True
except Exception:
    HAS_DB = False

TAB_COMMANDS = {
    "balance":    ["show history", "importer", "evaluation", "debts", "categories", "budget", "help", "exit"],
    "history":    ["refresh", "back", "exit"],
    "importer":   ["choose path", "import", "undo import", "delete csv", "delete db", "back", "exit"],
    "evaluation": ["comparison", "seasonal", "recurring", "income", "forecast", "settings", "back", "exit"],
    "debts":      ["add debt", "pay debt", "show debts", "back", "exit"],
    "categories": ["add", "remove", "list", "back", "exit"],
    "budget":     ["set budget", "show budget", "back", "exit"],
}

TABS = [
    ("balance",    "💰 Balance"),
    ("history",    "📋 History"),
    ("importer",   "📥 Importer"),
    ("evaluation", "📊 Evaluation"),
    ("debts",      "💸 Debts"),
    ("categories", "🏷  Categories"),
    ("budget",     "🎯 Budget"),
]


# ─── Frosch mit Sternenhimmel ─────────────────────────────────────────────────

# Frosch-Frames (8 Zeichen breit)
_FROG = {
    "normal": [
        " @    @ ",
        "(------)",
        "(>____<)",
        "^^    ^^",
    ],
    "blink": [
        " -    - ",
        "(------)",
        "(>____<)",
        "^^    ^^",
    ],
    "jump": [
        " @    @ ",
        "(------)",
        "(>____<)",
        " /    \\ ",
    ],
    "squat": [
        " @    @ ",
        "(------)",
        "(______)",
        " ^^  ^^ ",
    ],
    "open": [
        " @    @ ",
        "(------)",
        "(>    <)",
        " /    \\ ",
    ],
}

_W, _H = 14, 24   # Raster (Breite = sidebar 16 - 2 border)


class BigFrog(Static):
    def on_mount(self) -> None:
        self._f = 0
        rng = random.Random(7)
        # Sterne: (x, y_float, char, phase, speed)
        self._stars = [
            (rng.randint(0, _W - 1),
             rng.uniform(0, _H),
             rng.choice("✦✧★·*"),
             rng.uniform(0, math.pi * 2),
             rng.uniform(0.4, 1.2))
            for _ in range(28)
        ]
        self.set_interval(0.13, self._tick)

    def _tick(self) -> None:
        self._f += 1
        t = self._f * 0.13

        # ── Sterne scrollen nach unten ──
        grid = [[(" ", "#111100")] * _W for _ in range(_H)]
        for sx, sy0, ch, phase, spd in self._stars:
            sy  = (sy0 + self._f * spd * 0.09) % _H
            iy  = int(sy)
            bri = (math.sin(t * 1.8 + phase) + 1) / 2
            if bri > 0.75:   col, star = "bold yellow", "✦"
            elif bri > 0.5:  col, star = "#ccaa00",     "✧"
            elif bri > 0.25: col, star = "#665500",     "·"
            else:             col, star = "#221100",     " "
            if 0 <= iy < _H:
                grid[iy][sx] = (star, col)

        # ── Frosch reist von oben nach unten ──
        # base_y: -4 … _H+4, dann von vorne
        total   = _H + 8
        base_y  = (self._f * 0.28) % total - 4   # langsam runter

        # Hüpf-Offset: Sinus erzeugt kleines Auf/Ab während der Reise
        hop_sin = math.sin(self._f * 0.55)
        hop_off = -int(abs(hop_sin) * 2)

        # Frame abhängig vom Hüpfzustand
        if abs(hop_sin) > 0.7:
            frame_name = "jump"
        elif abs(hop_sin) < 0.12:
            frame_name = "squat"
        elif self._f % 40 < 3:
            frame_name = "blink"
        else:
            frame_name = "normal"

        frog_lines = _FROG[frame_name]
        gy  = int(base_y) + hop_off
        gx  = (_W - 8) // 2          # horizontal zentrieren (8 breit)
        grn = int(110 + 70 * abs(math.sin(t * 0.4)))
        er  = int(200 + 55 * abs(math.sin(t * 1.1)))

        # Frosch ins Raster einzeichnen
        for li, line in enumerate(frog_lines):
            for ci, ch in enumerate(line):
                giy, gix = gy + li, gx + ci
                if 0 <= giy < _H and 0 <= gix < _W:
                    if ch == " ":
                        grid[giy][gix] = (" ", "#0a1a0a")
                    elif ch in "@-" and li == 0:
                        grid[giy][gix] = (ch, f"bold rgb({er},60,60)")
                    elif ch in "^/\\":
                        grid[giy][gix] = (ch, "#1a5c1a")
                    else:
                        grid[giy][gix] = (ch, f"bold rgb(40,{grn},40)")

        # Text ausgeben
        out = Text()
        for row in grid:
            for ch, col in row:
                out.append(ch, style=col)
            out.append("\n")
        self.update(out)


class PulseTitle(Static):
    def on_mount(self) -> None:
        self._f = 0
        self.set_interval(0.07, self._tick)

    def _tick(self) -> None:
        self._f += 1
        t = self._f * 0.07
        r = int(127 + 127 * math.sin(t * 2))
        g = int(127 + 127 * math.sin(t * 2 + 2))
        b = int(127 + 127 * math.sin(t * 2 + 4))
        self.update(Text.from_markup(
            f"[bold rgb({r},{g},{b})]  Finanz-App  ●  get-your-stuff-together[/bold rgb({r},{g},{b})]"
        ))


# ─── Content-Views ────────────────────────────────────────────────────────────

class BalanceView(Static):
    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y  %H:%M")
        if HAS_DB:
            try:
                saldo = start_saldo_request()
                style = "bold green" if saldo >= 0 else "bold red"
                self.update(Text.from_markup(
                    f"[bold #fa7ff6]Balance Overview[/]\n\n"
                    f"[{style}]  Saldo:  {saldo:+.2f} €[/{style}]\n\n"
                    f"[dim]{date_str}[/dim]"
                ))
                return
            except Exception:
                pass
        self.update(Text.from_markup(
            f"[bold #fa7ff6]Balance Overview[/]\n\n"
            f"[dim]Keine Datenbank — bitte CSV importieren.[/dim]\n\n"
            f"[#808080]{date_str}[/#808080]"
        ))


class HistoryView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static(id="history-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        w = self.query_one("#history-content", Static)
        if not HAS_DB:
            w.update(Text.from_markup("[dim]Keine DB.[/dim]"))
            return
        try:
            rows = overview(sqlite3.connect(DB_PFAD))
            if not rows:
                w.update(Text.from_markup("[dim]Keine Transaktionen.[/dim]"))
                return
            table = Table(box=rbox.SIMPLE, show_header=True,
                          header_style="bold #fa7ff6", expand=True, padding=(0, 1))
            table.add_column("Datum",      width=12, justify="center")
            table.add_column("Betrag €",   width=12, justify="right")
            table.add_column("Saldo €",    width=12, justify="right")
            table.add_column("Kategorie",  width=14)
            table.add_column("Verwendung", ratio=1)
            for _, datum, betrag, saldo, zweck, cat in rows[:80]:
                s = "bold green" if (betrag or 0) >= 0 else "bold red"
                table.add_row(
                    str(datum or "–"),
                    Text(f"{betrag:+.2f}" if betrag is not None else "–", style=s),
                    str(f"{saldo:.2f}" if saldo is not None else "–"),
                    Text(str(cat or "–"), style="#aaaaaa"),
                    Text(str(zweck or "–")[:60], style="#666666"),
                )
            w.update(table)
        except Exception as e:
            w.update(Text.from_markup(f"[red]Fehler:[/red] {e}"))


class PlaceholderView(Static):
    def set_tab(self, name: str) -> None:
        self.update(Text.from_markup(
            f"[bold #fa7ff6]{name}[/]\n\n"
            f"[dim]Noch nicht implementiert.[/dim]\n\n"
            f"[#808080]Benutze das Eingabefeld unten für Befehle.[/#808080]"
        ))


class LogView(Static):
    def on_mount(self) -> None:
        self._lines: list[str] = ["[dim]Bereit.[/dim]"]
        self._refresh()

    def add(self, line: str) -> None:
        self._lines.append(line)
        if len(self._lines) > 20:
            self._lines = self._lines[-20:]
        self._refresh()

    def _refresh(self) -> None:
        self.update(Text.from_markup("\n".join(self._lines)))


# ─── Autocomplete Dropdown ────────────────────────────────────────────────────

class CommandCompleter(OptionList):

    def show_for(self, query: str, commands: list[str]) -> None:
        self.clear_options()
        matches = [c for c in commands if c.startswith(query.lower())] if query else commands
        if not matches:
            self.display = False
            return
        for m in matches:
            n = len(query)
            label = Text.from_markup(
                f"[bold cyan]{m[:n]}[/bold cyan][dim]{m[n:]}[/dim]"
            )
            self.add_option(Option(label, id=m))
        self.highlighted = 0
        self.display = True

    def pick_highlighted(self) -> str | None:
        if not self.display or self.highlighted is None:
            return None
        val = str(self.get_option_at_index(self.highlighted).id)
        inp = self.app.query_one("#cmd-input", Input)
        inp.value = val
        inp.cursor_position = len(val)
        self.display = False
        inp.focus()
        return val

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        val = str(event.option.id)
        inp = self.app.query_one("#cmd-input", Input)
        inp.value = val
        inp.cursor_position = len(val)
        self.display = False
        inp.focus()


# ─── Haupt-App ────────────────────────────────────────────────────────────────

class FinanzApp(App):
    CSS = """
    Screen { background: #0d0d0d; }

    #main-row {
        height: 1fr;
        margin: 0 1;
    }

    #sidebar {
        width: 16;
        border: round #2a2a2a;
        align: center middle;
        padding: 0;
    }

    #right {
        width: 1fr;
        margin-left: 1;
    }

    Tabs { height: 3; }
    Tab { color: #666; }
    Tab.-active { color: #fa7ff6; }

    #content-area {
        height: 1fr;
        border: round #2a2a2a;
    }
    BalanceView, PlaceholderView, LogView { height: 1fr; padding: 1 2; }
    HistoryView { height: 1fr; }

    #input-area  { height: auto; margin: 0 1; }
    #cmd-input   { border: round cyan; }
    #statusbar   { height: 1; background: #111; color: #444; padding: 0 2; }
    #completer   {
        display: none;
        height: auto;
        max-height: 8;
        border: round #333;
        background: #0d0d1a;
    }
    #completer > .option-list--option             { padding: 0 2; }
    #completer > .option-list--option-highlighted { background: #1a1a3a; }
    """

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-row"):
            yield BigFrog(id="sidebar")
            with Vertical(id="right"):
                yield Tabs(*[Tab(label, id=tid) for tid, label in TABS])
                with ContentSwitcher(id="content-area", initial="balance"):
                    yield BalanceView(id="balance")
                    yield HistoryView(id="history")
                    yield PlaceholderView(id="importer")
                    yield PlaceholderView(id="evaluation")
                    yield PlaceholderView(id="debts")
                    yield PlaceholderView(id="categories")
                    yield PlaceholderView(id="budget")
                    yield LogView(id="log")
        with Vertical(id="input-area"):
            yield CommandCompleter(id="completer")
            yield Input(placeholder="Befehl eingeben  (Tab = Menü)", id="cmd-input")
        yield Static(id="statusbar")

    def on_mount(self) -> None:
        self.title = "Finanz-App"
        self._active_tab = "balance"
        self.query_one("#cmd-input", Input).focus()
        self.query_one("#statusbar", Static).update(
            Text.from_markup(
                "  [dim]←/→[/dim] Tab wechseln  "
                "[dim]Tab[/dim] Menü öffnen  "
                "[dim]Enter[/dim] Bestätigen  "
                "[dim]Esc[/dim] Schließen"
            )
        )

    # ── Tab-Wechsel ──────────────────────────────────────────────────────────

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab is None:
            return
        tab_id = event.tab.id
        self._active_tab = tab_id
        switcher = self.query_one("#content-area", ContentSwitcher)

        if tab_id == "balance":
            self.query_one(BalanceView).refresh_data()
            switcher.current = "balance"
        elif tab_id == "history":
            self.query_one(HistoryView).refresh_data()
            switcher.current = "history"
        elif tab_id in ("importer", "evaluation", "debts", "categories", "budget"):
            switcher.current = tab_id
            self.query_one(f"#{tab_id}", PlaceholderView).set_tab(tab_id.capitalize())

        # Completer aktualisieren falls offen
        completer = self.query_one("#completer", CommandCompleter)
        if completer.display:
            inp = self.query_one("#cmd-input", Input)
            completer.show_for(inp.value, TAB_COMMANDS.get(tab_id, []))

    # ── Tastatur ─────────────────────────────────────────────────────────────

    def on_key(self, event) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        inp = self.query_one("#cmd-input", Input)

        if event.key == "tab" and self.focused == inp:
            event.prevent_default()
            event.stop()
            if completer.display:
                count = completer.option_count
                completer.highlighted = ((completer.highlighted or 0) + 1) % count
            else:
                completer.show_for(inp.value, TAB_COMMANDS.get(self._active_tab, []))
            return

        if event.key == "backspace" and completer.display and inp.value == "":
            completer.display = False
            event.stop()
            return

        if not completer.display:
            return

        if event.key == "enter":
            val = completer.pick_highlighted()
            if val:
                event.stop()
                self._execute(val)
        elif event.key == "escape":
            completer.display = False
            inp.focus()
            event.stop()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "cmd-input":
            return
        completer = self.query_one("#completer", CommandCompleter)
        if completer.display:
            completer.show_for(event.value, TAB_COMMANDS.get(self._active_tab, []))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        if completer.display:
            val = completer.pick_highlighted()
            if val:
                event.input.clear()
                self._execute(val)
            return
        cmd = event.value.strip().lower()
        event.input.clear()
        if cmd:
            self._execute(cmd)

    # ── Befehls-Handler ──────────────────────────────────────────────────────

    def _execute(self, cmd: str) -> None:
        log = self.query_one("#log", LogView)
        tabs = self.query_one(Tabs)

        if cmd == "exit":
            self.exit()
            return

        if cmd == "back":
            tabs.active = "balance"
            return

        if cmd == "refresh" and self._active_tab == "history":
            self.query_one(HistoryView).refresh_data()
            log.add("[green]✓ History aktualisiert.[/green]")
            return

        if cmd == "import" and self._active_tab == "importer":
            try:
                from import_csv import main_import
                main_import()
                log.add("[green]✓ Import abgeschlossen.[/green]")
            except Exception as e:
                log.add(f"[red]Import-Fehler:[/red] {e}")
            self.query_one("#content-area", ContentSwitcher).current = "log"
            return

        # Tab-Shortcuts als Befehl
        tab_map = {t: t for t, _ in TABS}
        if cmd in tab_map:
            tabs.active = cmd
            return

        log.add(f"[dim]→ {cmd}[/dim]")
        self.query_one("#content-area", ContentSwitcher).current = "log"


if __name__ == "__main__":
    FinanzApp().run()
