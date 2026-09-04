# Entry

This document defines an entry of the catalogue: the fields every entry
carries, the six plain-words fields a person reads, and the definition the
app turns into an item.

An entry is one JSON file in `entries/`, named by its id, with these keys:

| Key | What it holds |
| --- | --- |
| `id` | Lowercase letters, digits, and hyphens; the file's name. |
| `kind` | `source`, `query`, or `template`, the catalogue's three lists for the three questions (2026-09-04): a **source** is where the data comes from, the connection alone, the address with its headers and terms, with no extraction and no placed areas, and the app builds a tile from it; a **query** is what intel, a source plus the values picked and formatted, with a suggested look in its placement, added to the feed as it is or adjusted first; a **template** is how it is presented, a look alone, which any query can wear. `item` is accepted for older entries and read as a query. |
| `version` | An integer, raised on every change, so the app can offer updates. |
| `category` | One of `transport`, `energy`, `weather`, `nature`, `money`, `code`, `fun`. |
| `region` | `no` for a Norwegian source, `global` otherwise. |
| `plain` | The six fields a person reads, below. |
| `questions` | What the app asks when the entry is added: `name`, `label`, `help`, `type` (`text`, `number`, `choice`, `location`), optional `choices`, optional `default`. Each `name` appears as `{name}` in the definition's URL or parameters. |
| `attribution` | The text the app shows beside the source's name. |
| `terms` | The URL of the source's terms, and the date they were checked. |
| `sample` | A template alone: one example value per role its areas use, `{"first": "12.4 µg/m³", "second": "Bergen"}`, so the app can preview the look. |
| `definition` | The item in the app's exchange form (`docs/ITEM.md` in the app repository), with `{name}` placeholders where a question's answer goes. `id`, `createdAt`, `position`, and `lastResult` are absent; the app assigns them. |

## A template's definition

A template's definition holds `schemaVersion` and `placement` alone. The
placement's areas hold roles in place of the query's value names: `first`,
`second`, `third`, and `fourth`, starting at `first` with no gap, and a
picture where the look has one. The app applies the look to a query by
rank: the query's first value goes where `first` is, its second where
`second` is, and so on; a query with fewer values than the look has
roles leaves those areas empty. A template's category is `look`, it asks
nothing, and its `from` and `cadence` say so in words.

## The index

`index.json` lists every entry once with its `id`, `name`, `kind`,
`category`, `region`, `version`, and `file`, and, copied from the entry so
the app can show a tile as a preview without fetching it, the entry's
`example`, its `gives`, its `from`, its `picture` when the placement has one, and for a template its `placement` and `sample`. The
check refuses an index whose copies differ from the entries.

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
