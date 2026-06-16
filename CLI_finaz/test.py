"""
Textual Demo — Animationen + Input + Auswahl-Completer
"""

import math
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal
from textual.binding import Binding


BEFEHLE = ["addieren", "hilfe", "status", "beenden", "einstellungen", "konto", "budget"]


# ─── Pulsierender Titel ───────────────────────────────────────────────────────

class PulseTitle(Static):
    def on_mount(self) -> None:
        self._frame = 0
        self.set_interval(0.07, self._tick)

    def _tick(self) -> None:
        self._frame += 1
        t = self._frame * 0.07
        r = int(127 + 127 * math.sin(t * 2))
        g = int(127 + 127 * math.sin(t * 2 + 2))
        b = int(127 + 127 * math.sin(t * 2 + 4))
        self.update(Text.from_markup(
            f"[bold rgb({r},{g},{b})]● get-your-stuff-together ●[/bold rgb({r},{g},{b})]"
        ))


# ─── Rotierender 3D Würfel ────────────────────────────────────────────────────

class Cube3D(Static):
    VERTICES = [
        (-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
        (-1,-1, 1),(1,-1, 1),(1,1, 1),(-1,1, 1),
    ]
    EDGES = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7),
    ]

    def on_mount(self) -> None:
        self._frame = 0
        self.set_interval(0.05, self._tick)

    @staticmethod
    def _rotate(x, y, z, ax, ay, az):
        y, z = y*math.cos(ax)-z*math.sin(ax), y*math.sin(ax)+z*math.cos(ax)
        x, z = x*math.cos(ay)+z*math.sin(ay), -x*math.sin(ay)+z*math.cos(ay)
        x, y = x*math.cos(az)-y*math.sin(az), x*math.sin(az)+y*math.cos(az)
        return x, y, z

    def _tick(self) -> None:
        self._frame += 1
        t = self._frame * 0.05
        W, H = 38, 16
        grid = [[" "] * W for _ in range(H)]
        rotated = [self._rotate(x,y,z, t*0.7, t*1.1, t*0.4) for x,y,z in self.VERTICES]

        def proj(x, y, z):
            f = 180 / (5 + z)
            return int(x*f)+W//2, int(y*f*0.5)+H//2

        projected = [proj(*v) for v in rotated]
        chars = "·░▒▓"
        for a, b in self.EDGES:
            x0,y0 = projected[a]; x1,y1 = projected[b]
            steps = max(abs(x1-x0), abs(y1-y0), 1)
            for i in range(steps+1):
                px = x0 + int((x1-x0)*i/steps)
                py = y0 + int((y1-y0)*i/steps)
                if 0 <= px < W and 0 <= py < H:
                    ci = min(3, max(0, int((rotated[a][2]+1.5)*1.2)))
                    grid[py][px] = chars[ci]
        for px,py in projected:
            if 0 <= px < W and 0 <= py < H:
                grid[py][px] = "◆"

        r = int(80 + 175*abs(math.sin(t*0.8)))
        g = int(80 + 175*abs(math.sin(t*0.8+2)))
        b = int(40 + 100*abs(math.sin(t*0.8+4)))
        lines = "\n".join("".join(row) for row in grid)
        self.update(Text.from_markup(f"[rgb({r},{g},{b})]{lines}[/rgb({r},{g},{b})]"))


# ─── Output Log ──────────────────────────────────────────────────────────────

class OutputLog(Static):
    def on_mount(self) -> None:
        self._lines: list[str] = ["[dim]Tippe einen Befehl unten...[/dim]"]
        self._refresh()

    def add(self, line: str) -> None:
        self._lines.append(line)
        if len(self._lines) > 8:
            self._lines = self._lines[-8:]
        self._refresh()

    def _refresh(self) -> None:
        self.update(Text.from_markup("\n".join(self._lines)))


# ─── Autocomplete Dropdown ────────────────────────────────────────────────────

class CommandCompleter(OptionList):
    """Dropdown das bei Eingabe erscheint und mit Tab/Pfeiltasten navigierbar ist."""

    BINDINGS = [
        Binding("escape", "close", "Schließen"),
    ]

    def action_close(self) -> None:
        self.display = False
        self.app.query_one("#cmd-input", Input).focus()

    def filter(self, query: str) -> None:
        self.clear_options()
        matches = [b for b in BEFEHLE if b.startswith(query.lower())] if query else BEFEHLE
        if not matches:
            self.display = False
            return
        for m in matches:
            # Tippe Teil cyan, Rest grau
            typed_len = len(query)
            label = Text.from_markup(
                f"[bold cyan]{m[:typed_len]}[/bold cyan][dim]{m[typed_len:]}[/dim]"
            )
            self.add_option(Option(label, id=m))
        self.display = True
        self.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._pick(str(event.option.id))

    def pick_highlighted(self) -> bool:
        """Übernimmt den aktuell markierten Eintrag. Gibt True zurück wenn erfolgreich."""
        if not self.display:
            return False
        highlighted = self.highlighted
        if highlighted is None:
            return False
        option = self.get_option_at_index(highlighted)
        self._pick(str(option.id))
        return True

    def _pick(self, value: str) -> None:
        inp = self.app.query_one("#cmd-input", Input)
        inp.value = value
        inp.cursor_position = len(value)
        self.display = False
        inp.focus()


