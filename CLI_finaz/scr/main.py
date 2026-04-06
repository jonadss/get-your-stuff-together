#Import von ui_toolkit 
from ui_toolkit import *

#Import von ui_styles.py
from ui_styles import UI


def start_app():
    start_ui = UI()
    start_ui.draw_welcom_panel(2)

    command = ["start", "help", "exit"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "euer volk hungert mein lord  ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                break
            
            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.play_loading("Load bank balance ...")
                start_balance_overview()
                
        
        
        
        

        
        
        
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


def start_balance_overview():
    


    start_ui = UI()
    start_ui.draw_header("start_balance_overview")  
    
    command = ["budget","categories","debts","importer", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "balance_overview -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                sys.exit(1)
            elif user_input == "back":
                return
                

            elif user_input == "help":
                print("no help for you")





            elif user_input == "categories":
                from app_categories import start_categories
                start_ui.draw_header("you will be forwarded")
                start_categories()

            elif user_input == "debts":
                from app_debts import start_debts
                start_ui.draw_header("you will be forwarded")
                start_debts()
            
            elif user_input == "importer":
                from app_importer import start_importer
                start_ui.draw_header("you will be forwarded")
                start_importer()
            
            elif user_input == "budget":
                from app_budget import start_budget
                start_ui.draw_header("you will be forwarded")
                start_budget()




            elif user_input == "":
                continue
            else: 
                console.print(f"[red]Unknown command:[/red] {user_input}")

        # Fängt Strg+C ab
        except KeyboardInterrupt: 
            return sys.exit(0)
        # Fängt Strg+D ab
        except EOFError: 
            return sys.exit(0)

##########################################################
#####habs nichts gemacht daran#########################
###########################################################################


def start_budget():
    
    start_ui = UI()
    start_ui.draw_header("start_budget")
    
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
                return

            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.draw_header("you will be forwarded")
                
    









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
                return

            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.draw_header("you will be forwarded")
                
    









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











def start_debts():
    
    start_ui = UI()
    start_ui.draw_header("start_debts")
    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "debts -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                break
            elif user_input == "back":
                return

            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.draw_header("you will be forwarded")
                
    









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






def start_importer():
    
    start_ui = UI()
    start_ui.draw_header("start_importer")
    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "importer -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                break
            elif user_input == "back":
                return

            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.draw_header("you will be forwarded")
                









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
    start_app()