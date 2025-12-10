import pandas as pd
import numpy as np

from utils.query_helpers import (
    find_permitted_naics_indexes,
    exclude_naics_codes,
    exclude_naics_names,
)

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


def _clean_falsy_values(df: pd.DataFrame) -> pd.DataFrame:
    # replace all falsy values with an empty string
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].replace(False, "")
        df[col] = df[col].replace("False", "")
        df[col] = df[col].fillna("")
    return df


def _prepare_results_columns(
    results: pd.DataFrame, first_columns: list, minimal_columns: bool = False
) -> pd.DataFrame:
    primary_columns = first_columns + ZR_URL_COLUMNS
    reordered = _reorder_columns(results, primary_columns)
    cleaned_values = _clean_falsy_values(reordered)

    result = cleaned_values
    if minimal_columns:
        return result.loc[:, primary_columns]
    return result


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
    return _prepare_results_columns(results, first_columns, minimal_columns)


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
    results = exclude_naics_names(codes_excluded, district_uses)

    first_columns = [
        "Zoning District",
        "Use Group",
        "Use Name",
        "Is Allowed",
        "NAICS Title",
        "NAICS Code",
        "Permitted reason",
        "Permitted value",
    ]
    return _prepare_results_columns(results, first_columns, minimal_columns)


def get_all_uses_by_district(
    uses_by_zoning_district: pd.DataFrame,
    zoning_distrct: str,
    naics_codes: pd.DataFrame,
    minimal_columns: bool = False,
):
    naics_indexes_by_district = get_naics_indexes_by_district(
        uses_by_zoning_district, zoning_distrct, naics_codes, minimal_columns
    )

    zr_uses_by_district = uses_by_zoning_district[
        (uses_by_zoning_district["Zoning District"] == zoning_distrct)
        & (uses_by_zoning_district["Use NAICS Code"].isna())
        & ~uses_by_zoning_district["Not permitted"]
    ].copy()
    if not zr_uses_by_district.empty:
        zr_uses_by_district.loc[:, "Permitted reason"] = "ZR use name"
        zr_uses_by_district.loc[:, "Permitted value"] = zr_uses_by_district["Use Name"]
        first_columns = [
            "Zoning District",
            "Use Group",
            "Use Name",
            "Is Allowed",
        ]
        zr_uses_by_district = _prepare_results_columns(
            zr_uses_by_district, first_columns, minimal_columns
        )

    results = pd.concat([zr_uses_by_district, naics_indexes_by_district]).reset_index(
        drop=True
    )
    return results


def get_district_uses_by_naics_index(
    uses_by_zoning_district: pd.DataFrame,
    naics_codes: pd.DataFrame,
    naics_title: str,
    minimal_columns: bool = False,
    include_all_districts: bool = False,
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
    if results.empty:
        return pd.DataFrame()

    assert len(results["Use Name"].unique().tolist()) == 1
    if include_all_districts:
        all_use_districts = uses_by_zoning_district[
            uses_by_zoning_district["Use Name"] == results["Use Name"].iloc[0]
        ]
        all_use_districts = all_use_districts[
            ["Use Group", "Use Name", "Zoning District", "Is Allowed"]
        ]
        all_use_districts["NAICS Title"] = naics_title
        all_use_districts["NAICS Code"] = naics_codes_single["NAICS Code"].iloc[0]
        results = all_use_districts.merge(
            results,
            how="left",
            on=[
                "NAICS Title",
                "NAICS Code",
                "Use Group",
                "Use Name",
                "Zoning District",
                "Is Allowed",
            ],
        )

    first_columns = [
        "NAICS Title",
        "NAICS Code",
        "Use Group",
        "Use Name",
        "Zoning District",
        "Is Allowed",
        "Permitted reason",
        "Permitted value",
    ]
    return _prepare_results_columns(results, first_columns, minimal_columns)
