from ui_toolkit import *
from ui_styles import FinanzApp
from startup_check import startup_check

if __name__ == "__main__":
    startup_check()
    FinanzApp().run()
