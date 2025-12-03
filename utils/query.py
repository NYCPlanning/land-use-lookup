import pandas as pd

from utils.query_helpers import (
    find_permitted_naics_indexes,
    exclude_naics_codes,
)


def get_district_uses_by_zr_use(
    uses_by_zoning_district: pd.DataFrame,
    use_name: str,
) -> pd.DataFrame:
    """Return rows from `uses_by_zoning_district` matching a ZR use name.

    Parameters
    ----------
    uses_by_zoning_district : pd.DataFrame
        DataFrame containing zoning resolution uses.
    use_name : str
        The Zoning Resolution `Use Name` to filter for.

    Returns
    -------
    pd.DataFrame
        A new DataFrame filtered to rows where ``Use Name == use_name``.
    """
    return uses_by_zoning_district[
        uses_by_zoning_district["Use Name"] == use_name
    ].reset_index(drop=True)


def get_naics_indexes_by_district(
    uses_by_zoning_district: pd.DataFrame,
    zoning_distrct: str,
    naics_codes: pd.DataFrame,
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

    Returns
    -------
    pd.DataFrame
        DataFrame of permitted NAICS index rows for the district.
    """
    district_uses = uses_by_zoning_district[
        uses_by_zoning_district["Zoning District"] == zoning_distrct
    ]
    return district_uses.pipe(find_permitted_naics_indexes, naics_codes).pipe(
        exclude_naics_codes, district_uses
    )


def get_district_uses_by_naics_index(
    uses_by_zoning_district: pd.DataFrame,
    naics_codes: pd.DataFrame,
    naics_title: str,
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
    cols = [
        "NAICS Code",
        "NAICS Title",
        "Zoning District",
        "Not permitted",
        "Is Allowed",
        "Five-digit Group Code",
        "Five-digit Group Title",
        "Four-digit Group Code",
        "Four-digit Group Title",
        "Three-digit Group Code",
        "Three-digit Group Title",
        "Permitted reason",
        "Permitted value",
        "Use NAICS Code",
    ]
    # keep the specified columns first (only if they exist), then append any other columns in their current order
    existing_first_cols = [c for c in cols if c in results.columns]
    other_cols = [c for c in results.columns if c not in existing_first_cols]
    return results.loc[:, existing_first_cols + other_cols]
