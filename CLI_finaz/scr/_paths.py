import sys
from pathlib import Path

# When frozen by PyInstaller (--onefile), __file__ points into the temp
# extraction dir. User data (db, json) must live next to the executable.
if getattr(sys, 'frozen', False):
    PROJEKT_DIR = Path(sys.executable).parent
else:
    PROJEKT_DIR = Path(__file__).parent.parent
