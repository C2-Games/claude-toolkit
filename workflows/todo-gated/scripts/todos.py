"""Command-line tool for reading and mutating .claude/todos.json.

This is the only sanctioned way to modify todos.json (a PreToolUse
hook blocks direct Edit/Write calls against that file). All mutating
subcommands read the whole file, apply one change, and write it back
atomically.

todos.json is the tracked backlog and travels with the repo. The
active session -- which todo(s) and branch a /start-todo run opened
the edit gate for -- lives separately in .claude/.current-todo, which
is gitignored runtime state. start-session writes it; end-session
removes it.
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import TypedDict

VALID_STATUSES = ("backlog", "in_progress", "completed")

TODOS_PATH = Path(__file__).resolve().parents[1] / "todos.json"
CURRENT_TODO_PATH = TODOS_PATH.parent / ".current-todo"


class Subtask(TypedDict):
    id: str
    header: str
    status: str
    completed: str | None


class Todo(TypedDict):
    id: int
    header: str
    description: str
    status: str
    created: str
    completed: str | None
    plan: str | None
    subtasks: list[Subtask]


class CurrentTodo(TypedDict):
    todos: list[int]
    branch: str
    recorded: str
    started: str


class TodosFile(TypedDict):
    next_id: int
    todos: list[Todo]


def load_todos(path: Path) -> TodosFile:
    """Load and parse todos.json from disk."""
    with open(path, encoding="utf-8") as handle:
        data: TodosFile = json.load(handle)

    return data


def save_todos(path: Path, data: TodosFile) -> None:
    """Atomically write todos.json, replacing any prior contents."""
    directory = path.parent
    fd, tmp_name = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except OSError:
        os.remove(tmp_name)
        raise


def find_todo(data: TodosFile, id_str: str) -> tuple[Todo, Subtask | None]:
    """Resolve an id like "3" or "3.1" to its todo and optional subtask."""
    parts = id_str.split(".")
    todo_id = int(parts[0])
    todo = next((t for t in data["todos"] if t["id"] == todo_id), None)
    if todo is None:
        raise ValueError(f"no todo with id {todo_id}.")

    if len(parts) == 1:
        return todo, None

    subtask = next((s for s in todo["subtasks"] if s["id"] == id_str), None)
    if subtask is None:
        raise ValueError(f"no subtask with id {id_str}.")

    return todo, subtask


def today() -> str:
    """Return today's date as an iso-formatted string."""
    return datetime.now().strftime("%Y-%m-%d")


