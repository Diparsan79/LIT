from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
import storage


console = Console()

def clear_and_header(title_text):
    console.clear()
    header= Text()
    header.append("LIT", style="bold red")
    header.append(f" | {title_text}", style="dim white")
    console.print(Panel(header, border_style="dim red", padding=(0,2)))
    console.print()

def prompt(label,optional=False):
# its a input prompt lol
    tag= " [dim](optional)[/dim]" if optional else ""
    console.print(f" [bold red],[/bold red] {label}{tag}")
    value=input("      ").strip
    return value

def prompt_rating():
    while True:
        console.print(" [bold red],[/bold red] Rating [dim](1-10, or skip[/dim]")
        value=input("     ").strip()

        if value == "": # if input is empty then js dont add thats it hah
            return None
        
        if value.isdigit():
            rating= int(value)
            if 1<= rating <=10:
                return rating
            
        console.print(" [dim red] Please enter a number between 1 and 10, or press Enter or skip.[/dim red]")
        console.print()

