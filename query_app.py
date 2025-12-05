import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium", css_file="public/custom.css")

with app.setup:
    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # THIS IS AN EXPERIMENTAL APPLICATION
    """)
    return


@app.cell
def _():
    mo.image(
        src="public/img/dcp_logo_standard.svg",
        alt="Notebook Header",
        width=200,
        style={
            "margin-left": "auto",
            "margin-right": "auto",
        },
    )
    return


@app.cell(hide_code=True)
def _():
    mo.center(mo.md("# Use Query Tool"))
    return


@app.cell
def _():
    import pandas as pd
    import polars as pl
    import pyarrow  # to force install in WASM notebook

    # Using mo.notebook_location() to access data both locally and when running via WebAssembly (e.g. hosted on GitHub Pages)
    SOURCE_DATA_DIRECTORY = mo.notebook_location() / "public" / "data"
    return SOURCE_DATA_DIRECTORY, pd, pl


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## This tool helps identify permitted uses for parcels of land in New York City.

    It is based on the NYC Department of City Planning's [Zoning Resolution](https://zoningresolution.planning.nyc.gov/) and the Census Bureau's [North American Industry Classification System](https://www.census.gov/naics/?99967) (NAICS).

    It can can be used to either:

    1. **Query by zoning district** to find which uses are allowed in a certain zoning district
    2. **Query by use name or NAICS Index** to find which zoning districts allow a certain use

    To find the zoning distring for a tax lot, visit [ZoLa](https://zola.planning.nyc.gov/), New York City's Zoning & Land Use Map.
    """)
    return


@app.cell
def _(user_accordion):
    user_accordion
    return


@app.cell
def _():
    mo.md(r"""
    ---
    """)
    return


@app.cell
def _(naics_codes, uses_by_zoning_district):
    mo.accordion(
        {
            "## View all uses and indexes": mo.vstack(
                [
                    mo.md("### Zoning Resolution Uses"),
                    uses_by_zoning_district,
                    mo.md("---"),
                    mo.md("### NAICS Indexes"),
                    naics_codes,
                ]
            ),
        }
    )
    return


@app.cell
def _():
    # build UI components
    return


@app.cell
def _(naics_codes, uses_by_zoning_district_minimal):
    dropdown_districts = mo.ui.dropdown(
        uses_by_zoning_district_minimal["Zoning District"],
        label="Zoning district: ",
        searchable=True,
    )

    dropdown_zr_uses = mo.ui.dropdown(
        uses_by_zoning_district_minimal["Use Name"],
        label="Use name: ",
        searchable=True,
    )
    dropdown_naics_uses = mo.ui.dropdown(
        naics_codes["NAICS Title"],
        label="Use name: ",
        searchable=True,
    )
    tab_use_type = mo.ui.tabs(
        {
            "Zoning Resolution": dropdown_zr_uses,
            "NAICS Index": dropdown_naics_uses,
        }
    )
    return (
        dropdown_districts,
        dropdown_naics_uses,
        dropdown_zr_uses,
        tab_use_type,
    )


@app.cell
def _(dropdown_districts, dropdown_naics_uses, dropdown_zr_uses, tab_use_type):
    selected_district = dropdown_districts.value

    selected_use_name = (
        dropdown_zr_uses.value
        if tab_use_type.value == "Zoning Resolution"
        else dropdown_naics_uses.value
    )
    use_name_header = (
        dropdown_zr_uses.value
        if tab_use_type.value == "Zoning Resolution"
        else dropdown_naics_uses.value
    )

    fake_list = ["code1/NAICS Name 1", "code1/NAICS Name 2"]
    fake_list_text = ", ".join(fake_list)
    fake_name = "An NYC thing"
    zr_to_naics_use_text = f"Use name '{selected_use_name}' is associated with {len(fake_list)} NAICS Index codes in the Zoning Resolution: {fake_list_text}"

    naics_to_zr_use_text = f"NAICS Index name '{selected_use_name}' is associated with the Zoning Resolution use name '{fake_name}'"
    return selected_district, selected_use_name, use_name_header


