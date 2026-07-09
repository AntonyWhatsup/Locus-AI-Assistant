import sys, json, datetime, pathlib, traceback

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]

try:
    data = json.load(sys.stdin)
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{datetime.date.today()}.md"

    text = data.get("prompt") or data.get("last_assistant_message") or ""
    label = "Q" if "prompt" in data else "A"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n## {label}\n{text}\n")
except Exception:
    debug_file = PROJECT_ROOT / "logs" / "hook_error.log"
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with open(debug_file, "a", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    sys.exit(1)
