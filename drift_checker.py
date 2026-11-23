from pathlib import Path

GOLDEN_FILE = Path("golden_config.cfg")
RUNNING_FILE = Path("r1_running_config.cfg")

# Parses unnecessary lines and removes characters
def load_clean_lines(path:Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    clean = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("!"):
            continue
        if stripped.startswith("Current configuration"):
            continue
        clean.append(line)

    return clean


def main() -> None:
    golden_lines = load_clean_lines(GOLDEN_FILE)
    running_lines = load_clean_lines(RUNNING_FILE)

    # Get added lines that were added to the "running-config"
    added = [
        line
        for line in running_lines
        if line not in golden_lines
    ]

    removed = [
        line
        for line in golden_lines
        if line not in running_lines
    ]

    if not added and not removed:
        print("OK: No changes")
        return

    if removed:
        print("UPDATE: Changes were modified")
        for line in removed:
            print(f"REMOVED: -{line}")

    if added:
        print("UPDATE: Changes were modified")
        for line in added:
            print(f"ADDED: -{line}")

if __name__ == "__main__":
    main()