@app.cell
def _(pd):
    _columns = ["ID", "Name", "Age"]
    _data = [[1, "Alice", 25], [2, "Bob", 30], [3, "Charlie", 22]]

    fake_results = pd.DataFrame(_data, columns=_columns)
    return


@app.cell
def _():
    query_by_district_intro = mo.md("**Start by selecting a zoning district**")
    query_by_use_intro = mo.md(
        "**Start by selecting the type and value of use to query**"
    )
    return query_by_district_intro, query_by_use_intro


@app.cell
def _(pd):
    def format_ui_table(data: pd.DataFrame):
        return mo.ui.table(
            data,
            page_size=25,
            selection=None,
            show_data_types=False,
        )
    return (format_ui_table,)


@app.cell
def _(
    format_ui_table,
    get_district_uses_by_naics_index,
    get_district_uses_by_zr_use,
    get_naics_indexes_by_district,
    naics_codes,
    selected_district,
    selected_use_name,
    tab_use_type,
    use_name_header,
    uses_by_zoning_district_minimal,
):
    # by district
    by_district_result = (
        format_ui_table(
            get_naics_indexes_by_district(
                uses_by_zoning_district_minimal,
                selected_district,
                naics_codes,
                minimal_columns=True,
            )
        )
        if selected_district
        else None
    )
    result_stack_district = mo.vstack(
        [
            f"You chose {selected_district}",
            by_district_result,
        ]
    )

    # by use name
    by_use_name_result = (
        (
            format_ui_table(
                get_district_uses_by_zr_use(
                    uses_by_zoning_district_minimal,
                    selected_use_name,
                    minimal_columns=True,
                )
            )
            if tab_use_type.value == "Zoning Resolution"
            else format_ui_table(
                get_district_uses_by_naics_index(
                    uses_by_zoning_district_minimal,
                    naics_codes,
                    selected_use_name,
                    minimal_columns=True,
                )
            )
        )
        if selected_use_name
        else None
    )
    result_stack_use_name = mo.vstack(
        [
            use_name_header,
            by_use_name_result,
        ]
    )
    return result_stack_district, result_stack_use_name


@app.cell
def _(
    result_stack_district,
    result_stack_use_name,
    selected_district,
    selected_use_name,
):
    conditional_result_district = (
        result_stack_district
        if selected_district
        else "No zoning district selected"
    )

    conditional_result_use_name = (
        result_stack_use_name if selected_use_name else "No use name selected"
    )
    return conditional_result_district, conditional_result_use_name


@app.cell
def _(
    conditional_result_district,
    conditional_result_use_name,
    dropdown_districts,
    query_by_district_intro,
    query_by_use_intro,
    tab_use_type,
):
    user_accordion = mo.accordion(
        {
            "## Query by zoning district": mo.vstack(
                [
                    query_by_district_intro,
                    dropdown_districts,
                    mo.md("---"),
                    conditional_result_district,
                ],
            ),
            "## Query by use": mo.vstack(
                [
                    query_by_use_intro,
                    tab_use_type,
                    mo.md("---"),
                    conditional_result_use_name,
                ]
            ),
        }
    )
    return (user_accordion,)


@app.cell
def _():
    # get data
    return


@app.cell
def _(SOURCE_DATA_DIRECTORY, pl):
    # pandas fails to read csvs from URLs with error "BadGzipFile: Not a gzipped file (b'sp')"
    uses_by_zoning_district_polars = pl.read_csv(
        str(SOURCE_DATA_DIRECTORY / "uses_by_zoning_district.csv"),
        infer_schema_length=None,
    )
    uses_by_zoning_district = uses_by_zoning_district_polars.to_pandas()
    return (uses_by_zoning_district,)


@app.cell
def _(uses_by_zoning_district):
    uses_by_zoning_district_minimal = uses_by_zoning_district.copy()

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
            "Special Permit",
            "Size Restrictions",
            "Additional Conditions",
            "Open Use Allowances",
        ]
    ]
    return (uses_by_zoning_district_minimal,)