def load_current_todo() -> CurrentTodo | None:
    """Read .claude/.current-todo, or None if no session is active."""
    try:
        with open(CURRENT_TODO_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def parse_top_level_ids(raw: str) -> list[int]:
    """Split a comma-joined id list, rejecting subtask ids like '3.1'."""
    ids: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            raise ValueError(
                f"start-session takes top-level todo ids only, got {part!r}."
            )
        ids.append(int(part))
    return ids


def cmd_add(args: argparse.Namespace) -> None:
    data = load_todos(TODOS_PATH)
    todo_id = data["next_id"]
    subtasks: list[Subtask] = [
        {
            "id": f"{todo_id}.{i}",
            "header": header,
            "status": "backlog",
            "completed": None,
        }
        for i, header in enumerate(args.subtask, start=1)
    ]
    todo: Todo = {
        "id": todo_id,
        "header": args.header,
        "description": args.description,
        "status": "backlog",
        "created": datetime.now().isoformat(timespec="seconds"),
        "completed": None,
        "plan": None,
        "subtasks": subtasks,
    }
    data["todos"].append(todo)
    data["next_id"] = todo_id + 1
    save_todos(TODOS_PATH, data)
    print(f"created todo {todo_id}: {args.header}")


def cmd_update_status(args: argparse.Namespace) -> None:
    if args.status not in VALID_STATUSES:
        raise ValueError(
            f"status must be one of {VALID_STATUSES}, got {args.status!r}."
        )

    data = load_todos(TODOS_PATH)
    todo, subtask = find_todo(data, args.id)
    target: Todo | Subtask = subtask if subtask is not None else todo
    target["status"] = args.status
    target["completed"] = today() if args.status == "completed" else None
    save_todos(TODOS_PATH, data)
    print(f"todo {args.id} set to {args.status}")


def cmd_set_plan(args: argparse.Namespace) -> None:
    data = load_todos(TODOS_PATH)
    todo, _ = find_todo(data, args.id)
    todo["plan"] = args.text
    save_todos(TODOS_PATH, data)
    print(f"plan set for todo {args.id}")


def cmd_start_session(args: argparse.Namespace) -> None:
    if load_current_todo() is not None:
        raise ValueError(
            "a session is already active (.claude/.current-todo exists). "
            "Run end-session first, or delete the file if it is stale."
        )

    todo_ids = parse_top_level_ids(args.ids)
    data = load_todos(TODOS_PATH)
    for todo_id in todo_ids:
        todo, _ = find_todo(data, str(todo_id))
        todo["status"] = "in_progress"
    save_todos(TODOS_PATH, data)

    record: CurrentTodo = {
        "todos": todo_ids,
        "branch": args.branch,
        "recorded": today(),
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    with open(CURRENT_TODO_PATH, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(f"session started for {todo_ids} on branch {args.branch}")


def cmd_end_session(args: argparse.Namespace) -> None:
    session = load_current_todo()
    if session is None:
        raise ValueError("no active session to end (.claude/.current-todo absent).")

    data = load_todos(TODOS_PATH)
    completed_date = today()
    for todo_id in session["todos"]:
        todo, _ = find_todo(data, str(todo_id))
        todo["status"] = "completed"
        todo["completed"] = completed_date
        for subtask in todo["subtasks"]:
            if subtask["status"] != "completed":
                subtask["status"] = "completed"
                subtask["completed"] = completed_date

    save_todos(TODOS_PATH, data)
    os.remove(CURRENT_TODO_PATH)
    print(f"session ended, completed {session['todos']}")


def format_subtask(subtask: Subtask) -> str:
    """Render a single subtask as an indented status line."""
    return f"    [{subtask['status']}] {subtask['id']}: {subtask['header']}"


def cmd_list(args: argparse.Namespace) -> None:
    data = load_todos(TODOS_PATH)
    statuses = (args.status,) if args.status else ("backlog", "in_progress")
    todos = [t for t in data["todos"] if t["status"] in statuses]

    if args.json:
        print(json.dumps(todos, indent=2))

        return

    if not todos:
        print("no matching todos.")

        return

    for todo in todos:
        print(f"[{todo['status']}] {todo['id']}: {todo['header']}")
        for subtask in todo["subtasks"]:
            print(format_subtask(subtask))


def validate_schema(data: TodosFile) -> list[str]:
    """Return a list of schema violations found in the loaded data."""
    errors: list[str] = []
    if not isinstance(data.get("next_id"), int):
        errors.append("next_id must be an int.")

    seen_ids: set[int] = set()
    for todo in data.get("todos", []):
        todo_id = todo.get("id")
        if not isinstance(todo_id, int):
            errors.append(f"todo id {todo_id!r} is not an int.")
            continue

        if todo_id in seen_ids:
            errors.append(f"duplicate todo id {todo_id}.")
        seen_ids.add(todo_id)

        if todo.get("status") not in VALID_STATUSES:
            errors.append(f"todo {todo_id} has invalid status.")

        for subtask in todo.get("subtasks", []):
            if subtask.get("status") not in VALID_STATUSES:
                errors.append(
                    f"subtask {subtask.get('id')} has invalid status."
                )

    session = load_current_todo()
    if session is not None:
        for todo_id in session.get("todos", []):
            if todo_id not in seen_ids:
                errors.append(
                    f".current-todo references unknown todo {todo_id}."
                )

    return errors


def cmd_validate(args: argparse.Namespace) -> None:
    data = load_todos(TODOS_PATH)
    errors = validate_schema(data)
    if errors:
        for error in errors:
            print(f"invalid: {error}", file=sys.stderr)
        sys.exit(1)

    print("todos.json is valid.")


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser covering every todos.py subcommand."""
    parser = argparse.ArgumentParser(prog="todos.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--header", required=True)
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument("--subtask", action="append", default=[])
    add_parser.set_defaults(func=cmd_add)

    status_parser = subparsers.add_parser("update-status")
    status_parser.add_argument("id")
    status_parser.add_argument("status")
    status_parser.set_defaults(func=cmd_update_status)

    plan_parser = subparsers.add_parser("set-plan")
    plan_parser.add_argument("id")
    plan_parser.add_argument("text")
    plan_parser.set_defaults(func=cmd_set_plan)

    start_parser = subparsers.add_parser("start-session")
    start_parser.add_argument("ids")
    start_parser.add_argument("branch")
    start_parser.set_defaults(func=cmd_start_session)

    end_parser = subparsers.add_parser("end-session")
    end_parser.set_defaults(func=cmd_end_session)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--status", choices=VALID_STATUSES)
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and dispatch to the matching subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
