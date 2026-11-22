import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run(script_name: str) -> None:
    script_path = BASE_DIR / script_name
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        raise SystemExit(f"ERROR: {script_name} - EXIT CODE: {result.returncode}")

def main() -> None:
    run("get_config.py")
    run("drift_checker.py")

if __name__ == "__main__":
    main()