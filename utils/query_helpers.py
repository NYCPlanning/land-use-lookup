import pandas as pd


def find_permitted_naics_indexes(
    district_uses: pd.DataFrame,
    naics_codes: pd.DataFrame,
) -> pd.DataFrame:
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

    code_search = pd.concat(code_search_parts, ignore_index=True) if code_search_parts else pd.DataFrame()

    # Build mapping by exploded Use NAICS Code so we can attach the original
    # permitted district-use columns to each search result before concatenating.
    mapping_codes = permitted_district_uses.copy()
    mapping_codes.loc[:, "Use NAICS Code"] = (
        mapping_codes["Use NAICS Code"]
        .astype(str)
        .str.split(",")
        .apply(lambda lst: [s.strip() for s in lst] if isinstance(lst, list) else lst)
    )
    mapping_codes = mapping_codes.explode("Use NAICS Code").reset_index(drop=True)

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
        mapping_names = mapping_names.explode("Use NAICS Code").reset_index(drop=True)

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
    df: pd.DataFrame, column_to_split: str, delimiter: str = ","
) -> pd.DataFrame:
    # Split the column into lists and strip whitespace
    df.loc[:, column_to_split] = (
        df[column_to_split]
        .str.split(delimiter)
        .apply(lambda lst: [s.strip() for s in lst] if isinstance(lst, list) else lst)
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
        district_uses["Use NAICS Code"].isin(permitted_use_codes["Permitted value"])
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
    permitted_district_uses = district_uses[
        district_uses["Use NAICS Code"].isin(permitted_use_codes["Permitted value"])
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
