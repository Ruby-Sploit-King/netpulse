import json 
import os 
import subprocess 
from pathlib import Path 

def collect() -> dict:
    executable = os.environ.get("NETPULSE_CORE", "")
    if not executable or not Path(executable).is_file():
        raise RuntimeError("C++ core not found. Run netpulse --build.")

    result = subprocess.run(
        [executable, "--json"],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )
    data = json.loads(result.stdout)

    required = {"load_1m", "load_5m", "load_15m",
                "memory_total", "memory_available",
                "disk_total", "disk_free", "uptime_seconds"}

    if not required.issubset(data):
        raise RuntimeError("C++ core returned incomplete system metrics.")

    return data 

def format_bytes(value: int) -> str:
    size = float(value) 
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(size) < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}"
        size /= 1024 

def format_uptime(seconds: int) -> str:
    days, seconds = divmod(max(0, seconds), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, _ = divmod(seconds, 60)
    return f"{days}d {hours}h {minutes}m"
