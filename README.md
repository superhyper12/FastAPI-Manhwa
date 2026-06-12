# FastAPI-Manhwa

A small REST API built with **FastAPI** that tracks manhwa (Korean webcomics) by
scraping live data from [templetoons.com](https://templetoons.com). Entries are kept
in an in-memory dictionary and expose create / read / update / delete operations,
with scraped metadata for description, latest chapter number, and access tier
(Free vs. Premium).

> **Note:** the database is in-memory only — all entries are lost when the server
> restarts. There is no persistence layer.

---

## Architecture

```
main.py              # App entry point: builds FastAPI(), mounts the router, adds GET /
routes.py            # APIRouter "endPoints" — every endpoint lives here
routes_function.py   # Scraping & parsing helpers (requests + BeautifulSoup)
Manhwa_DB.py         # In-memory dict "Manhwa_DB" + the Pydantic "ManhwaModel"
```

Request flow: a route in `routes.py` reads/writes `Manhwa_DB` and delegates any live
scraping to `routes_function.py`, which fetches and parses the templetoons.com page
for a given comic slug.

---

## Module Breakdown

### `main.py`
Creates the `FastAPI` app, includes the `endPoints` router from `routes.py`, and
registers a root `GET /` route (a lambda) that returns a welcome message.

### `Manhwa_DB.py`
Holds the runtime "database" and the data model.

- **`Manhwa_DB`** — a plain `dict` keyed by manhwa slug. It ships seeded with one
  example record (see *Data Model* for its exact, and slightly inconsistent, shape).
- **`ManhwaModel`** — a Pydantic `BaseModel` with three fields, `description: str | None`,
  `chapters: int | None`, `access: str | None`. Used to shape new entries created via
  the API.

### `routes_function.py`
All scraping logic. Uses `requests` for HTTP, `BeautifulSoup` for parsing, and `re`
for chapter-number extraction. (`httpx` is imported but currently unused.)

| Function | Description |
|---|---|
| `get_parser(path)` | GETs `https://templetoons.com/comic/{path}` and returns a parsed `BeautifulSoup`. Raises on HTTP errors. |
| `get_manhwa_description(path)` | Returns the description text, or `None` if the target element is missing. |
| `get_chapter_tag(path)` | Returns the first `<a>` whose `href` contains `"chapter"`, or `None`. |
| `extract_chapter_url(path)` | Returns the `href` of that chapter link, or `None`. |
| `extract_chapter_number(path)` | Parses the chapter number as `int` from the URL (regex `chapter-?(\d+)`, with a digit-sequence fallback). Raises `ValueError` if none found. |
| `extract_chapter_access(path)` | Returns the access badge text, defaulting to `"FREE"` when the badge container is absent. |
| `check_new_chapter(path, storedChapter)` | Returns `(chapter, message)` — the larger of scraped/stored chapter plus a status string. |

### `routes.py`
Defines the `endPoints` `APIRouter`, registered in `main.py`.

---

## Data Model

The seeded record and API-created records do **not** share the same schema today.
This is documented here exactly as it exists so the behavior is predictable:

**Seeded entry (`Manhwa_DB.py`):**
```python
"Manhwa_A": {
    "description": "Postem Morem",
    "Chapter": 10,          # capitalized + singular
    "access": "PREMIUM",
    "releaseDate": "9/28/2025"   # not present on created entries
}
```

**Entry created via `POST .../create` (from `ManhwaModel().dict()`):**
```python
{
    "description": <str>,
    "chapters": <int>,      # lowercase + plural
    "access": <str>
}
```

The key difference — `Chapter` vs `chapters` — matters: the
`update-chapter-from-parser` endpoint reads `record.get("chapters", 0)`, so for the
seeded `Manhwa_A` it never sees the `"Chapter"` value and treats the stored chapter
as `0`. See *Known Issues* for the recommended fix.

---

## Endpoints

Every operation identifies the target comic by the **`manhwa_name` query parameter**.
The `{manhwa_id}` in the path is decorative and is not read by the handlers.

| Method | Path | Query params | Description | Errors |
|---|---|---|---|---|
| `GET` | `/` | — | Welcome message | — |
| `GET` | `/manhwas` | — | Returns the full `Manhwa_DB` | — |
| `POST` | `/manhwas/{manhwa_id}/create` | `manhwa_name` | Scrapes description/chapter/access for the slug and stores a new entry | `400` if the slug already exists |
| `DELETE` | `/manhwas/{manhwa_id}/delete` | `manhwa_name` | Deletes the entry | `404` if not found |
| `PATCH` | `/manhwas/{manhwa_id}/update-chapter` | `manhwa_name`, `Chapter_val` | Manually sets the entry's `chapters` field | `404` if not found |
| `PATCH` | `/manhwas/{manhwa_id}/update-chapter-from-parser` | `manhwa_name` | Scrapes the latest chapter and updates the stored value if newer | `404` if not found |
| `GET` | `/manhwa/{manhwa_id}/latest-chapter` | `manhwa_name` | Live-scraped latest chapter number | — |
| `GET` | `/manhwa/{manhwa_id}/chapter-access` | `manhwa_name` | Live-scraped access tier | — |
| `GET` | `/manhwa/{manhwa_id}/description` | `manhwa_name` | Live-scraped description | — |
| `GET` | `/run-parser` | `manhwa_name` | Debug: returns the raw scraped HTML | — |

FastAPI also serves interactive docs at `/docs` (Swagger UI) and `/redoc`, and the
schema at `/openapi.json`.

---

## Setup

```bash
pip install fastapi uvicorn requests beautifulsoup4 httpx pydantic
```

## Running

```bash
uvicorn main:app --reload
```

The API is then available at `http://127.0.0.1:8000`, with interactive docs at
`http://127.0.0.1:8000/docs`.

---

## Example Usage

```bash
# List everything currently tracked
curl "http://127.0.0.1:8000/manhwas"

# Create an entry by slug (slug = the templetoons.com URL path)
curl -X POST "http://127.0.0.1:8000/manhwas/solo-leveling/create?manhwa_name=solo-leveling"

# Check the live latest chapter
curl "http://127.0.0.1:8000/manhwa/solo-leveling/latest-chapter?manhwa_name=solo-leveling"

# Refresh the stored chapter from the live page
curl -X PATCH "http://127.0.0.1:8000/manhwas/solo-leveling/update-chapter-from-parser?manhwa_name=solo-leveling"

# Manually set a chapter value
curl -X PATCH "http://127.0.0.1:8000/manhwas/solo-leveling/update-chapter?manhwa_name=solo-leveling&Chapter_val=200"

# Delete it
curl -X DELETE "http://127.0.0.1:8000/manhwas/solo-leveling/delete?manhwa_name=solo-leveling"
```

A successful create responds with:
```json
{ "id": "solo-leveling", "data": { "description": "...", "chapters": 200, "access": "FREE" } }
```

---

## Known Issues

These are real behaviors of the current code, listed so the docs stay honest and to
guide cleanup:

1. **Inconsistent DB schema.** The seeded `Manhwa_A` uses `"Chapter"` (capitalized,
   singular) and a `"releaseDate"` field, while API-created entries use `"chapters"`
   (lowercase) and have no `releaseDate`. Because `update-chapter-from-parser` reads
   `"chapters"`, the seeded record's chapter is effectively invisible to it.
   **Fix:** standardize on `chapters` everywhere (and either drop `releaseDate` or add
   it to `ManhwaModel`).

2. **`ManhwaModel` fields are required, not optional.** Each field is typed
   `X | None` but has **no default**, so Pydantic treats all three as required
   (nullable, but mandatory). To make them genuinely optional, give them defaults,
   e.g. `description: str | None = None`.

3. **`extract_chapter_access` can crash.** It calls `.find(...)` on the result of
   `get_chapter_tag(path)`, which returns `None` when no chapter link is found,
   raising `AttributeError`. Guard for `None` before calling `.find`.

4. **`update-chapter` returns a set, not a dict.** The handler returns
   `{"Chapter is changed!"}` (a Python set literal), which FastAPI serializes as the
   JSON array `["Chapter is changed!"]`. Return a dict like
   `{"message": "Chapter is changed!"}` for a conventional response.

5. **Unused path parameter.** `{manhwa_id}` appears in several paths but is never read;
   handlers use the `manhwa_name` query parameter instead. Consider using the path
   parameter directly for a more RESTful design.

6. **`httpx` is imported but unused** in `routes_function.py`.

---

## Dependencies

| Package | Role |
|---|---|
| `fastapi` | Web framework / routing |
| `uvicorn` | ASGI server |
| `requests` | HTTP client for scraping |
| `beautifulsoup4` | HTML parsing |
| `pydantic` | `ManhwaModel` data model |
| `httpx` | Imported, currently unused |
