# Python cheatsheet, for a Java/Laravel developer

Written for someone comfortable with structured code in Java and Laravel
(repositories, migrations, services, models, controllers) who is new to
Python. Every concrete example below is pulled from a real, working FastAPI
project already on this machine: `/home/clalix/projects/holwiv/holwiv/services/passport`.
Open it side by side with this doc.

## 1. There's no compiler, so there's no build step

Java compiles to bytecode before it runs; Python doesn't. `python file.py`
reads the file and executes it top to bottom, line by line, right then. The
closest Python gets to a "build artifact" is the `.pyc` bytecode cache
(`__pycache__/`, see section 4), and that's an automatic side effect, not
something you ever run yourself.

Composer's `vendor/autoload.php` and Maven's dependency resolution still have
an analog in Python (section 2), but there's no `mvn compile` / `php artisan optimize` step. You edit a `.py` file and the next time something imports it,
the new code runs.

## 2. Virtual environments (venv) — Python's `vendor/`

A **virtual environment** is a private, isolated folder holding one specific
Python interpreter plus whatever packages you `pip install` into it. It's the
direct equivalent of Composer's `vendor/` directory or Maven's
project-local dependency set — except Python's package manager (`pip`)
doesn't isolate per-project automatically the way Composer does, so you
create that isolation yourself with a venv. Skip this step and every
`pip install` lands globally on your machine, and two projects needing
different versions of the same package will collide.

```bash
# From inside a project's root directory:
python3 -m venv .venv          # creates the .venv/ folder (the "vendor dir")
source .venv/bin/activate      # "enter" the venv for this shell session
# your prompt now shows (.venv) — pip/python inside this shell are scoped to it
pip install fastapi uvicorn    # installs into .venv/, not globally
deactivate                      # leave the venv, back to your system Python
```

- `.venv/` is **never committed to git** (like `vendor/` or `node_modules/`)
  — every one of HOLWIV's services has a `.gitignore` entry for it.
