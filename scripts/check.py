#!/usr/bin/env python3
"""The check every entry passes: the schema, the six plain fields without
the forbidden words, placeholders matching questions, and the index
listing every entry once."""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = re.compile(r"\b(JSON|URL|API|key|keys|path|paths)\b", re.I)
KINDS = {"source", "query", "template", "item"}
CATEGORIES = {"transport", "energy", "weather", "nature", "money", "code", "fun", "look"}
ROLES = ["first", "second", "third", "fourth"]
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
        problems += fail(path.name, "kind must be source, query, template, or item (an older name for query)")
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
    if entry.get("kind") == "template":
        return problems + check_template(path, entry)
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
    if entry.get("kind") in {"query", "item"} and not definition.get("placement", {}).get("areas"):
        problems += fail(path.name, "a query entry needs placed areas, its suggested look")
    if entry.get("kind") == "source" and (definition.get("extraction") or definition.get("placement", {}).get("areas")):
        problems += fail(path.name, "a source entry is the connection alone: no extraction, no placed areas")
    return problems

def check_template(path, entry):
    """A template is a look alone: a placement whose keys are the roles
    first to fourth, a sample value per role, and neither a source nor
    an extraction. The category is look."""
    problems = 0
    definition = entry.get("definition", {})
    if set(definition) - {"schemaVersion", "placement"}:
        problems += fail(path.name, "a template's definition holds schemaVersion and placement alone")
    if entry.get("category") != "look":
        problems += fail(path.name, "a template's category is look")
    if entry.get("questions"):
        problems += fail(path.name, "a template asks nothing")
    areas = definition.get("placement", {}).get("areas", {})
    roles = [content.get("key") for area, content in areas.items() if area != "picture"]
    if not roles or any(role not in ROLES for role in roles):
        problems += fail(path.name, f"a template's areas hold the roles {ROLES}")
    if sorted(roles, key=ROLES.index) != ROLES[: len(roles)]:
        problems += fail(path.name, "a template's roles start at first and leave no gap")
    if set(entry.get("sample", {})) != set(roles):
        problems += fail(path.name, "sample holds one value per role used")
    return problems

def main():
    problems = 0
    entries = sorted((ROOT / "entries").glob("*.json"))
    for path in entries:
        problems += check_entry(path)
    index = json.loads((ROOT / "index.json").read_text())
    # Every row carries the entry's example, its source in words, and its
    # picture, so the app can show a tile as a preview without fetching it.
    for row in index.get("entries", []):
        entry = json.loads((ROOT / row["file"]).read_text()) if (ROOT / row.get("file", "")).exists() else {}
        for field, expected in (("example", entry.get("plain", {}).get("example")), ("from", entry.get("plain", {}).get("from")), ("gives", entry.get("plain", {}).get("gives"))):
            if row.get(field) != expected:
                problems += fail("index.json", f"{row['id']}: {field} differs from the entry; regenerate the index")
        picture = entry.get("definition", {}).get("placement", {}).get("areas", {}).get("picture", {}).get("picture")
        if row.get("picture") != picture:
            problems += fail("index.json", f"{row['id']}: picture differs from the entry; regenerate the index")
        if entry.get("kind") == "template":
            if row.get("placement") != entry.get("definition", {}).get("placement") or row.get("sample") != entry.get("sample"):
                problems += fail("index.json", f"{row['id']}: placement or sample differs from the entry; regenerate the index")
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
