# Entry

This document defines an entry of the catalogue: the fields every entry
carries, the six plain-words fields a person reads, and the definition the
app turns into an item.

An entry is one JSON file in `entries/`, named by its id, with these keys:

| Key | What it holds |
| --- | --- |
| `id` | Lowercase letters, digits, and hyphens; the file's name. |
| `kind` | `source`, `query`, or `item`: how much is filled in. A source has questions and no placement; a query has its parameters filled; an item has a placement too. |
| `version` | An integer, raised on every change, so the app can offer updates. |
| `category` | One of `transport`, `energy`, `weather`, `nature`, `money`, `code`, `fun`. |
| `region` | `no` for a Norwegian source, `global` otherwise. |
| `plain` | The six fields a person reads, below. |
| `questions` | What the app asks when the entry is added: `name`, `label`, `help`, `type` (`text`, `number`, `choice`, `location`), optional `choices`, optional `default`. Each `name` appears as `{name}` in the definition's URL or parameters. |
| `attribution` | The text the app shows beside the source's name. |
| `terms` | The URL of the source's terms, and the date they were checked. |
| `definition` | The item in the app's exchange form (`docs/ITEM.md` in the app repository), with `{name}` placeholders where a question's answer goes. `id`, `createdAt`, `position`, and `lastResult` are absent; the app assigns them. |

## The six plain fields

Every word a person reads in simple mode comes from `plain`, and the check
refuses an entry whose `plain` fields contain the words JSON, URL, API,
key, or path:

| Field | What it says |
| --- | --- |
| `name` | What the person calls it, as a title. |
| `gives` | One sentence on what the person gets. |
| `example` | The values as they will appear on the tile. |
| `from` | The source, named as a person would name it. |
| `cadence` | How often it changes. |
| `asks` | The questions the entry will ask, in one sentence, or "Nothing." |

## A path that finds a list element

A path segment is a key or an index. It may also be an object,
`{"where": "station_id", "is": "175"}`, which picks the first element of
a list whose field `where` equals `is`, compared as text, so a question's
answer can choose the element: `["data", "stations", {"where":
"station_id", "is": "{station}"}, "num_bikes_available"]`.

## Placeholders

`{name}` in the definition's `source.url`, in a parameter's `value`, or in
a header's `value` is replaced by the answer to the question `name`. A
`location` question answers two placeholders, `{name.lat}` and
`{name.lon}`. `{today}` is today's date as `YYYY/MM-DD`, and `{today-iso}`
as `YYYY-MM-DD`, in the person's time zone.
