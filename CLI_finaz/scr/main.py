from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

console = Console()

def start_app():
    console.print(Panel.fit(
        "[#ff4d4d]Mein CLI Interface[/#ff4d4d]", 
        title= "MCI-App",
        subtitle="v1.0"))
    
    # Hier definieren wir die Wörter für die Vervollständigung
    befehle = ["addieren", "hilfe", "beenden", "status", "einstellungen"]
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
            




            elif user_input == "addieren":
                n1 = prompt("Erste Zahl: ")
                n2 = prompt("Zweite Zahl: ")
                try:
                    res = int(n1) + int(n2)
                    console.print(f"[green]Ergebnis:[/green] {res}")
                except ValueError:
                    console.print("[red]Fehler: Bitte nur Zahlen eingeben![/red]")
            
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