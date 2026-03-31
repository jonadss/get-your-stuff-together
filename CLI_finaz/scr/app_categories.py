#Import von ui_toolkit 
from ui_toolkit import *

#Import von ui_styles.py
from ui_styles import UI



def start_categories():
    
    start_ui = UI()
    start_ui.draw_header("start_categories")
    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "categories -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                break
            elif user_input == "back":
                start_app()
                break

            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.draw_header("you will be forwarded")
                co
    









            elif user_input == "":
                continue
            else: 
                console.print(f"[red]Unknown command:[/red] {user_input}")

        # Fängt Strg+C ab
        except KeyboardInterrupt: 
            break
        # Fängt Strg+D ab
        except EOFError: 
            break







if __name__ == "__main__":
    start_balance_overview()