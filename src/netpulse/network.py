import json 
import os 
import subprocess 
from pathlib import Path 

def probe(host: str, port: int, timeout: float = 3.0) -> dict:
    executable = os.environ.get("NETPULSE_NET", "")
    if not executable or not Path(executable).is_file():
        raise RuntimeError("Go network probe not found. Run netpulse --build.")

    if not host or len(host) > 253:
        raise ValueError("Provide a valid host or IP address.")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")

    if not 0.1 <= timeout <= 30:
        raise ValueError("Time must be between 0.1 and 30 seconds.")

    result = subprocess.run(
        [executable, "--host", host, "--port", str(port),
         "--timeout", str(timeout)],
        capture_output=True,
        text=True,
        timeout=timeout + 5,
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Go probe returned invalid JSON.") from exc 

    if result.returncode != 0:
        raise RuntimeError(data.get("error", "Network probe failed."))

    return data 

