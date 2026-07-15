import json
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT_DIR / "logs"
SRC_DIR = ROOT_DIR / "src"


def send_message(payload):
    print(json.dumps(payload), flush=True)


def list_tools():
    return [
        {
            "name": "project_status",
            "description": "Summarize the local Locus project status.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "answer_project_question",
            "description": "Answer a basic question about the local Locus project using repository files.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The question or request to answer."}
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    ]


def project_status_text():
    python_files = sorted(ROOT_DIR.rglob("*.py"))
    test_files = sorted((ROOT_DIR / "tests").glob("test_*.py")) if (ROOT_DIR / "tests").exists() else []
    log_files = sorted(LOGS_DIR.glob("*.md")) if LOGS_DIR.exists() else []
    model_path = ROOT_DIR / "data" / "data.pth"
    latest_log = log_files[-1].name if log_files else "none"
    model_state = "present" if model_path.exists() else "missing"
    return (
        f"Locus project status: {len(python_files)} Python files, "
        f"{len(test_files)} test files, model file is {model_state}, latest log is {latest_log}."
    )


def answer_project_question(arguments):
    query = " ".join(str(arguments.get("query", "")).split()).strip()
    if not query:
        return "No question was provided."

    lowered = query.lower()
    if any(keyword in lowered for keyword in ("status", "project", "repo", "repository")):
        return project_status_text()
    if "intent" in lowered:
        intents_path = SRC_DIR / "brain" / "intents.json"
        return f"Intent data lives at {intents_path.relative_to(ROOT_DIR)}."
    if "log" in lowered:
        log_files = sorted(LOGS_DIR.glob("*.md")) if LOGS_DIR.exists() else []
        latest_log = log_files[-1].name if log_files else "none"
        return f"The latest project log is {latest_log}."
    return (
        f"MCP server received your project question at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC: "
        f"{query}"
    )


def handle_call(tool_name, arguments):
    if tool_name == "project_status":
        return project_status_text()
    if tool_name == "answer_project_question":
        return answer_project_question(arguments)
    raise ValueError(f"Unknown tool: {tool_name}")


def process_message(message):
    method = message.get("method")
    request_id = message.get("id")
    params = dict(message.get("params") or {})

    if method == "initialize":
        if request_id is None:
            return
        send_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "locus-project-server", "version": "0.1.0"},
                },
            }
        )
        return

    if method == "notifications/initialized":
        return

    if method == "tools/list":
        send_message({"jsonrpc": "2.0", "id": request_id, "result": {"tools": list_tools()}})
        return

    if method == "tools/call":
        try:
            text = handle_call(str(params.get("name", "")), dict(params.get("arguments") or {}))
            send_message(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": text}], "isError": False},
                }
            )
        except Exception as exc:
            send_message(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True},
                }
            )
        return

    if request_id is not None:
        send_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        )


def main():
    while True:
        try:
            line = input()
        except EOFError:
            return
        if not line.strip():
            continue
        try:
            process_message(json.loads(line))
        except Exception as exc:
            send_message({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}})


if __name__ == "__main__":
    main()
