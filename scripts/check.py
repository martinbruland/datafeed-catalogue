#!/usr/bin/env python3
"""The check every entry passes: the schema, the six plain fields without
the forbidden words, placeholders matching questions, and the index
listing every entry once."""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = re.compile(r"\b(JSON|URL|API|key|keys|path|paths)\b", re.I)
KINDS = {"source", "query", "item"}
CATEGORIES = {"transport", "energy", "weather", "nature", "money", "code", "fun"}
QUESTION_TYPES = {"text", "number", "choice", "location"}
PLAIN = ["name", "gives", "example", "from", "cadence", "asks"]

def fail(entry, message):
    print(f"{entry}: {message}")
    return 1

def placeholders(definition):
    text = json.dumps(definition)
    return set(re.findall(r"\{([a-z][a-z0-9.-]*)\}", text))

def check_entry(path):
    problems = 0
    try:
        entry = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        return fail(path.name, f"not JSON: {error}")
    if entry.get("id") != path.stem or not re.fullmatch(r"[a-z0-9-]+", path.stem):
        problems += fail(path.name, "id must equal the file name, lowercase with hyphens")
    if entry.get("kind") not in KINDS:
        problems += fail(path.name, "kind must be source, query, or item")
    if not isinstance(entry.get("version"), int):
        problems += fail(path.name, "version must be an integer")
    if entry.get("category") not in CATEGORIES:
        problems += fail(path.name, "category unknown")
    if entry.get("region") not in {"no", "global"}:
        problems += fail(path.name, "region must be no or global")
    plain = entry.get("plain", {})
    for field in PLAIN:
        value = plain.get(field, "")
        if not isinstance(value, str) or not value.strip():
            problems += fail(path.name, f"plain.{field} is missing")
        elif FORBIDDEN.search(value):
            problems += fail(path.name, f"plain.{field} uses a forbidden word: {value!r}")
    questions = entry.get("questions", [])
    names = set()
    for question in questions:
        if question.get("type") not in QUESTION_TYPES:
            problems += fail(path.name, f"question {question.get('name')} has an unknown type")
        for field in ("name", "label", "help"):
            if not question.get(field):
                problems += fail(path.name, f"question is missing {field}")
        if question.get("type") == "location":
            names |= {f"{question['name']}.lat", f"{question['name']}.lon"}
        else:
            names.add(question.get("name"))
    if not entry.get("attribution") or not entry.get("terms", {}).get("url") or not entry.get("terms", {}).get("checked"):
        problems += fail(path.name, "attribution and terms (url, checked) are required")
    definition = entry.get("definition", {})
    for required in ("schemaVersion", "name", "source", "extraction", "placement", "refresh"):
        if required not in definition:
            problems += fail(path.name, f"definition is missing {required}")
    used = placeholders(definition) - {"today", "today-iso"}
    if used - names:
        problems += fail(path.name, f"placeholders without a question: {sorted(used - names)}")
    if names - used:
        problems += fail(path.name, f"questions never used: {sorted(names - used)}")
    for key in definition.get("extraction", []):
        for segment in key.get("path", []):
            if isinstance(segment, dict) and set(segment) != {"where", "is"}:
                problems += fail(path.name, f"path segment {segment} must be a key, an index, or {{where, is}}")
    if entry.get("kind") == "item" and not definition.get("placement", {}).get("areas"):
        problems += fail(path.name, "an item entry needs placed areas")
    return problems

def main():
    problems = 0
    entries = sorted((ROOT / "entries").glob("*.json"))
    for path in entries:
        problems += check_entry(path)
    index = json.loads((ROOT / "index.json").read_text())
    listed = [row["id"] for row in index.get("entries", [])]
    on_disk = [path.stem for path in entries]
    if sorted(listed) != sorted(on_disk) or len(listed) != len(set(listed)):
        problems += fail("index.json", f"must list every entry exactly once; listed {len(listed)}, on disk {len(on_disk)}")
    for row in index.get("entries", []):
        entry = json.loads((ROOT / "entries" / f"{row['id']}.json").read_text()) if (ROOT / "entries" / f"{row['id']}.json").exists() else {}
        for field in ("name", "kind", "category", "region", "version"):
            expected = entry.get("plain", {}).get("name") if field == "name" else entry.get(field)
            if row.get(field) != expected:
                problems += fail("index.json", f"{row['id']}.{field} differs from the entry")
    print(f"{len(entries)} entries, {problems} problems")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
