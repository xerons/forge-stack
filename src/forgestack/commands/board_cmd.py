"""forgestack board — attach AGTX UI."""

import shutil
import subprocess

from rich.console import Console


def cli() -> None:
    console = Console()
    if shutil.which("agtx"):
        subprocess.run(["agtx"], check=False)
    else:
        console.print("AGTX CLI missing. Install first per upstream docs.")