# ─── Haupt-App ────────────────────────────────────────────────────────────────

class DemoApp(App):
    CSS = """
    Screen { background: #0d0d0d; }

    #title {
        height: 3;
        content-align: center middle;
        border: round #333;
        margin: 0 1;
    }
    #main-row { height: 1fr; margin: 0 1; }
    #cube-panel {
        width: 42;
        border: round #444;
        padding: 0 1;
        content-align: center middle;
    }
    #right-panel {
        width: 1fr;
        border: round #444;
        margin-left: 1;
        padding: 1 2;
    }
    #output { height: 1fr; }

    #input-area { height: auto; }
    #cmd-input { border: round cyan; }

    #completer {
        display: none;
        height: auto;
        max-height: 6;
        border: round #555;
        background: #1a1a2e;
        margin-top: 0;
        padding: 0;
    }
    #completer > .option-list--option {
        padding: 0 1;
    }
    #completer > .option-list--option-highlighted {
        background: #16213e;
    }
    """

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield PulseTitle(id="title")
        with Horizontal(id="main-row"):
            yield Cube3D(id="cube-panel")
            with Vertical(id="right-panel"):
                yield OutputLog(id="output")
                with Vertical(id="input-area"):
                    yield Input(placeholder="Befehl eingeben...", id="cmd-input")
                    yield CommandCompleter(id="completer")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "GYSO — Finaz"
        self.sub_title = "Textual Demo"
        self.query_one("#cmd-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "cmd-input":
            self.query_one("#completer", CommandCompleter).filter(event.value)

    def on_input_focus(self, event: Input.Focus) -> None:
        # Dropdown beim Fokus NICHT automatisch öffnen — nur per Tab
        pass

    def action_complete_or_next(self) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        inp = self.query_one("#cmd-input", Input)
        if completer.display:
            # Tab im offenen Dropdown → nächster Eintrag
            count = completer.option_count
            current = completer.highlighted or 0
            completer.highlighted = (current + 1) % count
        else:
            # Tab → Dropdown öffnen (immer, auch leer)
            completer.filter(inp.value)

    def action_close_completer(self) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        completer.display = False

    def on_key(self, event) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        inp = self.query_one("#cmd-input", Input)

        # Tab abfangen bevor Textual Fokus wechselt
        if event.key == "tab" and self.focused == inp:
            event.prevent_default()
            event.stop()
            self.action_complete_or_next()
            return

        # Backspace bei leerem Eingabefeld → Dropdown schließen
        if event.key == "backspace" and completer.display and inp.value == "":
            completer.display = False
            event.stop()
            return

        if not completer.display:
            return

        if event.key == "enter":
            if completer.pick_highlighted():
                event.stop()
        elif event.key == "escape":
            completer.display = False
            inp.focus()
            event.stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        # Wenn Dropdown offen war und Enter gedrückt → bereits durch on_key behandelt
        if completer.display:
            completer.pick_highlighted()
            return

        log = self.query_one("#output", OutputLog)
        cmd = event.value.strip().lower()
        event.input.clear()
        completer.display = False
        if not cmd:
            return

        log.add(f"[cyan]>[/cyan] {cmd}")
        if cmd == "beenden":
            self.exit()
        elif cmd == "hilfe":
            log.add(f"[yellow]Befehle:[/yellow] {', '.join(BEFEHLE)}")
        elif cmd == "status":
            log.add("[green]System läuft. Alles OK.[/green]")
        elif cmd == "budget":
            log.add("[magenta]Budget-Modul geladen.[/magenta]")
        elif cmd == "konto":
            log.add("[blue]Konto-Übersicht geladen.[/blue]")
        elif cmd == "einstellungen":
            log.add("[yellow]Einstellungen geöffnet.[/yellow]")
        elif " " in cmd:
            parts = cmd.split()
            if len(parts) == 2:
                try:
                    res = float(parts[0]) + float(parts[1])
                    log.add(f"[green]Ergebnis:[/green] {res:g}")
                except ValueError:
                    log.add("[red]Keine Zahlen.[/red]")
            else:
                log.add(f"[red]Unbekannt:[/red] {cmd}")
        else:
            log.add(f"[red]Unbekannt:[/red] {cmd}")


if __name__ == "__main__":
    DemoApp().run()
