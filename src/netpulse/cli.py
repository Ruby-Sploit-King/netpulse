import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from netpulse.dashboard import render
from netpulse.network import probe
from netpulse.system import collect, format_bytes, format_uptime

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netpulse",
        description="Linux system and network intelligence dashboard",
    )
    commands = parser.add_subparsers(dest="command")

    commands.add_parser("dashboard", help="Display system dashboard")
    commands.add_parser("status", help="Print system metrics")

    network = commands.add_parser("probe", help="Test a TCP endpoint")
    network.add_argument("host")
    network.add_argument("--port", type=int, default=443)
    network.add_argument("--timeout", type=float, default=3.0)

    return parser


def show_status() -> None:
    data = collect()
    table = Table(title="NETPULSE // STATUS")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Load average", f"{data['load_1m']:.2f}, "
                   f"{data['load_5m']:.2f}, {data['load_15m']:.2f}")
    table.add_row("Memory total", format_bytes(data["memory_total"]))
    table.add_row("Memory available", format_bytes(data["memory_available"]))
    table.add_row("Disk total", format_bytes(data["disk_total"]))
    table.add_row("Disk free", format_bytes(data["disk_free"]))
    table.add_row("Uptime", format_uptime(data["uptime_seconds"]))
    console.print(table)


def show_probe(host: str, port: int, timeout: float) -> None:
    result = probe(host, port, timeout)
    table = Table(title="NETPULSE // NETWORK PROBE")
    table.add_column("FIELD", style="cyan")
    table.add_column("RESULT", style="bright_white")
    table.add_row("Host", result["host"])
    table.add_row("Port", str(result["port"]))
    table.add_row("Resolved address", result["address"])
    table.add_row("TCP connection", "[green]CONNECTED[/]")
    table.add_row("Elapsed", f"{result['elapsed_ms']:.2f} ms")
    console.print(table)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command in (None, "dashboard"):
            render()
        elif args.command == "status":
            show_status()
        elif args.command == "probe":
            show_probe(args.host, args.port, args.timeout)
        return 0
    except (RuntimeError, ValueError, OSError, KeyError) as exc:
        print(f"netpulse: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"netpulse: unexpected error: {exc}", file=sys.stderr)
        return 1