@app.cell
def _(SOURCE_DATA_DIRECTORY, pl):
    # pandas fails to read csvs from URLs with error "BadGzipFile: Not a gzipped file (b'sp')"
    naics_codes_polars = pl.read_csv(
        str(SOURCE_DATA_DIRECTORY / "naics_codes.csv"),
        infer_schema_length=None,
    )
    naics_codes = naics_codes_polars.to_pandas()
    return (naics_codes,)


@app.cell
def _():
    # utils below are copied from the utils/ files because they can't be packaged and imported with the WASM notebook.
    return


@app.cell
def _(pd):
    def find_permitted_naics_indexes(
        district_uses: pd.DataFrame,
        naics_codes: pd.DataFrame,
    ) -> pd.DataFrame:
        districts = district_uses["Zoning District"].unique()
        assert len(districts) == 1, (
            f"There should only be one zoning district value, not {districts}"
        )
        permitted_district_uses = district_uses[~district_uses["Not permitted"]]

        # "Use NAICS Code" values are NAICS index codes and are , delimited
        permitted_use_codes = (
            permitted_district_uses["Use NAICS Code"]
            .dropna()
            .sort_values()
            .reset_index(drop=True)
        )
        # may have a comma-delimited list of codes
        split_permitted_use_codes = permitted_use_codes.str.split(",")
        permitted_use_codes = pd.Series(
            [
                item.strip()
                for sublist in split_permitted_use_codes
                for item in sublist
            ]
        )

        # district uses may have no code or a code with 6 to 3 digits
        use_codes_six_digits = permitted_use_codes[
            permitted_use_codes.str.len() == 6
        ].reset_index(drop=True)
        use_codes_five_digits = permitted_use_codes[
            permitted_use_codes.str.len() == 5
        ].reset_index(drop=True)
        use_codes_four_digits = permitted_use_codes[
            permitted_use_codes.str.len() == 4
        ].reset_index(drop=True)
        use_codes_three_digits = permitted_use_codes[
            permitted_use_codes.str.len() == 3
        ].reset_index(drop=True)

        six_digit_search = (
            naics_codes[naics_codes["NAICS Code"].isin(use_codes_six_digits)]
            .sort_values(by="NAICS Code")
            .reset_index(drop=True)
        )
        six_digit_search["Permitted reason"] = "NAICS Code"
        six_digit_search["Permitted value"] = six_digit_search["NAICS Code"]
        five_digit_search = (
            naics_codes[
                naics_codes["Five-digit Group Code"].isin(use_codes_five_digits)
            ]
            .sort_values(by="Five-digit Group Code")
            .reset_index(drop=True)
        )
        five_digit_search["Permitted reason"] = "Five-digit Group Code"
        five_digit_search["Permitted value"] = five_digit_search[
            "Five-digit Group Code"
        ]
        four_digit_search = (
            naics_codes[
                naics_codes["Four-digit Group Code"].isin(use_codes_four_digits)
            ]
            .sort_values(by="Four-digit Group Code")
            .reset_index(drop=True)
        )
        four_digit_search["Permitted reason"] = "Four-digit Group Code"
        four_digit_search["Permitted value"] = four_digit_search[
            "Four-digit Group Code"
        ]
        three_digit_search = (
            naics_codes[
                naics_codes["Three-digit Group Code"].isin(use_codes_three_digits)
            ]
            .sort_values(by="Three-digit Group Code")
            .reset_index(drop=True)
        )
        three_digit_search["Permitted reason"] = "Three-digit Group Code"
        three_digit_search["Permitted value"] = three_digit_search[
            "Three-digit Group Code"
        ]

        code_search = pd.concat(
            [
                six_digit_search,
                five_digit_search,
                four_digit_search,
                three_digit_search,
            ]
        ).reset_index(drop=True)

        # Build mapping by exploded Use NAICS Code so we can attach the original
        # permitted district-use columns to each search result before concatenating.
        mapping_codes = permitted_district_uses.copy()
        mapping_codes.loc[:, "Use NAICS Code"] = (
            mapping_codes["Use NAICS Code"]
            .astype(str)
            .str.split(",")
            .apply(
                lambda lst: [s.strip() for s in lst]
                if isinstance(lst, list)
                else lst
            )
        )
        mapping_codes = mapping_codes.explode("Use NAICS Code").reset_index(
            drop=True
        )

        code_search = code_search.merge(
            mapping_codes,
            how="left",
            left_on="Permitted value",
            right_on="Use NAICS Code",
        )

        # "NAICS index names to include" values are NAICS index titles and are ; delimited
        if not "NAICS index names to include" in permitted_district_uses.columns:
            name_search = pd.DataFrame()
        else:
            names_to_include = (
                permitted_district_uses["NAICS index names to include"]
                .dropna()
                .sort_values()
                .reset_index(drop=True)
            )
            # may have a semicolon-delimited list of codes
            split_names_to_include = names_to_include.str.split(";")
            names_to_include = pd.Series(
                [
                    item.strip()
                    for sublist in split_names_to_include
                    for item in sublist
                ]
            )

            name_search = (
                naics_codes[naics_codes["NAICS Title"].isin(names_to_include)]
                .sort_values(by="NAICS Title")
                .reset_index(drop=True)
            )
            name_search["Permitted reason"] = "NAICS Title"
            name_search["Permitted value"] = name_search["NAICS Title"]

            mapping_names = permitted_district_uses.copy()
            # Build mapping by exploded NAICS index names to include (if present)
            # Also explode any comma-delimited `Use NAICS Code` so each name mapping
            # row refers to a single code (e.g. "456 (select)") when merging below.
            # Explode `Use NAICS Code`, but drop short numeric codes (e.g., 3-digit
            # group codes like "123") so name-based matches don't get attached to
            # plain numeric entries. Those numeric codes are already handled by
            # the code-based search above.
            mapping_names.loc[:, "Use NAICS Code"] = (
                mapping_names["Use NAICS Code"]
                .astype(str)
                .str.split(",")
                .apply(
                    lambda lst: [
                        s.strip()
                        for s in lst
                        if not (s.strip().isdigit() and len(s.strip()) <= 3)
                    ]
                    if isinstance(lst, list)
                    else lst
                )
            )
            mapping_names = mapping_names.explode("Use NAICS Code").reset_index(
                drop=True
            )

            mapping_names.loc[:, "NAICS index names to include"] = (
                mapping_names["NAICS index names to include"]
                .dropna()
                .astype(str)
                .str.split(";")
                .apply(
                    lambda lst: [s.strip() for s in lst]
                    if isinstance(lst, list)
                    else lst
                )
            )
            mapping_names = mapping_names.explode(
                "NAICS index names to include"
            ).reset_index(drop=True)

            name_search = name_search.merge(
                mapping_names,
                how="left",
                left_on="Permitted value",
                right_on="NAICS index names to include",
            )

        permitted_values = pd.concat(
            [
                code_search,
                name_search,
            ]
        ).reset_index(drop=True)

        return permitted_values


    def explode_delimited_lists(
        df: pd.DataFrame, column_to_split: str, delimiter: str = ","
    ) -> pd.DataFrame:
        # Split the column into lists and strip whitespace
        df.loc[:, column_to_split] = (
            df[column_to_split]
            .str.split(delimiter)
            .apply(
                lambda lst: [s.strip() for s in lst]
                if isinstance(lst, list)
                else lst
            )
        )
        # Explode the column
        return df.explode(column_to_split).reset_index(drop=True)


    def explode_code(code: str) -> list[str]:
        code_length = len(code)
        if code_length == 6:
            return [code]
        elif code_length < 6:
            # Pad code with zeros to the right to get the range start
            start = int(code.ljust(6, "0"))
            # Pad code with nines to the right to get the range end
            end = int(code.ljust(6, "9"))
            return [str(i).zfill(6) for i in range(start, end + 1)]
        else:
            raise ValueError("Code must be 6 digits or fewer")


    def exclude_naics_codes(
        permitted_use_codes: pd.DataFrame,
        district_uses: pd.DataFrame,
    ) -> pd.DataFrame:
        permitted_district_uses = district_uses[
            district_uses["Use NAICS Code"].isin(
                permitted_use_codes["Permitted value"]
            )
        ]
        # Split and explode comma-separated lists of codes
        exploded_exclusions = permitted_district_uses.pipe(
            explode_delimited_lists, "NAICS to subtract"
        ).dropna(subset=["NAICS to subtract"])
        # Explode 6-or-less-digit codes to lists of 6-digit codes
        exploded_exclusions["NAICS to subtract"] = exploded_exclusions[
            "NAICS to subtract"
        ].apply(explode_code)
        # After expanding each value to a list of 6-digit codes, explode those lists
        # into individual rows so each row contains a single 6-digit code.
        exploded_exclusions = exploded_exclusions.explode(
            "NAICS to subtract"
        ).reset_index(drop=True)

        reduced_use_codes_indicated = permitted_use_codes.merge(
            exploded_exclusions,
            how="left",
            left_on=["NAICS Code", "Permitted value"],
            right_on=["NAICS to subtract", "Use NAICS Code"],
            indicator=True,
            suffixes=(None, "_exclusions"),
        )
        # Filter for 'left_only' rows and drop the indicator column
        reduced_use_codes = reduced_use_codes_indicated[
            reduced_use_codes_indicated["_merge"] == "left_only"
        ][permitted_use_codes.columns.to_list()].reset_index(drop=True)

        return reduced_use_codes


    def exclude_naics_names(
        permitted_use_codes: pd.DataFrame,
        district_uses: pd.DataFrame,
    ) -> pd.DataFrame:
        permitted_district_uses = district_uses[
            district_uses["Use NAICS Code"].isin(
                permitted_use_codes["Permitted value"]
            )
        ]
        # Split and explode semicolon-separated lists of names
        exploded_exclusions = permitted_district_uses.pipe(
            explode_delimited_lists, "NAICS index names to subtract", ";"
        ).dropna(subset=["NAICS index names to subtract"])
        # After expanding each value to a list of 6-digit codes, explode those lists
        # into individual rows so each row contains a single 6-digit code.
        exploded_exclusions = exploded_exclusions.explode(
            "NAICS index names to subtract"
        ).reset_index(drop=True)

        reduced_use_names_indicated = permitted_use_codes.merge(
            exploded_exclusions,
            how="left",
            left_on=["NAICS Title", "Permitted value"],
            right_on=["NAICS index names to subtract", "Use NAICS Code"],
            indicator=True,
            suffixes=(None, "_exclusions"),
        )
        # Filter for 'left_only' rows and drop the indicator column
        reduced_use_names = reduced_use_names_indicated[
            reduced_use_names_indicated["_merge"] == "left_only"
        ][permitted_use_codes.columns.to_list()].reset_index(drop=True)

        return reduced_use_names
    return exclude_naics_codes, find_permitted_naics_indexes


