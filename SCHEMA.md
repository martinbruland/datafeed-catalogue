# Entry

This document defines an entry of the catalogue: the fields every entry
carries, the six plain-words fields a person reads, and the definition the
app turns into an API, a tile, or a layout.

An entry is one JSON file in `entries/`, named by its id, with these keys:

| Key | What it holds |
| --- | --- |
| `id` | Lowercase letters, digits, and hyphens; the file's name. |
| `kind` | `api`, `operation`, or `template`, the catalogue's three lists for the three questions (OpenAPI's words since 2026-09-05): an **api** is where the data comes from, the server alone, the URL with its headers and terms, with no extraction and no placed areas, and the app builds a tile from it; an **operation** is what intel, an API plus the properties picked and formatted, with a suggested layout in its placement, added to the feed as it is or adjusted first; a **template** is how it is presented, a layout alone, which any operation can wear. The app still reads `source`, `query`, and `item` from older catalogues. |
| `version` | An integer, raised on every change, so the app can offer updates. |
| `category` | One of `transport`, `energy`, `weather`, `nature`, `money`, `code`, `fun`. |
| `region` | `no` for a Norwegian API, `global` otherwise. |
| `plain` | The six fields a person reads, below. |
| `questions` | What the app asks when the entry is added: `name`, `label`, `help`, `type` (`text`, `number`, `choice`, `location`), optional `choices`, optional `default`. Each `name` appears as `{name}` in the definition's URL or parameters. |
| `attribution` | The text the app shows beside the API's name. |
| `terms` | The URL of the API's terms, and the date they were checked. |
| `sample` | A template alone: one example value per role its areas use, `{"first": "12.4 µg/m³", "second": "Bergen"}`, so the app can preview the layout. |
| `explains` | Optional: one plain sentence per property, by the property's `name` in the definition's extraction, shown in the builder beside the property's sample when the API's own documentation says nothing: `{"now": "What one kilowatt-hour costs this hour…"}`. |
| `definition` | The tile with its API and properties in the app's exchange form, version 1, which the app reads as an operation and its API (`docs/TILE.md` in the app repository), with `{name}` placeholders where a question's answer goes. `id`, `createdAt`, `position`, and `lastResult` are absent; the app assigns them. |

## A template's definition

A template's definition holds `schemaVersion` and `placement` alone. The
placement's areas hold roles in place of the operation's property names: `first`,
`second`, `third`, and `fourth`, starting at `first` with no gap, and a
picture where the layout has one. The app applies the layout to an
operation by rank: the operation's first property goes where `first` is,
its second where `second` is, and so on; an operation with fewer
properties than the layout has roles leaves those areas empty. A
template's category is `look`, the key the app reads, it asks
nothing, and its `from` and `cadence` say so in words.

## The index

`index.json` lists every entry once with its `id`, `name`, `kind`,
`category`, `region`, `version`, and `file`, and, copied from the entry so
the app can show a tile as a preview without fetching it, the entry's
`example`, its `gives`, its `from`, its `picture` when the placement has one, and for a template its `placement` and `sample`. The
check refuses an index whose copies differ from the entries.

## The six plain fields

Every word a person reads in simple mode comes from `plain`. The app
speaks OpenAPI's words since 2026-09-05, API, operation, parameter,
header, request body, response, and property, so those are welcome; the
check refuses the retired words subscription, item, marketplace, and
dashboard:

| Field | What it says |
| --- | --- |
| `name` | A concise title. For APIs, use the provider or product name, adding a short scope only when needed to distinguish endpoints. |
| `gives` | One short description of the available data or layout. State what it contains; avoid lifestyle advice, introductions, and promotional claims. |
| `example` | The values as they will appear on the tile. |
| `from` | The API, named as a person would name it. |
| `cadence` | How often it changes. |
| `asks` | The questions the entry will ask, in one sentence, or "Nothing." |

## A path that finds a list element

A path segment is a key or an index. It may also be an object,
`{"where": "station_id", "is": "175"}`, which picks the first element of
a list whose field `where` equals `is`, compared as text, so a question's
answer to a question can choose the element: `["data", "stations", {"where":
"station_id", "is": "{station}"}, "num_bikes_available"]`.

## An API that pushes

A definition's `source` key, the API, may carry `"method": "WEBSOCKET"` or `"method":
"EVENTS"`: the app keeps the connection open while the feed is on screen
and each message that is JSON is a response to the operation, so the tile
updates as messages arrive; a message without the operation's properties
is skipped. A `WEBSOCKET` API's `body` is sent once on opening, placeholders filled.
Called once, for a test or an ordinary update, a live API responds with
its first message and the last to follow within a moment.

## An API that sends, and where it explains itself

A definition's `source` key may carry `"method": "POST"` with a `body`, JSON as
text, which the app sends with the request; a question's `{name}` in the
body is filled the way it is in the URL, and the headers should name
the content type. The API may carry `docs`, the URL where the
API explains itself, its documentation or an OpenAPI file, which the
app shows in Explore and on a tile's detail.

## A question answered by lookup

A question of type `lookup` is answered in words and found in another
entry's response: `"lookup": {"entry": "entur-places", "parameter":
"text", "take": ["features", 0, "properties", "id"]}` calls the entry's
API with what the person typed as the parameter `text`, and takes the
property at `take` as the answer; `"match": [...]` instead of
`parameter` matches the text against that property of a list the API
answers whole. The question's placeholder stays in the definition and is
filled when the API is called, so it may sit in the body or the URL. The
app keeps the looked-up entry's API and an operation with the take
property in the library, since the lookup calls it.

## Placeholders

`{name}` in the definition's `source.url`, in a parameter's `value`, or in
a header's `value` is replaced by the answer to the question `name`. A
`location` question answers two placeholders, `{name.lat}` and
`{name.lon}`. `{today}` is today's date as `YYYY/MM-DD`, and `{today-iso}`
as `YYYY-MM-DD`, in the person's time zone.


## Route parameters

Keep variable route segments as named placeholders, for example
`https://api.coinbase.com/v2/prices/{pair}/spot`. Supply a sample value
in `source.parameters`, such as `{"name": "pair", "value": "BTC-NOK"}`,
or obtain it from a question named `pair`. The app keeps the template
on the API and the value on each operation, so different pairs reuse
one API. Fixed endpoint segments remain literal. Parameters without a
URL placeholder become query parameters. Built-in date placeholders
are resolved when the entry is added.

Write question help as one brief instruction with an example where useful.
Use property help to explain units or meaning, without repeating its label.
