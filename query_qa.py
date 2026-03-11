import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import polars as pl

    from utils.query_helpers import (
        find_permitted_naics_indexes,
        explode_delimited_lists,
        explode_code,
        exclude_naics_codes,
        exclude_naics_names,
    )
    from utils.query import (
        get_naics_indexes_by_district,
        get_district_uses_by_zr_use,
        get_district_uses_by_naics_index,
    )

    SOURCE_DATA_DIRECTORY = mo.notebook_location() / "public" / "data"


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # QA query utils

    This notebook is for checking the results of specific queries by zoning districts, Zoning Resolution uses, and NAICS Indexes.

    These validation or QA checks are in addition to the unit tests and spot checking in the app. These are about the utils, not the UI elements in the app.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Get data
    """)
    return


@app.cell
def _():
    uses_by_zoning_district_polars = pl.read_csv(
        str(SOURCE_DATA_DIRECTORY / "uses_by_zoning_district.csv"),
        infer_schema_length=None,
    )
    # Pandas fails to read csvs from URLs with error "BadGzipFile: Not a gzipped file (b'sp')"
    uses_by_zoning_district = uses_by_zoning_district_polars.to_pandas()
    uses_by_zoning_district
    return (uses_by_zoning_district,)


@app.cell
def _(uses_by_zoning_district):
    url_columns = [
        "Special Permit",
        "Size Restrictions",
        "Additional Conditions",
        "Open Use Allowances",
    ]

    uses_by_zoning_district_minimal = uses_by_zoning_district.copy()

    uses_by_zoning_district_minimal["ZR URL"] = (
        uses_by_zoning_district_minimal[url_columns]
        .astype(str)
        .agg(",".join, axis=1)
    )


    def styled_hyperlink(urls):
        name = "A link"
        return ",".join([f'<a href="{url}">{name}</a>' for url in urls.split(",")])


    def join_and_handle_false(row, cols):
        filtered_values = [str(val) for val in row[cols] if val != "False"]
        return ",".join(filtered_values)


    uses_by_zoning_district_minimal["ZR URLs"] = (
        uses_by_zoning_district_minimal.apply(
            lambda row: join_and_handle_false(row, url_columns), axis=1
        )
    )

    uses_by_zoning_district_minimal = uses_by_zoning_district_minimal[
        [
            "Use Name",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
            "ZR URLs",
        ]
    ]
    uses_by_zoning_district_minimal
    return (uses_by_zoning_district_minimal,)


@app.cell
def _():
    naics_codes_polars = pl.read_csv(
        str(SOURCE_DATA_DIRECTORY / "naics_codes.csv"),
        infer_schema_length=None,
    )
    naics_codes = naics_codes_polars.to_pandas()
    naics_codes
    return (naics_codes,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Test cases
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **R1**

    R1 zoning districts should allowed XXX uses.
    """)
    return


@app.cell
def _(naics_codes, uses_by_zoning_district):
    get_naics_indexes_by_district(
        uses_by_zoning_district,
        "R1",
        naics_codes,
    )
    return


@app.cell
def _(uses_by_zoning_district):
    uses_by_zoning_district
    return


@app.cell
def _(naics_codes):
    naics_codes
    return


@app.cell
def _(naics_codes):
    # "Academies, riding instruction"
    naics_codes
    return


@app.cell
def _():
    return


@app.cell
def _(naics_codes, uses_by_zoning_district):
    zoning_district_list = uses_by_zoning_district[
        "Zoning District"
    ].unique()
    all_addressed_naics_titles = set()

    for district in zoning_district_list:
        dist_results = get_naics_indexes_by_district(
            uses_by_zoning_district,
            district,
            naics_codes,
        )
        naics_titles = dist_results["NAICS Title"].unique().tolist()
        all_addressed_naics_titles.update(set(naics_titles))

    all_addressed_naics_titles = list(all_addressed_naics_titles)
    all_addressed_naics_titles = sorted(all_addressed_naics_titles)
    all_addressed_naics_titles
    return


