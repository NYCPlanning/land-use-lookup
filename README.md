# Land Use Lookup

The [Land Use Lookup](https://nycplanning.github.io/land-use-lookup/) tool is intended to make use allowance rules clear and accessible to business and property owners, city staff, and the public in the wake of changes adopted through [City of Yes](https://www.nyc.gov/content/planning/pages/our-work?active=citywide).

This simple web tool allows a user to instantly check whether any particular commercial, residential, or other use is allowed in any zoning district per the [Zoning Resolution](https://zr.planning.nyc.gov/), without having to navigate the text directly. Use allowances can be queried by their official Zoning-defined use names, associated/underlying NAICS indices, or by selecting a zoning district and seeing a full list of what’s allowed there.

## Development

The app is a marimo notebook hosted on GitHub Pages.

A github action converts the notebook to WASM HTML and deploys the page. The action is triggered by changes to the `main` branch but can be configured to use other branches via the repo's Environment settings.

### Setup

> [!IMPORTANT]
> `uv` is the preferred python environment and package manager ([install docs](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)) but everything here is possible with `pip`. See Data Engineering wiki page on [Python management with `uv`](https://github.com/NYCPlanning/data-engineering/wiki/Python-management-with-uv) for more details.

1. Create a virtual environment with `uv venv`
2. (Optional) Recompile python package requirements with `uv pip compile --upgrade requirements.in -o requirements.txt`
3. Run `uv pip sync requirements.txt` to ensure virtual environment has desired packages and their versions
4. Activate the virtual environment with `source .venv/bin/activate`

### Process for making changes

1. Create a new branch to modify data or code files
2. If data files in `input/` have been modified, run `marimo run process_data.py` to update files used by the app
3. (Optional) Run the app locally with `marimo run query_app.py` to confirm changes have the expected results
4. Open a Pull Request to request review of changes (emergency fixes may have to be merged without review)
5. Once approved, merge the Pull Request
6. Once the GitHub action automatically updates and redeploys the app, confirm the changes have the expected results

### Notebooks

`marimo` [docs](https://docs.marimo.io/)

```bash
# Open a notebook
marimo edit process_data.py
# Open a notebook in app mode
marimo run query_app.py
```

```bash
# Export to WASM HTML
uvx --verbose marimo export html-wasm --mode run a_notebook.py --output _site_a_notebook
# Run exported notebook
python -m http.server --directory _site_a_notebook
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