- Every terminal tab/session needs its own `source .venv/bin/activate` — it
  doesn't persist across shells. If `pip install` or `python` is doing
  something unexpected, check whether you forgot to activate first (`which python` should point inside `.venv/bin/` if you're active).
- `services/passport/pyproject.toml`'s `dependencies` list is the dependency
  manifest — Python's `composer.json`/`pom.xml`. A plain `requirements.txt`
  (just package names, one per line) is the older, simpler alternative still
  used by a lot of projects; `pyproject.toml` is the modern standard and also
  holds project metadata (name, version) the way `composer.json` does.
- There's no `composer.lock` equivalent baked into the tool by default; for
  truly pinned versions people either pin exact versions in
  `requirements.txt` or use a separate tool (Poetry, uv, pip-tools). Don't
  worry about this until you need it.

## 3. Running a project

Three ways you'll see code actually get run:

```bash
python app/main.py              # runs one file directly, top to bottom
python -m app.main               # runs a file *as part of a package* (see __init__.py below)
uvicorn app.main:app --reload    # runs a FastAPI app: "in app/main.py, find the object named `app`"
```

`services/passport` is run the third way — there's no `python main.py` at
all for a FastAPI service. `uvicorn` is the actual program; `app.main:app`
tells it which Python object to serve. `--reload` is the dev-mode flag that
restarts the server whenever a file changes (Laravel's `php artisan serve`
doesn't need this since PHP re-reads files on every request; Python holds
the process in memory, so without `--reload` you'd have to restart it
yourself after every edit).

```bash
cd services/passport
source .venv/bin/activate
uvicorn app.main:app --port 8000 --reload
```

The `if __name__ == "__main__":` idiom you'll see in standalone scripts
(never in `services/passport`, since uvicorn is the entry point there) means
"only run this block if this file was executed directly, not imported by
something else." There's no equivalent concept in Java/PHP because those
don't execute top-level code just by importing a file the way Python does.

## 4. The files and folders that look like noise at first

| Path                        | What it actually is                                                                                                                                                                                                                                                      | Rough Laravel/Java equivalent                                                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `__init__.py`             | An empty (or near-empty) file marking a folder as an importable **package**. `app/api/__init__.py` in passport is 0 bytes — it exists purely so `from app.api.auth import router` works.                                                                      | A namespace declaration, except Python needs the file to *exist*, Java just needs the folder structure to match the package name. |
| `__pycache__/`            | Auto-generated compiled bytecode (`.pyc` files), one per module, created the first time each file is imported. Speeds up the *next* run slightly. Never edit, never commit, safe to delete anytime (it just regenerates).                                            | Nothing in Laravel; roughly like a JVM's class-loading cache, but far less important.                                               |
| `.pytest_cache/`          | pytest's own scratch directory (which tests failed last run, etc.). Auto-created the first time you run `pytest`. Never commit.                                                                                                                                        | PHPUnit doesn't leave an equivalent directory; closest is a CI tool's local cache.                                                  |
| `.venv/`                  | The virtual environment itself (section 2). Never commit.                                                                                                                                                                                                                | `vendor/` / `node_modules/`.                                                                                                    |
| `.env` / `.env.example` | Exactly what you already know from Laravel: real secrets in `.env` (gitignored), a template with blanks in `.env.example` (committed). passport's `app/core/config.py` reads these into a typed `Settings` object at startup.                                    | Identical concept, same file names even.                                                                                            |
| `pyproject.toml`          | Dependency list + project metadata. See section 2.                                                                                                                                                                                                                       | `composer.json` / `pom.xml`.                                                                                                    |
| `conftest.py`             | A pytest-specific file: fixtures and setup code that every test file in that folder (and subfolders) can use *without importing it* — pytest auto-discovers it by name. `services/passport/tests/conftest.py` defines the `db_pool` fixture every test file uses. | Laravel's base `TestCase` class, except Python's version is function-based fixtures, not inheritance.                             |
| `README.md`               | Same as everywhere else — human-facing docs, not read by Python at all.                                                                                                                                                                                                 | Same.                                                                                                                               |

Nothing in this table is magic; they're just filenames and directories that
specific tools (`python`, `pip`, `pytest`) look for by convention, the same
way Laravel looks for `routes/web.php` by convention.

## 5. Concept map: Laravel/Java → Python/FastAPI

| You know this as...                                                                      | In a FastAPI project, it's...                                                                                                                                                                                                                                                                                         | Where in `services/passport`                                                                                 |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Routes + Controllers (`routes/api.php` + `app/Http/Controllers`)                     | **API routers**: a file per resource, each function decorated with the HTTP verb + path, doing what a controller method does                                                                                                                                                                                    | `app/api/contributors.py` — `@router.post("/contributors")`                                               |
| Form Requests (validation) + API Resources (response shaping)                            | **Pydantic schemas**: typed classes that validate incoming JSON and shape outgoing JSON, in one tool instead of two                                                                                                                                                                                             | `app/schemas/contributor.py` — `ContributorCreateRequest`, `ContributorResponse`                        |
| Services (`app/Services`)                                                              | **Services** — genuinely the same word and the same job: the actual business logic, called by the router, doing the real work                                                                                                                                                                                  | `app/services/contributor_service.py` — `create_contributor(...)`                                         |
| Eloquent Models (Active Record: the object *is* the row, and knows how to save itself) | **Plain data classes that mirror a DB row, with no save/query methods of their own.** This is the single biggest conceptual gap from Laravel — see the callout below.                                                                                                                                          | `app/models/contributor.py` — `class Contributor(BaseModel): ...`                                         |
| Migrations (`database/migrations`, `php artisan migrate`)                            | Either raw numbered `.sql` files run by a small custom script (what this project does), or a proper migration tool (Alembic) if you're using an ORM                                                                                                                                                                 | `infra/db/migrations/0001_initial_schema.sql` + `infra/db/migrate.sh`                                      |
| Middleware / Form Request authorization                                                  | **Dependencies** — functions passed to `Depends(...)` that FastAPI runs before your route handler, for auth checks, pulling the current user, etc.                                                                                                                                                           | `app/core/auth.py` — `require_permission("create-consent")`, used as `Depends(require_permission(...))` |
| The service container auto-resolving constructor dependencies                            | **Nothing automatic.** You write `Depends(some_function)` explicitly in every route signature that needs it. Python doesn't guess what you need from type hints the way Laravel's container does.                                                                                                             | Every route in `app/api/*.py`                                                                                |
| Repository pattern                                                                       | **Not a built-in concept at all.** Many simpler FastAPI projects (like this one) just write SQL queries straight inside the service functions. Nothing stops you from adding a repository layer yourself if a project is big enough to want one — it's a design choice, not something the framework gives you. | Query code lives directly inside `app/services/*.py`                                                         |
| `.env` + config                                                                        | **Pydantic Settings** — a typed class that reads env vars once at startup                                                                                                                                                                                                                                      | `app/core/config.py`                                                                                         |
| `bootstrap/app.php` / where the app object gets built                                  | **`main.py`** — creates the `FastAPI()` app, registers routers and middleware                                                                                                                                                                                                                              | `app/main.py`                                                                                                |

### The Active Record gap, specifically

This trips up every Laravel developer at first. In Eloquent:

```php
$user = User::find(1);
$user->name = "New Name";
$user->save();   // the model knows how to persist itself
```

A Pydantic model has **no idea a database exists**. It's purely a typed
container plus validation:

```python
class Contributor(BaseModel):
    id: UUID
    full_name: str
    phone_number: str
    # ... no .save(), no .find(), nothing database-related at all

    @classmethod
    def from_record(cls, record) -> "Contributor":
        return cls(**dict(record))   # just unpacks a DB row into this shape
```

The actual SQL lives in the **service** file, as a plain SQL string run
through the database driver, and the result is wrapped into the model
afterward:

```python
# app/services/contributor_service.py
async def get_contributor(pool, contributor_id):
    record = await pool.fetchrow("select ... from contributors where id = $1", contributor_id)
    return Contributor.from_record(record)
```

If you want Eloquent-style "the object saves itself," you'd reach for an
ORM like SQLAlchemy instead of raw SQL + Pydantic — a different, heavier
choice this project deliberately didn't make. Know that both options exist;
don't assume Pydantic is "Python's Eloquent," because it isn't.

## 6. A real project, folder by folder

```
services/passport/
├── app/
│   ├── main.py            # builds the FastAPI() app, registers every router
│   ├── __init__.py        # empty; makes `app` an importable package
│   ├── api/                # <- routes + controllers
│   │   ├── contributors.py
│   │   ├── auth.py
│   │   └── ...
│   ├── schemas/             # <- request validation + response shaping
│   │   ├── contributor.py
│   │   └── ...
│   ├── services/            # <- business logic, the actual SQL
│   │   ├── contributor_service.py
│   │   └── ...
│   ├── models/               # <- typed shape of a DB row (not Active Record)
│   │   ├── contributor.py
│   │   └── ...
│   └── core/                 # <- config, DB connection pool, auth helpers
│       ├── config.py
│       ├── db.py
│       └── auth.py
├── tests/
│   ├── conftest.py          # shared fixtures every test file can use
│   └── test_contributors.py
├── pyproject.toml            # dependency list + project metadata
├── .env / .env.example
└── Dockerfile
```

### Tracing one request through all five layers

`POST /contributors` (register a new contributor) — follow it exactly like
you'd trace a Laravel request through routes → controller → service → model:

1. **`app/main.py`** registers the router: `app.include_router(contributors_router)`.
2. **`app/api/contributors.py`** — the route function receives the raw
   request, validated into a schema object by FastAPI automatically:

   ```python
   @router.post("/contributors", response_model=ContributorResponse)
   async def create_contributor(data: ContributorCreateRequest, pool=Depends(get_pool)):
       contributor = await contributor_service.create_contributor(pool, data)
       return ContributorResponse(**contributor.model_dump())
   ```

   `data: ContributorCreateRequest` is the whole validation step — if the
   JSON body doesn't match that schema's fields/types, FastAPI rejects it
   with a 422 before your function body even runs. No separate "Form
   Request" class/file needed.
3. **`app/schemas/contributor.py`** defines what a valid request/response
   actually looks like (field names, types, which are optional).
4. **`app/services/contributor_service.py`** does the real work: runs the
   `insert into contributors (...)` SQL, hashes the PIN, checks business
   rules (age must be 18+), and returns a `Contributor`.
5. **`app/models/contributor.py`** is just the typed shape that SQL result
   gets poured into on the way back up.

That's the whole request/response cycle across five small, single-purpose
files — the same separation of concerns Laravel gives you, just without a
framework automatically wiring the pieces together for you; you wire them
yourself with plain function calls and `Depends()`.

## 7. Organizing code inside a file

Python doesn't force "one class per file" the way Java does. A file
(called a **module**) can hold any mix of functions, classes, and constants.
Looking at `app/services/contributor_service.py`: it's mostly plain
functions, not a `ContributorService` class with methods. This is normal,
idiomatic Python — a class is for when you need to bundle *state* with
behavior (an object that remembers something between calls); if a function
just takes inputs and returns an output, it doesn't need a class wrapping it
at all. Don't reflexively translate every Laravel `Service` class into a
Python class with the same name; a module full of functions often *is* the
direct translation.

```python
# A plain function — most of what you'll write
def create_contributor(pool, data: ContributorCreateRequest) -> Contributor:
    ...

# A class — only when you need to hold state across calls
class RateLimiter:
    def __init__(self):
        self._hits: dict[str, list[float]] = {}

    def check(self, key: str) -> bool:
        ...
```

Other conventions that matter day to day:

- **Type hints** (`def foo(x: int) -> str:`) are optional at runtime — Python
  never enforces them by itself — but FastAPI and Pydantic *do* read and
  enforce them for request/response validation, and every editor uses them
  for autocomplete. Write them everywhere; treat them as load-bearing even
  though the language itself doesn't force it.
- **`async def`** marks a function as asynchronous (non-blocking) — needed
  for anything that talks to the database or network in a FastAPI app, since
  the whole server is built on `asyncio`. You `await` an async function to
  actually run it and get its result. If a function doesn't do any
  I/O-waiting, it's usually just a plain `def`.
- **Decorators** (`@router.post(...)`, `@pytest.fixture`, `@classmethod`) are
  Python's version of Java annotations — a line starting with `@` just
  before a function/class that modifies or registers it. `@router.post(...)`
  is doing the same job as Laravel's `Route::post(...)`, just expressed as a
  decorator sitting directly on the function it applies to.
- **Imports resolve relative to where you run Python from**, which is why
  `__init__.py` files and running things with `python -m` (not plain
  `python somefile.py`) matter once a project has subfolders — it's the
  single most common source of "ModuleNotFoundError" confusion coming from
  Java/PHP, where the classpath/autoloader hides this entirely.

## 8. Testing

```bash
cd services/passport
source .venv/bin/activate
pytest                      # runs every tests/test_*.py file
pytest tests/test_auth.py   # just one file
pytest -k "cohort"           # just tests whose name contains "cohort"
pytest -q                    # quiet output, one line per test
```

- pytest auto-discovers any file matching `test_*.py` and any function
  inside it matching `test_*` — no test-suite registration file needed,
  unlike `phpunit.xml` listing suites explicitly.
- `conftest.py` fixtures are requested by **name**, as a parameter:

  ```python
  async def test_create_contributor_success(client, db_pool):
      ...
  ```

  `client` and `db_pool` here aren't imported — pytest sees the parameter
  names, finds matching fixtures in `conftest.py`, and injects them. This is
  the one place Python *does* do automatic "container-style" resolution,
  and it's pytest's own magic, not a general Python feature.
- Async tests need `async def test_...` plus pytest-asyncio installed
  (`pyproject.toml`'s `[tool.pytest.ini_options] asyncio_mode = "auto"`
  handles the rest automatically in this project).

## 9. Day-to-day command cheat block

```bash
# New project, from scratch
mkdir myproject && cd myproject
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]"
pip freeze > requirements.txt     # quick-and-dirty dependency snapshot

# Every time you come back to an existing project
cd myproject
source .venv/bin/activate          # do this first, always
uvicorn app.main:app --reload      # if it's a FastAPI app

# Installing something new mid-project
pip install httpx
pip freeze > requirements.txt      # keep the manifest in sync by hand

# Testing
pytest

# Leaving the venv
deactivate

# Using uv
mkdir myproject && cd myproject
python3 -m venv .venv
source .venv/bin/activate
uv init
uv add fastapi # adding a dependency
```

## 10. Pitfalls specific to coming from Java/Laravel

- **Forgetting to activate the venv.** `pip install` and `python` will
  silently use your system Python instead, installing packages nowhere
  useful. If something that should work doesn't, check `which python`
  first.
- **Expecting the container to auto-wire dependencies.** FastAPI's
  `Depends()` is explicit — you write it on every function that needs it.
  There's no central container config file to register bindings in.
- **Expecting models to save themselves.** See section 5's Active Record
  callout. SQL lives in services, not models, in a raw-SQL project like this
  one.
- **Treating `__init__.py` as optional boilerplate.** An empty file that
  "does nothing" is exactly the point — its *presence* is what matters, not
  its contents.
- **Committing `.venv/` or `__pycache__/`.** Both regenerate from
  `pyproject.toml`/`requirements.txt` and source files respectively; neither
  belongs in git. Check `.gitignore` covers them before your first commit.
- **One-class-per-file habit.** Don't be surprised to see a file full of
  plain functions with no class in sight — that's normal, not unfinished.