@app.cell
def _(naics_codes, uses_by_zoning_district):
    c1_results = get_naics_indexes_by_district(
        uses_by_zoning_district,
        "C1",
        naics_codes,
    )
    c1_results
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Outdoor racket courts**

    Outdoor racket courts (use name) should be allowed in C3 with additional conditions
    """)
    return


@app.cell
def _(uses_by_zoning_district_minimal):
    zr_use_name_racket_courts = "Outdoor racket courts"
    get_district_uses_by_zr_use(
        uses_by_zoning_district_minimal, zr_use_name_racket_courts
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Sailboat dealers**

    Sailboat dealers (NAICS index) should be allowed in C3 districts with additional conditions
    """)
    return


@app.cell
def _(naics_codes):
    naics_title_sailboat_dealers = "Sailboat dealers"
    naics_codes[
        naics_codes["NAICS Title"] == naics_title_sailboat_dealers
    ].reset_index(drop=True)
    return (naics_title_sailboat_dealers,)


@app.cell
def _(naics_codes, naics_title_sailboat_dealers, uses_by_zoning_district):
    get_district_uses_by_naics_index(
        uses_by_zoning_district,
        naics_codes,
        naics_title_sailboat_dealers,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Escape rooms**

    Escape rooms (NAICS index name – under Select entertainment facilities use name) should be allowed in C3 districts by special permit, C1 with size restrictions
    """)
    return


@app.cell
def _(naics_codes):
    naics_title_escape_rooms = "Escape rooms"
    naics_codes[
        naics_codes["NAICS Title"] == naics_title_escape_rooms
    ].reset_index(drop=True)
    return (naics_title_escape_rooms,)


@app.cell
def _(naics_codes, naics_title_escape_rooms, uses_by_zoning_district):
    get_district_uses_by_naics_index(
        uses_by_zoning_district,
        naics_codes,
        naics_title_escape_rooms,
    )
    return


@app.cell
def _(uses_by_zoning_district):
    uses_by_zoning_district[
        uses_by_zoning_district["Use Name"]
        == "#Select entertainment facilities#"
    ]
    return


@app.cell
def _(uses_by_zoning_district):
    uses_by_zoning_district[
        uses_by_zoning_district["Use Name"]
        == "#Amusement or recreation facilities#"
    ]
    return


@app.cell
def _(uses_by_zoning_district):
    _district_uses = uses_by_zoning_district[
        uses_by_zoning_district["Use Name"]
        == "#Amusement or recreation facilities#"
    ]
    exploded_exclusions = explode_delimited_lists(
        _district_uses, "NAICS index names to subtract", ";"
    ).dropna(subset=["NAICS index names to subtract"])
    # Split and explode comma-separated lists of codes to join to permitted uses
    exploded_exclusions = explode_delimited_lists(
        exploded_exclusions, "Use NAICS Code",
    ).dropna(subset=["Use NAICS Code"])
    exploded_exclusions
    return


@app.cell
def _(naics_codes, naics_title_escape_rooms, uses_by_zoning_district):
    _naics_codes = naics_codes[
        naics_codes["NAICS Title"] == naics_title_escape_rooms
    ].reset_index(drop=True)

    _uses = uses_by_zoning_district[
        uses_by_zoning_district["Use Name"]
        == "#Amusement or recreation facilities#"
    ]
    _uses_c1 = _uses[_uses["Zoning District"] == "C1"]

    get_naics_indexes_by_district(_uses, "C1", _naics_codes)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Day spas**

    Day spas (NAICS index name – under Health and fitness use name) should be allowed in C3 districts with additional conditions and open use allowances
    """)
    return


@app.cell
def _(naics_codes, uses_by_zoning_district):
    naics_title_day_spas = "Day spas"
    get_district_uses_by_naics_index(
        uses_by_zoning_district,
        naics_codes,
        naics_title_day_spas,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Lentil Farmimg**

    Lentil farming is not addressed by any uses in the ZR so the result should be an empty table
    """)
    return


@app.cell
def _(naics_codes, uses_by_zoning_district):
    naics_title_lentils = "Lentil farming, dry, field and seed production"
    get_district_uses_by_naics_index(
        uses_by_zoning_district,
        naics_codes,
        naics_title_lentils,
    )
    return


if __name__ == "__main__":
    app.run()
