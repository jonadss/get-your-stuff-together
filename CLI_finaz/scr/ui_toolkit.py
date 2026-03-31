
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich import box
from rich.live import Live
from rich.console import Group
from rich.styled import Styled
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


from main import start_app
from app_balance_overview import start_balance_overview
from app_categories import start_categories
from app_debts import start_debts
from app_importer import start_importer



console = Console()