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
        [item.strip() for sublist in split_permitted_use_codes for item in sublist]
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
        naics_codes[naics_codes["Five-digit Group Code"].isin(use_codes_five_digits)]
        .sort_values(by="Five-digit Group Code")
        .reset_index(drop=True)
    )
    five_digit_search["Permitted reason"] = "Five-digit Group Code"
    five_digit_search["Permitted value"] = five_digit_search["Five-digit Group Code"]
    four_digit_search = (
        naics_codes[naics_codes["Four-digit Group Code"].isin(use_codes_four_digits)]
        .sort_values(by="Four-digit Group Code")
        .reset_index(drop=True)
    )
    four_digit_search["Permitted reason"] = "Four-digit Group Code"
    four_digit_search["Permitted value"] = four_digit_search["Four-digit Group Code"]
    three_digit_search = (
        naics_codes[naics_codes["Three-digit Group Code"].isin(use_codes_three_digits)]
        .sort_values(by="Three-digit Group Code")
        .reset_index(drop=True)
    )
    three_digit_search["Permitted reason"] = "Three-digit Group Code"
    three_digit_search["Permitted value"] = three_digit_search["Three-digit Group Code"]

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

    permitted_values = pd.concat(
        [
            six_digit_search,
            five_digit_search,
            four_digit_search,
            three_digit_search,
            name_search,
        ]
    ).reset_index(drop=True)

    # Attach the original 'Is Allowed' value from the permitted district uses.
    # Normalize the permitted use codes (they may be comma-separated) so we
    # can join by the permitted value (which is the original Use NAICS Code).
    # mapping = permitted_district_uses[["Use NAICS Code", "Is Allowed"]].copy()
    mapping = permitted_district_uses.copy()
    mapping.loc[:, "Use NAICS Code"] = (
        mapping["Use NAICS Code"]
        .astype(str)
        .str.split(",")
        .apply(lambda lst: [s.strip() for s in lst] if isinstance(lst, list) else lst)
    )
    mapping = mapping.explode("Use NAICS Code").reset_index(drop=True)

    permitted_values = permitted_values.merge(
        mapping,
        how="left",
        left_on="Permitted value",
        right_on="Use NAICS Code",
    )

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
