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
                start_ui.draw_exit_panel()
            
            
            elif user_input == "help":
                print("no help for you")

            elif user_input == "start":
                start_ui.play_loading("Load bank balance ...")
                start_balance_overview()
                start_ui.draw_welcom_panel(1)
                
        
        
   
            elif user_input == "":
                continue
            else: 
                console.print(f"[red]Unknown command:[/red] {user_input}")

        # Fängt Strg+C ab
        except KeyboardInterrupt: 
            start_ui.draw_exit_panel()

        # Fängt Strg+D ab
        except EOFError: 
            start_ui.draw_exit_panel()
            


def start_balance_overview():
  
    start_ui = UI()

    
    command = ["budget","categories","debts","importer", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)




    def draw_balance_overview():
        start_ui = UI()
        start_ui.draw_menu_panel("balance_overview")


    draw_balance_overview()


    while True:
        try:
            user_input = prompt(
                "balance_overview -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                start_ui.draw_exit_panel()
            elif user_input == "back":
                return
                

            elif user_input == "help":
                print("no help for you")





            elif user_input == "categories":
                
                start_ui.play_loading("Load categories" )
                start_categories()
                draw_balance_overview()

            elif user_input == "debts":
                
                start_ui.play_loading("Load debts" )
                start_debts()
                draw_balance_overview()
            
            elif user_input == "importer":
                
                start_ui.play_loading("Load importer" )
                start_importer()
                draw_balance_overview()
            
            elif user_input == "budget":

                start_ui.play_loading("Load budget" )
                start_budget()
                draw_balance_overview()




            elif user_input == "":
                continue
            else: 
                console.print(f"[red]Unknown command:[/red] {user_input}")

        # Fängt Strg+C ab
        except KeyboardInterrupt: 
            start_ui.draw_exit_panel()
            
        # Fängt Strg+D ab
        except EOFError: 
            start_ui.draw_exit_panel()
            



def start_budget():
    
    start_ui = UI()
    start_ui.draw_menu_panel("budget")
    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "categories -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                start_ui.draw_exit_panel()
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
            start_ui.draw_exit_panel()
        # Fängt Strg+D ab
        except EOFError: 
            start_ui.draw_exit_panel()




def start_categories():
    
    start_ui = UI()
    start_ui.draw_menu_panel("budget")

    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "categories -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                start_ui.draw_exit_panel()
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
            start_ui.draw_exit_panel()
        # Fängt Strg+D ab
        except EOFError: 
            start_ui.draw_exit_panel()











def start_debts():
    
    start_ui = UI()
    start_ui.draw_menu_panel("debts")

    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "debts -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                start_ui.draw_exit_panel()
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
            start_ui.draw_exit_panel()
        # Fängt Strg+D ab
        except EOFError: 
            start_ui.draw_exit_panel()






def start_importer():
    
    start_ui = UI()
    start_ui.draw_menu_panel("importer")

    
    command = ["start", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)

    while True:
        try:
            user_input = prompt(
                "importer -- enter command: ", 
                completer=command_completer
            ).strip().lower()

            if user_input == "exit":
                start_ui.draw_exit_panel()
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
            start_ui.draw_exit_panel()
        # Fängt Strg+D ab
        except EOFError: 
            start_ui.draw_exit_panel()





if __name__ == "__main__":
    start_app()