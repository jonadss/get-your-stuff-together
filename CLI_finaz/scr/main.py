#Import von ui_toolkit 
from ui_toolkit import *

#Import von ui_styles.py
from ui_styles import UI

from request import overview, start_saldo_request, DB_PFAD
import sqlite3


def start_balance_overview():
    
    start_ui = UI()
    #help func
    def draw_balance_overview():
        start_ui = UI()
        
        new_saldo = start_saldo_request()
        start_ui.draw_balance_overview_panel(saldo=new_saldo)
    
    command = ["show history","importer","categories","debts","budget","evaluation", "help", "exit", "back"]
    command_completer = WordCompleter(command, ignore_case=True)



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
                console.print("\n[bold cyan]Available commands:[/bold cyan]")
                console.print("  [green]show history[/green]  – show all imported transactions")
                console.print("  [green]importer[/green]      – import CSV files into the database")
                console.print("  [green]categories[/green]    – manage transaction categories")
                console.print("  [green]debts[/green]         – manage debts and credits")
                console.print("  [green]budget[/green]        – manage monthly budgets")
                console.print("  [green]evaluation[/green]    – show spending evaluations and charts")
                console.print("  [green]back[/green]          – go back")
                console.print("  [green]exit[/green]          – quit the program\n")





            elif user_input == "categories":
                start_ui.play_loading("Load categories")
                from categories import manage_categories
                manage_categories()
                draw_balance_overview()


            elif user_input == "show history":
                start_ui.play_loading("Load history...")
                try:
                    rows = overview(sqlite3.connect(DB_PFAD))
                except sqlite3.OperationalError:
                    print("ERROR: Table not found – please import data first.")
                else:
                    start_ui.draw_overview_table(rows)
                  


            elif user_input == "debts":
                start_ui.play_loading("Load debts")
                from debts import manage_debts
                manage_debts()
                draw_balance_overview()
            
            elif user_input == "importer":
                
                start_ui.play_loading("Load importer" )
                start_importer()
                draw_balance_overview()
            
            elif user_input == "budget":
                start_ui.play_loading("Load budget")
                from budget import manage_budget
                manage_budget()
                draw_balance_overview()


            elif user_input == "evaluation":
                start_ui.play_loading("Load evaluation")
                from evaluation import manage_evaluation
                manage_evaluation()
                draw_balance_overview()




            elif user_input == "":
                continue
            else: 
                console.print(f"[red]Unknown command:[/red] {user_input}")

        # Fängt Strg+C ab
        except KeyboardInterrupt,EOFError: 
            start_ui.draw_exit_panel()



def start_importer():
    
    start_ui = UI()
    start_ui.draw_importer_panel("importer")

    
    command = ["choose path", "import", "undo import", "delete csv", "delete db", "help", "exit", "back"]
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
                console.print("\n[bold cyan]Available commands:[/bold cyan]")
                console.print("  [green]choose path[/green]  – set the path to a CSV file")
                console.print("  [green]import[/green]       – import the selected CSV into the database")
                console.print("  [green]undo import[/green]  – revert the last import")
                console.print("  [green]delete csv[/green]   – remove the selected CSV file from the database")
                console.print("  [green]delete db[/green]    – clear the entire database")
                console.print("  [green]back[/green]         – go back")
                console.print("  [green]exit[/green]         – quit the program\n")

            elif user_input == "choose path":
                from import_csv import user_interaktion
                new_path = user_interaktion()
                start_ui.draw_importer_panel("importer",new_path)
                

            elif user_input == "import":
                from import_csv import main_import
                main_import()
            elif user_input == "delete db":
                from import_csv import clear_database
                clear_database()

            
            elif user_input == "undo import":
                from import_csv import undo_last_import
                undo_last_import()

            elif user_input == "delete csv":
                from import_csv import delete_csv_from_db
                delete_csv_from_db()




            elif user_input == "":
                continue
            else: 
                console.print(f"[red]Unknown command:[/red] {user_input}")

        # Fängt Strg+C ab
        except KeyboardInterrupt,EOFError: 
            #start_ui.draw_exit_panel()
            return



from startup_check import startup_check
if __name__ == "__main__":
    startup_check()
    
    start_ui = UI()
    start_ui.draw_welcom_panel(4)
    
    start_balance_overview()