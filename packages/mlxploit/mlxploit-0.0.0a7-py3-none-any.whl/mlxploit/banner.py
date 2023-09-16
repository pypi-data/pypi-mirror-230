from rich.console import Console
from rich.table import Table
from typing import Optional


def banner(console: Console, subtitle: str = "") -> None:
    console.print(f"""[bold cyan]
           __            _       _ _   
  /\/\    / /__  ___ __ | | ___ (_) |_ 
 /    \  / / \ \/ / '_ \| |/ _ \| | __|
/ /\/\ \/ /___>  <| |_) | | (_) | | |_ 
\/    \/\____/_/\_\ .__/|_|\___/|_|\__|
                  |_|                   [/bold cyan]
    [bold yellow]{subtitle}[/bold yellow]
""")



def options_table(
    console: Console,
    target_model: Optional[str] = None,
    dataset: Optional[str] = None,
    img: Optional[str] = None,
    device: Optional[str] = None
) -> None:
    console.print()

    table = Table(
        title=":reminder_ribbon: Options :reminder_ribbon:",
        style="bright_magenta",
        show_header=False)
    
    table.add_column(style="bright_cyan")
    table.add_column(style="bright_green")

    if target_model is not None:
        table.add_row("Target Model", f"{target_model}")
    if dataset is not None:
        table.add_section()
        table.add_row("Dataset", f"{dataset}")
    if img is not None:
        table.add_section()
        table.add_row("Image", f"{img}")
    if device is not None:
        table.add_section()
        table.add_row("Device", f"{device}")

    console.print(table)
    console.print()