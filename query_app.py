import marimo

__generated_with = "0.18.3"
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
        src="public/img/dcp-logo-white.svg",
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

    # fake_list = ["code1/NAICS Name 1", "code1/NAICS Name 2"]
    # fake_list_text = ", ".join(fake_list)
    # fake_name = "An NYC thing"
    # zr_to_naics_use_text = f"Use name '{selected_use_name}' is associated with {len(fake_list)} NAICS Index codes in the Zoning Resolution: {fake_list_text}"

    # naics_to_zr_use_text = f"NAICS Index name '{selected_use_name}' is associated with the Zoning Resolution use name '{fake_name}'"
    return selected_district, selected_use_name


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
        if data.empty:
            return "No results, try again."
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
            f"You chose '{selected_district}'",
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
            f"You chose '{selected_use_name}'",
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
        """Return NAICS index rows permitted by a single zoning district's rules.

        This inspects ``district_uses`` for a single ``Zoning District`` and
        builds a set of permitted NAICS index rows (from ``naics_codes``).
        It supports two complementary matching strategies:

        - Code-based matching: values in ``Use NAICS Code`` may be numeric
          prefixes (3-6 digits) or full 6-digit codes; prefixes are matched
          against the appropriate group-code columns in ``naics_codes``.
        - Name-based matching: values in ``NAICS index names to include`` are
          semicolon-delimited NAICS titles and are matched against
          ``naics_codes["NAICS Title"]``.

        Parameters
        ----------
        district_uses : pd.DataFrame
            DataFrame containing zoning district rules. Must contain a single
            unique value in the ``Zoning District`` column.
        naics_codes : pd.DataFrame
            DataFrame containing NAICS index rows and group-code columns.

        Returns
        -------
        pd.DataFrame
            Matched ``naics_codes`` rows with two additional columns appended:
            ``Permitted reason`` (the column used for the match) and
            ``Permitted value`` (the original district value that caused the
            match).
        """

        districts = district_uses["Zoning District"].unique()
        assert len(districts) == 1, (
            f"There should only be one zoning district value, not {districts}"
        )
        permitted_district_uses = district_uses[~district_uses["Not permitted"]]

        # "Use NAICS Code" values are NAICS index codes and are comma-delimited.
        # Reuse the generic `explode_delimited_lists` helper to split, strip,
        # and explode values rather than doing manual string manipulation here.
        permitted_use_codes = (
            explode_delimited_lists(
                permitted_district_uses[["Use NAICS Code"]],
                "Use NAICS Code",
                ",",
            )["Use NAICS Code"]
            .dropna()
            .sort_values()
            .reset_index(drop=True)
        )

        # district uses may have no code or a code with 6 to 3 digits
        # Build searches for code-based permitted values in a DRY way.
        # Map: (length of code string, column in `naics_codes`, readable reason)
        length_column_reason = [
            (6, "NAICS Code", "NAICS Code"),
            (5, "Five-digit Group Code", "Five-digit Group Code"),
            (4, "Four-digit Group Code", "Four-digit Group Code"),
            (3, "Three-digit Group Code", "Three-digit Group Code"),
        ]

        code_search_parts = []
        for length, column_name, reason in length_column_reason:
            matches = permitted_use_codes[permitted_use_codes.str.len() == length]
            if matches.empty:
                continue
            matches = matches.reset_index(drop=True)
            part = (
                naics_codes[naics_codes[column_name].isin(matches)]
                .sort_values(by=column_name)
                .reset_index(drop=True)
            )
            part["Permitted reason"] = reason
            part["Permitted value"] = part[column_name]
            code_search_parts.append(part)

        code_search = (
            pd.concat(code_search_parts, ignore_index=True)
            if code_search_parts
            else pd.DataFrame(
                columns=naics_codes.columns.to_list()
                + ["Permitted reason", "Permitted value"]
            )
        )

        # Build mapping by exploded Use NAICS Code so we can attach the original
        # permitted district-use columns to each search result before concatenating.
        mapping_codes = permitted_district_uses.copy()
        mapping_codes = explode_delimited_lists(
            mapping_codes, "Use NAICS Code", ",", convert_to_str=True
        )

        code_search = code_search.merge(
            mapping_codes,
            how="left",
            left_on="Permitted value",
            right_on="Use NAICS Code",
        )

        # "NAICS index names to include" values are NAICS index titles and are ; delimited
        if not "NAICS index names to include" in permitted_district_uses.columns:
            name_search = pd.DataFrame(
                columns=naics_codes.columns.to_list()
                + ["Permitted reason", "Permitted value"]
            )
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
                [item.strip() for sublist in split_names_to_include for item in sublist]
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
            mapping_names = explode_delimited_lists(
                mapping_names,
                "Use NAICS Code",
                ",",
                convert_to_str=True,
                drop_short_numeric_max_len=6,
            )

            mapping_names.loc[:, "NAICS index names to include"] = (
                mapping_names["NAICS index names to include"]
                .dropna()
                .astype(str)
                .str.split(";")
                .apply(
                    lambda lst: [s.strip() for s in lst] if isinstance(lst, list) else lst
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
        df: pd.DataFrame,
        column_to_split: str,
        delimiter: str = ",",
        convert_to_str: bool = False,
        drop_short_numeric_max_len: int | None = None,
    ) -> pd.DataFrame:
        """Split a delimited column into lists, strip whitespace, and explode it.

        The column values are split on the given ``delimiter``, surrounding
        whitespace is stripped from each item, and the column is exploded so each
        row contains a single item.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the column to split.
        column_to_split : str
            Name of the column to split and explode.
        delimiter : str, optional
            Delimiter to split by, by default ",".
        convert_to_str : bool, optional
            If True, convert the column to string before splitting.
        drop_short_numeric_max_len : int or None, optional
            If provided, drop items which are purely numeric and whose length is
            less than or equal to this value.

        Returns
        -------
        pd.DataFrame
            A new DataFrame where ``column_to_split`` has been expanded and
            exploded into individual rows.
        """

        def _clean_list(lst):
            if not isinstance(lst, list):
                return lst
            if drop_short_numeric_max_len is not None:
                return [
                    s.strip()
                    for s in lst
                    if not (
                        s.strip().isdigit() and len(s.strip()) <= drop_short_numeric_max_len
                    )
                ]
            return [s.strip() for s in lst]

        series = df[column_to_split]
        if convert_to_str:
            series = series.astype(str)
        series = series.str.split(delimiter)
        series = series.apply(
            lambda lst: _clean_list(lst) if isinstance(lst, list) else lst
        )
        df.loc[:, column_to_split] = series
        return df.explode(column_to_split).reset_index(drop=True)


    def explode_code(code: str) -> list[str]:
        """Expand a NAICS prefix into the list of 6-digit NAICS codes it
        represents.

        Examples
        --------
        - ``"12345"`` -> [``"123450"``, ``"123451"``, ..., ``"123459"``]
        - ``"123"`` -> [``"123000"``, ..., ``"123999"``]

        Parameters
        ----------
        code : str
            Numeric string of length 1..6 representing a NAICS code or prefix.

        Returns
        -------
        list[str]
            List of 6-digit NAICS codes represented by the prefix. If ``code`` is
            already 6 digits this returns a single-item list containing ``code``.

        Raises
        ------
        ValueError
            If ``code`` is not a numeric string or is longer than 6 digits.
        """
        if not isinstance(code, str) or not code.isdigit():
            raise ValueError("Code must be a numeric string")

        code_length = len(code)
        if code_length == 6:
            return [code]
        if code_length < 6:
            # Construct integer range by padding the prefix to the start and end
            # values for the full 6-digit range (e.g. "123" -> 123000..123999).
            start = int(code.ljust(6, "0"))
            end = int(code.ljust(6, "9"))
            return [str(i).zfill(6) for i in range(start, end + 1)]

        raise ValueError("Code must be 6 digits or fewer")


    def exclude_naics_codes(
        permitted_use_codes: pd.DataFrame,
        district_uses: pd.DataFrame,
    ) -> pd.DataFrame:
        """Remove excluded NAICS codes listed in district uses from a set of
        permitted NAICS codes.

        The function looks for ``NAICS to subtract`` entries in ``district_uses``,
        expands any prefixes to full 6-digit codes, and subtracts those codes from
        ``permitted_use_codes``.

        Parameters
        ----------
        permitted_use_codes : pd.DataFrame
            DataFrame of permitted NAICS codes. Must include columns ``NAICS Code``
            and ``Permitted value``.
        district_uses : pd.DataFrame
            DataFrame of district uses containing an optional ``NAICS to subtract``
            column with comma-delimited codes or prefixes.

        Returns
        -------
        pd.DataFrame
            Reduced ``permitted_use_codes`` DataFrame with excluded NAICS codes
            removed.
        """

        permitted_district_uses = district_uses[
            district_uses["Use NAICS Code"].isin(permitted_use_codes["Permitted value"])
        ]
        # Split and explode comma-separated lists of codes
        exploded_exclusions = explode_delimited_lists(
            permitted_district_uses, "NAICS to subtract"
        ).dropna(subset=["NAICS to subtract"])
        # Explode 6-or-less-digit codes to lists of 6-digit codes
        exploded_exclusions["NAICS to subtract"] = exploded_exclusions[
            "NAICS to subtract"
        ].apply(explode_code)
        # After expanding each value to a list of 6-digit codes, explode those lists
        # into individual rows so each row contains a single 6-digit code.
        exploded_exclusions = exploded_exclusions.explode("NAICS to subtract").reset_index(
            drop=True
        )

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
        # Split and explode semicolon-separated lists of names
        exploded_exclusions = explode_delimited_lists(
            district_uses, "NAICS index names to subtract", ";"
        ).dropna(subset=["NAICS index names to subtract"])
        # Split and explode comma-separated lists of codes to join to permitted uses
        exploded_exclusions = explode_delimited_lists(
            exploded_exclusions,
            "Use NAICS Code",
        ).dropna(subset=["Use NAICS Code"])

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
    return (
        exclude_naics_codes,
        exclude_naics_names,
        find_permitted_naics_indexes,
    )


@app.cell
def _(
    exclude_naics_codes,
    exclude_naics_names,
    find_permitted_naics_indexes,
    pd,
):
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
        permitted_indexes = find_permitted_naics_indexes(district_uses, naics_codes)
        if permitted_indexes is None:
            return None

        codes_excluded = exclude_naics_codes(permitted_indexes, district_uses)
        assert "NAICS index names to subtract" in district_uses.columns, (
            "Column 'NAICS index names to subtract' missing from District Uses data"
        )
        names_excluded = exclude_naics_names(codes_excluded, district_uses)

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
        reordered = _reorder_columns(names_excluded, primary_columns)
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
