import numpy as np
import pandas as pd
from utils.query import (
    find_permitted_naics_codes,
    explode_code_lists,
    explode_code,
    exclude_naics_codes,
    exclude_naics_names,
    query_naics_codes,
)

pd.set_option("display.max_columns", None)


def test_find_permitted_naics_codes_minimum():
    district_uses = pd.DataFrame(
        columns=["Use NAICS Code", "Zoning District", "Not permitted"],
        data=[
            ["123", "A1", False],
            ["456", "A1", True],
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
            ["123112", "12311", "1231", "123"],
            ["123113", "12311", "1231", "123"],
        ],
    )
    actual = find_permitted_naics_codes(district_uses, naics_codes)
    assert len(actual) == 3


def test_explode_code_lists():
    input = pd.DataFrame(
        columns=["id", "listy"],
        data=[
            ["123", "a, b, c"],
            ["1231", "d"],
        ],
    )
    # actual = explode_code_lists(input, "listy")
    actual = input.pipe(explode_code_lists, "listy")
    expected = pd.DataFrame(
        columns=["id", "listy"],
        data=[
            ["123", "a"],
            ["123", "b"],
            ["123", "c"],
            ["1231", "d"],
        ],
    )
    pd.testing.assert_frame_equal(actual, expected)


def test_explode_code():
    assert explode_code("12345") == [
        "123450",
        "123451",
        "123452",
        "123453",
        "123454",
        "123455",
        "123456",
        "123457",
        "123458",
        "123459",
    ]


def test_exclude_naics_codes():
    permitted_use_codes = pd.DataFrame(
        columns=["Permitted value", "NAICS Code"],
        data=[
            ["123", "123111"],
            ["123", "123112"],
            ["1231", "123111"],
            ["456", "456456"],
            ["456", "456789"],
            ["456", "456800"],
        ],
    )
    district_uses = pd.DataFrame(
        columns=["Use NAICS Code", "NAICS to subtract"],
        data=[
            ["123", "123111"],
            ["1231", np.nan],
            ["456", "4567, 456800"],
        ],
    )
    actual = permitted_use_codes.pipe(exclude_naics_codes, district_uses)
    expected = pd.DataFrame(
        columns=["Permitted value", "NAICS Code"],
        data=[
            ["123", "123112"],
            ["1231", "123111"],
            ["456", "456456"],
        ],
    )
    pd.testing.assert_frame_equal(actual, expected)


def test_query_naics_codes():
    district_uses = pd.DataFrame(
        columns=["Use NAICS Code", "NAICS to subtract", "Zoning District", "Not permitted"],
        data=[
            ["123", "12312, 123141", "A1", False],
            ["456", "456", "A1", True],
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
    actual = query_naics_codes(
        district_uses,
        "A1",
        naics_codes,
    )
    assert actual["NAICS Code"].to_list() == ["123111", "123131"]


def test_query_naics_codes_mock(mock_uses_by_zoning_district: pd.DataFrame, mock_naics_codes: pd.DataFrame):
    actual = query_naics_codes(
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