@app.cell
def _(exclude_naics_codes, find_permitted_naics_indexes, pd):
    ZR_URL_COLUMNS = [
        "Special Permit",
        "Size Restrictions",
        "Additional Conditions",
        "Open Use Allowances",
    ]


    def _reorder_columns(df: pd.DataFrame, first_columns: list):
        # keep the specified columns first (only if they exist), then append any other columns in their current order
        existing_first_cols = [c for c in first_columns if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_first_cols]
        return df.loc[:, existing_first_cols + other_cols]


    def get_district_uses_by_zr_use(
        uses_by_zoning_district: pd.DataFrame,
        use_name: str,
        minimal_columns: bool = False,
    ) -> pd.DataFrame:
        """Return rows from `uses_by_zoning_district` matching a ZR use name.

        Parameters
        ----------
        uses_by_zoning_district : pd.DataFrame
            DataFrame containing zoning resolution uses.
        use_name : str
            The Zoning Resolution `Use Name` to filter for.
        minimal_columns : bool, optional
            When True, the returned DataFrame will contain only the primary
            columns (the listed `first_columns` plus any `ZR_URL_COLUMNS`
            present).

        Returns
        -------
        pd.DataFrame
            A new DataFrame filtered to rows where ``Use Name == use_name``.
        """
        results = uses_by_zoning_district[
            uses_by_zoning_district["Use Name"] == use_name
        ].reset_index(drop=True)
        first_columns = [
            "Use Name",
            "Zoning District",
            "Is Allowed",
        ]
        primary_columns = first_columns + ZR_URL_COLUMNS
        reordered = _reorder_columns(results, primary_columns)
        if minimal_columns:
            return reordered.loc[:, primary_columns]
        return reordered


    def get_naics_indexes_by_district(
        uses_by_zoning_district: pd.DataFrame,
        zoning_distrct: str,
        naics_codes: pd.DataFrame,
        minimal_columns: bool = False,
    ) -> pd.DataFrame:
        """Compute permitted NAICS indexes for a single zoning district.

        This composes the lower-level helpers: it finds permitted NAICS
        indexes for the selected district, then applies NAICS-code-based
        exclusions defined in the district uses.

        Parameters
        ----------
        uses_by_zoning_district : pd.DataFrame
            DataFrame with all district uses.
        zoning_distrct : str
            The zoning district string to filter by.
        naics_codes : pd.DataFrame
            DataFrame of NAICS codes and group mappings.
        minimal_columns : bool, optional
            When True, the returned DataFrame will contain only the primary
            columns (the listed `first_columns` plus any `ZR_URL_COLUMNS`
            present).

        Returns
        -------
        pd.DataFrame
            DataFrame of permitted NAICS index rows for the district.
        """
        district_uses = uses_by_zoning_district[
            uses_by_zoning_district["Zoning District"] == zoning_distrct
        ]
        results = district_uses.pipe(
            find_permitted_naics_indexes, naics_codes
        ).pipe(exclude_naics_codes, district_uses)
        first_columns = [
            "Zoning District",
            "Use Name",
            "Is Allowed",
            "NAICS Title",
            "NAICS Code",
            "Permitted reason",
            "Permitted value",
        ]
        primary_columns = first_columns + ZR_URL_COLUMNS
        reordered = _reorder_columns(results, primary_columns)
        if minimal_columns:
            return reordered.loc[:, primary_columns]
        return reordered


    def get_district_uses_by_naics_index(
        uses_by_zoning_district: pd.DataFrame,
        naics_codes: pd.DataFrame,
        naics_title: str,
        minimal_columns: bool = False,
    ) -> pd.DataFrame:
        """Return zoning-district-level permitted uses for a given NAICS title.

        For each zoning district, compute permitted NAICS indexes and collect
        the results into a single DataFrame. The returned DataFrame is ordered
        to put commonly-used columns first when present.

        Parameters
        ----------
        uses_by_zoning_district : pd.DataFrame
            DataFrame with district uses.
        naics_codes : pd.DataFrame
            DataFrame of NAICS code rows (should include the selected NAICS title row).
        naics_title : str
            The NAICS index title to search for.
        minimal_columns : bool, optional
            When True, the returned DataFrame will contain only the primary
            columns (the listed `first_columns` plus any `ZR_URL_COLUMNS`
            present).

        Returns
        -------
        pd.DataFrame
            DataFrame of permitted NAICS entries across zoning districts for the
            provided NAICS title.
        """
        naics_codes_single = naics_codes[naics_codes["NAICS Title"] == naics_title]
        assert len(naics_codes_single) == 1, (
            f"There should only be one NAICS index, not {len(naics_codes_single)}"
        )
        districts_results = []
        districts = uses_by_zoning_district["Zoning District"].unique().tolist()
        for district in districts:
            district_result = get_naics_indexes_by_district(
                uses_by_zoning_district, district, naics_codes_single
            )
            district_result["Zoning District"] = district
            districts_results.append(district_result)

        results = pd.concat(districts_results, ignore_index=True)
        first_columns = [
            "NAICS Title",
            "NAICS Code",
            "Use Name",
            "Zoning District",
            "Is Allowed",
            "Permitted reason",
            "Permitted value",
        ]
        primary_columns = first_columns + ZR_URL_COLUMNS
        reordered = _reorder_columns(results, primary_columns)
        if minimal_columns:
            return reordered.loc[:, primary_columns]
        return reordered
    return (
        get_district_uses_by_naics_index,
        get_district_uses_by_zr_use,
        get_naics_indexes_by_district,
    )


if __name__ == "__main__":
    app.run()
