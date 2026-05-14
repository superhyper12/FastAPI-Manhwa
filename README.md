# FastAPI-Manhwa

A REST API built with **FastAPI** that tracks manhwa (Korean comics) by scraping live data from [templetoons.com](https://templetoons.com). It supports creating, reading, updating, and deleting manhwa entries stored in an in-memory database, with scraped metadata including descriptions, latest chapter numbers, and access status (Free vs. Premium).

---

## Project Structure

```
FastAPI-Manhwa/
├── main.py               # Application entry point
├── routes.py             # API endpoint definitions
├── routes_function.py    # Web scraping & helper functions
└── Manhwa_DB.py          # In-memory database & Pydantic data model
```

---

## File Breakdown

### `main.py`
The application entry point. Creates the `FastAPI` app instance, registers the router from `routes.py`, and adds a root welcome route.

**Key responsibilities:**
- Instantiates the `FastAPI` app
- Mounts the `endPoints` router from `routes.py`
- Adds a root `GET /` route returning a welcome message

---

### `Manhwa_DB.py`
Defines the in-memory database (a plain Python dictionary) and the Pydantic data model used when creating new entries.

**`Manhwa_DB`** — A dictionary acting as the runtime database. Each key is a manhwa slug (matching the URL path on templetoons.com), and its value is a dict with:
| Field | Type | Description |
|---|---|---|
| `description` | `str` | Story synopsis scraped from the site |
| `chapters` | `int` | Latest chapter number |
| `access` | `str` | Access type (`"FREE"` or `"PREMIUM"`) |

**`ManhwaModel`** — A Pydantic `BaseModel` with optional `description`, `chapters`, and `access` fields. Used to structure new entries before storing them in `Manhwa_DB`.

---

### `routes_function.py`
Contains all the web scraping and data-extraction logic using `requests` and `BeautifulSoup`. These functions are imported by both `routes.py` and `Manhwa_DB.py`.

| Function | Description |
|---|---|
| `get_parser(path)` | Fetches the templetoons.com comic page for the given slug and returns a parsed `BeautifulSoup` object |
| `get_manhwa_description(path)` | Extracts the story description from the page |
| `get_chapter_tag(path)` | Finds the first `<a>` tag whose `href` contains `"chapter"` |
| `extract_chapter_url(path)` | Returns the URL of the latest chapter link |
| `extract_chapter_number(path)` | Parses the chapter number (as `int`) from the latest chapter URL using regex |
| `extract_chapter_access(path)` | Determines whether the latest chapter is `"FREE"` or `"PREMIUM"` by inspecting a badge span |
| `check_new_chapter(path, storedChapter)` | Compares the scraped chapter number against a stored value; returns the updated chapter and a status message |

---

### `routes.py`
Defines all API endpoints using an `APIRouter` (`endPoints`), which is registered in `main.py`. Each route delegates data access to `Manhwa_DB` and scraping work to `routes_function.py`.

#### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/manhwas` | Returns all entries in `Manhwa_DB` |
| `POST` | `/manhwas/{manhwa_id}/create` | Scrapes and creates a new manhwa entry by slug; returns `400` if it already exists |
| `DELETE` | `/manhwas/{manhwa_id}/delete` | Deletes a manhwa entry by slug; returns `404` if not found |
| `PATCH` | `/manhwas/{manhwa_id}/update-chapter` | Manually sets the `chapters` field for a given manhwa; returns `404` if not found |
| `PATCH` | `/manhwas/{manhwa_id}/update-chapter-from-parser` | Scrapes the latest chapter and updates the stored value if a new chapter is detected |
| `GET` | `/manhwa/{manhwa_id}/latest-chapter` | Returns the latest chapter number scraped live for a given slug |
| `GET` | `/manhwa/{manhwa_id}/chapter-access` | Returns the access type (`FREE` / `PREMIUM`) scraped live |
| `GET` | `/manhwa/{manhwa_id}/description` | Returns the story description scraped live |
| `GET` | `/run-parser` | Debug endpoint that returns raw HTML from the scraped page |

> **Note:** The `{manhwa_id}` path parameter is present in the URL for REST convention, but the actual lookup key used internally is the `manhwa_name` query parameter.

---

## Dependencies

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework
- [Pydantic](https://docs.pydantic.dev/) — Data validation and modeling
- [Requests](https://requests.readthedocs.io/) — HTTP client for scraping
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [httpx](https://www.python-httpx.org/) — Async HTTP client (imported, available for future use)
- [Uvicorn](https://www.uvicorn.org/) — ASGI server to run the app

Install dependencies:
```bash
pip install fastapi uvicorn requests beautifulsoup4 httpx pydantic
```

---

## Running the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs are auto-generated at `http://127.0.0.1:8000/docs`.

---

## Example Usage

**Add a manhwa by its slug:**
```
POST /manhwas/solo-leveling/create?manhwa_name=solo-leveling
```

**Check for a new chapter:**
```
PATCH /manhwas/solo-leveling/update-chapter-from-parser?manhwa_name=solo-leveling
```

**Get all tracked manhwa:**
```
GET /manhwas
```
