from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def main():
    title = Text()
    title.append("L", style="bold red")
    title.append("I", style="bold white")
    title.append("T", style="bold red")
    title.append(" - Letterboxd in Terminal", style="dim white")


    console.print(Panel(title, border_style="red", padding=(1,4)))
    console.print("\n[dim]v0.1.0  | Local-first movie diary[/dim]\n")


if __name__ =="__main__":
    main()