from rich import box 
from rich.console import Console 
from rich.panel import Panel 
from rich.table import Table 

from netpulse.system import collect, format_bytes, format_uptime 

console = Console()

def render() -> None:
    data = collect()
    memory_used = data["memory_total"] - data["memory_available"]
    disk_used = data["disk_total"] - data["disk_free"]
    memory_pct = 100 * memory_used / max(1, data["memory_total"])
    disk_pct = 100 * disk_used / max(1, data["disk_total"])

    console.print(
        Panel(
            "[bold bright_cyan]NETPULSE[/] [magenta]// SYSTEM INTELLIGENCE[/]\n"
            "[dim]LIVE LOCAL TELEMETRY · NETWORK DIAGNOSTICS[/]",
            border_style="bright_cyan",
            box=box.DOUBLE,
        )
    )

    table = Table(box=box.ROUNDED, expand=True)
    table.add_column("METRIC", style="bright_cyan")
    table.add_column("VALUE", justify="right", style="bright_white")
    table.add_column("DETAIL", style="magenta")

    table.add_row(
        "CPU load average",
        f"{data['load_1m']:.2f}",
        f"5m {data['load_5m']:.2f} / 15m {data['load_15m']:.2f}",
    )
    table.add_row(
        "Memory",
        format_bytes(memory_used),
        f"{memory_pct:.1f}% of {format_bytes(data['memory_total'])}",
    )
    table.add_row(
        "Root filesystem",
        format_bytes(disk_used),
        f"{disk_pct:.1f}% of {format_bytes(data['disk_total'])}",
    )
    table.add_row("Uptime", format_uptime(data["uptime_seconds"]), "Since boot")

    console.print(table)
    console.print(
        Panel(
            "[bright_green]SYSTEM CORE ONLINE[/]  "
            "[bright_cyan]NETWORK PROBES READY[/]",
            border_style="magenta",
        )
    )
