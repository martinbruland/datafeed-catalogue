# datafeed catalogue

This repository holds the catalogue of the datafeed app: the sources,
queries, and finished items a person adds with one tap. It is public and
static: the app reads `index.json` and the entries it lists from this
repository's raw files, so an entry publishes without an app release.

- `index.json`: every entry's id, name, kind (source, query, or template), category, region, and file, with what a preview needs.
- `entries/<id>.json`: one entry, in the shape `SCHEMA.md` defines.
- `scripts/check.py`: the check every entry passes; the workflow runs it on
  every pull request.

What the app is and how it reads the catalogue is decided in the app's
repository (`martinbruland/datafeed`, `docs/ITEM.md`) and its Planner area.
