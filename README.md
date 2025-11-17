# Land Use Query

The NYC Department of City Planning has updated the Zoning Resolution to ...

## User paths

There are two paths a user might take:

1. *They know what* their business will be and *want to know where* it can be
2. *They know where* their business will be and *want to know what* it can be

### Knows what, doesn't know where

A user can select a NAICS category and determine which zoning districts allow that land use.

1. Find an appropriate NAICS code description
2. Using the 6-digit NAICS code, find the DCP use associated with that code
3. If the 6-digit code is not in the DCP uses, repeat with the 5-digit code
4. If the 5-digit code is not in the DCP uses, repeat with the 4-digit code
5. ...
6. Note the zoning districts in which this use is allowed and any special ...

### Knows where, doesn't know what

A user can select a zoning district and determine which NAICS categories are allowed on that land.

1. ...

## Development

### Setup

> [!IMPORTANT]
> `uv` is the preferred python environment and package manager ([install docs](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)) but everything here is possible with `pip`.

1. Create a virtual environment with `uv venv`
2. (Optional) Recompile python package requirements with `uv pip compile --upgrade requirements.in -o requirements.txt`
3. Run `uv pip sync requirements.txt` to ensure virtual environment has desired packages and their versions
4. Activate the virtual environment with `source .venv/bin/activate`

### Notebooks

`marimo` [docs](https://docs.marimo.io/)

```bash
# Open a notebook
marimo edit process_data.py
# Open a notebook in app mode
marimo app query.py
```

### Miscellaneous

Formatting files:

```bash
# Format all files in a folder
ruff format utils/
# Format a specific file
ruff format utils/query.py
```

Running tests:

```bash
# Run all tests
python -m pytest
# Run all tests in a file
python -m pytest test/test_utils.py
# Run a specific test
python -m pytest test/test_utils.py::test_query_naics_codes
```

### Docs

[marimo - WebAssembly Notebooks](https://docs.marimo.io/guides/wasm/)
[marimo - Publish to GitHub Pages](https://docs.marimo.io/guides/publishing/github_pages/)
