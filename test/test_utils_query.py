import pandas as pd
from utils.query import (
    get_naics_indexes_by_district,
    get_district_uses_by_naics_index,
)

pd.set_option("display.max_columns", None)


def test_query_naics_codes():
    district_uses = pd.DataFrame(
        columns=[
            "Use Name",
            "Use NAICS Code",
            "NAICS to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            ["A", "123", "12312, 123141", "A1", False, "Yes kinda"],
            ["B", "456", "456", "A1", True, "No"],
            ["A", "123", "12312, 123141", "A2", False, "Yes kinda"],
            ["B", "456", "456", "A2", True, "No"],
        ],
    )

    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
        ],
        data=[
            ["123111", "12311", "1231", "123"],
            ["123121", "12312", "1231", "123"],
            ["123131", "12313", "1231", "123"],
            ["123141", "12314", "1231", "123"],
        ],
    )
    actual = get_naics_indexes_by_district(
        district_uses,
        "A1",
        naics_codes,
    )
    assert actual["Is Allowed"].to_list() == ["Yes kinda", "Yes kinda"]
    assert actual["NAICS Code"].to_list() == ["123111", "123131"]


def test_query_naics_codes_mock(
    mock_uses_by_zoning_district: pd.DataFrame, mock_naics_codes: pd.DataFrame
):
    actual = get_naics_indexes_by_district(
        mock_uses_by_zoning_district,
        "M2",
        mock_naics_codes,
    )
    assert len(actual) == 733
    assert len(actual[actual["NAICS Code"] == "311512"]) == 5
    assert len(actual[actual["Four-digit Group Code"] == "3115"]) == 105
    assert len(actual[actual["NAICS Code"] == "311611"]) == 0
    assert len(actual[actual["Four-digit Group Code"] == "3116"]) == 0
    assert len(actual[actual["Four-digit Group Code"] == "3117"]) == 0


def test_get_district_uses_by_naics_index():
    district_uses = pd.DataFrame(
        columns=[
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            ["123", "Shouldn't matter", "12312, 123141", "A1", False, "Yes"],
            [
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "A2",
                False,
                "Yes pretty much",
            ],
            ["456", "Shouldn't matter", "456", "A1", True, "No"],
        ],
    )
    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "NAICS Title",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
        ],
        data=[
            ["123111", "Allowed in both", "12311", "1231", "123"],
            ["123112", "Something else", "12311", "1231", "123"],
        ],
    )
    naics_title = "Allowed in both"

    actual = get_district_uses_by_naics_index(district_uses, naics_codes, naics_title)
    expected = pd.DataFrame(
        columns=[
            "NAICS Title",
            "NAICS Code",
            "Zoning District",
            "Is Allowed",
            "Permitted reason",
            "Permitted value",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "Not permitted",
        ],
        data=[
            [
                "Allowed in both",
                "123111",
                "A1",
                "Yes",
                "Three-digit Group Code",
                "123",
                "12311",
                "1231",
                "123",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                False,
            ],
            [
                "Allowed in both",
                "123111",
                "A2",
                "Yes pretty much",
                "Three-digit Group Code",
                "123",
                "12311",
                "1231",
                "123",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                False,
            ],
        ],
    )

    print(actual.columns)
    pd.testing.assert_frame_equal(actual, expected)
