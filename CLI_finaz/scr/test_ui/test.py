from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.live import Live

import time 

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

console = Console()

def start_app():
    console.print(Panel("[bold blue]Mein CLI Interface[/bold blue]", subtitle="v1.0"))
    
    # Hier definieren wir die Wörter für die Vervollständigung
    befehle = ["print", "hilfe", "beenden", "status", "einstellungen"]
    befehl_completer = WordCompleter(befehle, ignore_case=True)
    
    while True:
        try:
            # Wir nutzen prompt() von prompt_toolkit statt Prompt.ask
            # 'completer' aktiviert die Tab-Vervollständigung
            user_input = prompt(
                "Was möchtest du tun? > ", 
                completer=befehl_completer
            ).strip().lower()




            if user_input == "beenden":
                break
            




            elif user_input == "print":
                console.print(Panel.fit(
                    "Rechenvorgang läuft...", 
                    title="Status", 
                    border_style="red",
                    padding=(1, 4),
                    style="#ff91b2 on #636363",
                    ))
                
                console.print(Panel(
                    "lol",
                    title= "Dicker Rahmen für wichtige Infos.",
                    box=box.HEAVY,
                    border_style="blue",
                    width = 15,
                    padding=(1, 1)

                ))
                frames = [
                    "( o.o )",
                    "( -.- )",
                    "( o.o )",
                    "( >.< )"
                ]

                with Live(refresh_per_second=4) as live:
                    for _ in range(15): 
                        for frame in frames:
                            # Wir aktualisieren das Panel im Live-Modus
                            live.update(Panel(
                                frame, 
                                title="Bot animiert", 
                                border_style="cyan",
                                high = 4,
                                width = 4,
                                padding = (3,1)))
                            time.sleep(0.2)






                break


                














            elif user_input == "hilfe":
                console.print("[yellow]Verfügbare Befehle:[/yellow]", ", ".join(befehle))
            







            #skip
            elif user_input == "":
                continue
                
            else: 
                console.print(f"[red]Unbekannter Befehl:[/red] {user_input}")










        except KeyboardInterrupt: # Fängt Strg+C ab
            break
        except EOFError: # Fängt Strg+D ab
            break

    console.print("[bold red]Programm beendet.[/bold red]")

if __name__ == "__main__":
    start_app()