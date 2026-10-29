# Python + uv + Pydantic Cheatsheet

## 1. Create a Project with uv

```bash
# Create an application project
uv init --app myproject
cd myproject

# Add dependencies
uv add pydantic fastapi "uvicorn[standard]"

# Run Python
uv run python main.py

# Run FastAPI
uv run uvicorn app.main:app --reload
```

`uv init --app myproject` creates the project directory and initializes it as an application.

**You do not need to create or activate `.venv` manually.** Commands such as `uv run` and `uv sync` manage the project's environment automatically.

## 2. Manage Dependencies with uv

```bash
# Add dependencies
uv add pydantic
uv add fastapi "uvicorn[standard]"

# Add development dependencies
uv add --dev pytest ruff mypy

# Add Pydantic email validation
uv add "pydantic[email]"

# Remove a dependency
uv remove pydantic

# Synchronize the environment with project dependencies
uv sync

# Run a command using the project environment
uv run python main.py
uv run pytest

# View installed dependency relationships
uv tree

# Update the lockfile
uv lock

# Upgrade dependencies within allowed version constraints
uv lock --upgrade

# Export dependencies for pip-compatible tools
uv export --format requirements-txt -o requirements.txt
```

**Important:** `uv add` and `uv remove` update your project dependencies and lockfile. You usually do not need to run `uv lock` manually after these commands.

`uv run` automatically ensures the project environment is synchronized before running the command. Use `uv sync` when you want to synchronize the environment explicitly.

## 3. Understand the Project Files

| File                 | Purpose                                                                           |
| -------------------- | --------------------------------------------------------------------------------- |
| `pyproject.toml`   | Project metadata and direct dependencies                                          |
| `uv.lock`          | Exact resolved versions of dependencies, including transitive dependencies        |
| `requirements.txt` | A pip-compatible list of dependencies, often used for deployment or compatibility |
| `.venv/`           | Local virtual environment managed by uv                                           |
| `.python-version`  | Specifies the Python version for the project                                      |

**When using uv, `pyproject.toml` and `uv.lock` are your main dependency-management files.** You do not need `requirements.txt` unless another tool or deployment workflow requires it.

## 4. Use an Existing Project with requirements.txt

There are two common situations.

### A. You want to migrate the project to uv

If the project already has a `requirements.txt` file:

```bash
cd myproject

# Initialize uv if the project has not been initialized
uv init --app

# Import requirements into project dependencies
uv add -r requirements.txt

# Synchronize the environment
uv sync

# Run the application
uv run python main.py
```

After importing the dependencies, `pyproject.toml` and `uv.lock` become the main files for managing them.

### B. You want to keep using pip and requirements.txt

In a traditional pip workflow, you manage the virtual environment yourself:

```bash
# Create and enter the project
mkdir myproject && cd myproject

# Create a virtual environment
python -m venv .venv

# Activate it on Linux
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt

# Save installed packages
python -m pip freeze > requirements.txt

# Deactivate when finished
deactivate
```

To create a `requirements.txt` from scratch, list the required packages, for example:

```text
fastapi
uvicorn[standard]
pydantic
```

Then install them with `python -m pip install -r requirements.txt`.

**Rule of thumb:** Use `uv add` and `uv sync` for a uv-managed project. Use `pip install -r requirements.txt` when following a traditional pip workflow.

## 5. Manage the Environment with uv

You generally do not need to activate the virtual environment or locate its Python executable.

```bash
# Run a Python file
uv run python main.py

# Run a module
uv run python -m app.main

# Run a FastAPI development server
uv run uvicorn app.main:app --reload

# Run Python interactively
uv run python

# Check the Python version used by the project
uv run python --version

# Install/synchronize dependencies without running an application
uv sync

# Run a command without installing the project itself
uv run --no-project python --version
```

Use `uv run` for project commands so that they use the project's environment and dependencies.

## 6. Install and Use Pydantic

```bash
uv add pydantic

# Email validation support
uv add "pydantic[email]"
```

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    email: EmailStr
    account_id: int = Field(gt=0)


user = User(
    name="Lisa",
    email="lisa@example.com",
    account_id=54321,
)

user.model_dump()          # Python dictionary
user.model_dump_json()     # JSON string
user.model_validate(data)  # Validate a dictionary
user.model_copy()          # Copy model
```

- `strict=True`: prevents many automatic type conversions.
- `extra="forbid"`: rejects unexpected fields.
- `Field(gt=0)`: requires a value greater than zero.
- `EmailStr`: validates email addresses.

## 7. Python Type Hints

```python
name: str
age: int
price: float
active: bool
names: list[str]
user: dict[str, str]
email: str | None = None


def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

Type hints describe expected types. They do not, by themselves, validate arbitrary runtime values; Pydantic can validate data against them.

## 8. Testing and Code Quality

```bash
# Install development tools
uv add --dev pytest ruff mypy

# Run tests
uv run pytest
uv run pytest -q

# Check code quality
uv run ruff check .

# Format code
uv run ruff format .

# Run static type checking
uv run mypy .
```

## 9. Project Structure

A typical uv application project may look like this:

```text
myproject/
├── .venv/                 # Created and managed by uv
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── ...
├── tests/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
└── uv.lock
```

The exact generated files depend on the template and project configuration.

For a FastAPI application, you can organize your code into modules such as `api/`, `models/`, `schemas/`, and `services/`. A root-level `app/` layout is also valid if that is the structure you choose.

## 10. .gitignore

```gitignore
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.env
```

Commit `pyproject.toml` and `uv.lock` to version control. Do not commit `.venv/` or secrets in `.env`.

## 11. Essential uv Commands

```bash
uv init --app myproject       # Create an application project
uv add package-name           # Add a dependency
uv add --dev package-name     # Add a development dependency
uv remove package-name        # Remove a dependency
uv sync                       # Synchronize the environment
uv lock                       # Update the lockfile
uv run python main.py         # Run Python
uv run pytest                 # Run tests
uv tree                       # View dependency tree
uv export --format requirements-txt -o requirements.txt
```

## 12. Quick Decision Guide

| Situation                                           | Use                                                                    |
| --------------------------------------------------- | ---------------------------------------------------------------------- |
| Starting a new Python application                   | `uv init --app myproject`                                            |
| Adding a package                                    | `uv add package-name`                                                |
| Installing project dependencies                     | `uv sync`                                                            |
| Running application code                            | `uv run ...`                                                         |
| Existing `requirements.txt` you want to migrate   | `uv add -r requirements.txt`                                         |
| A deployment platform requires `requirements.txt` | `uv export --format requirements-txt -o requirements.txt`            |
| Following a traditional pip-only project            | `python -m venv`, activate, then `pip install -r requirements.txt` |

**Recommended workflow:** For your new Python and FastAPI projects, use `uv init --app`, `uv add`, `uv sync`, and `uv run`. Keep `requirements.txt` for compatibility when needed, rather than maintaining two independent sources of dependency information.
