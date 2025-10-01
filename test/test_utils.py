import numpy as np
import pandas as pd
from utils.query import (
    find_permitted_naics_codes,
    explode_code_lists,
    explode_code,
    exclude_naics_codes,
    query_naics_codes,
)

pd.set_option("display.max_columns", None)


def test_find_permitted_naics_codes_minimum():
    district_uses = pd.DataFrame(
        {
            "Use NAICS Code": ["123", "456"],
            "Zoning District": ["A1", "A1"],
            "Not permitted": [False, True],
        }
    )
    naics_codes = pd.DataFrame(
        {
            "NAICS Code": [
                "123111",
                "123112",
                "123113",
            ],
            "Five-digit Group Code": [
                "12311",
                "12311",
                "12311",
            ],
            "Four-digit Group Code": [
                "1231",
                "1231",
                "1231",
            ],
            "Three-digit Group Code": [
                "123",
                "123",
                "123",
            ],
        }
    )
    actual = find_permitted_naics_codes(district_uses, naics_codes)
    assert len(actual) == 3


def test_explode_code_lists():
    input = pd.DataFrame(
        {
            "id": ["123", "1231"],
            "listy": ["a, b, c", "d"],
        }
    )
    # actual = explode_code_lists(input, "listy")
    actual = input.pipe(explode_code_lists, "listy")
    expected = pd.DataFrame(
        {
            "id": ["123", "123", "123", "1231"],
            "listy": ["a", "b", "c", "d"],
        }
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
        {
            "NAICS Code": ["123111", "123112", "123111", "456456", "456789", "456800"],
            "Permitted value": ["123", "123", "1231", "456", "456", "456"],
        }
    )
    district_uses = pd.DataFrame(
        {
            "Use NAICS Code": ["123", "1231", "456"],
            "NAICS to subtract": ["123111", np.nan, "4567, 456800"],
        }
    )
    actual = permitted_use_codes.pipe(exclude_naics_codes, district_uses)
    expected = pd.DataFrame(
        {
            "NAICS Code": ["123112", "123111", "456456"],
            "Permitted value": ["123", "1231", "456"],
        }
    )
    pd.testing.assert_frame_equal(actual, expected)


def test_query_naics_codes():
    district_uses = pd.DataFrame(
        {
            "Use NAICS Code": ["123", "456"],
            "NAICS to subtract": ["12312, 123141", "456"],
            "Zoning District": ["A1", "A1"],
            "Not permitted": [False, True],
        }
    )
    naics_codes = pd.DataFrame(
        {
            "NAICS Code": [
                "123111",
                "123121",
                "123131",
                "123141",
            ],
            "Five-digit Group Code": [
                "12311",
                "12312",
                "12313",
                "12314",
            ],
            "Four-digit Group Code": [
                "1231",
                "1231",
                "1231",
                "1231",
            ],
            "Three-digit Group Code": [
                "123",
                "123",
                "123",
                "123",
            ],
        }
    )
    actual = query_naics_codes(
        district_uses,
        "A1",
        naics_codes,
    )
    assert actual["NAICS Code"].to_list() == ["123111", "123131"]


def test_query_naics_codes_mock(mock_uses_by_zoning_district, mock_naics_codes):
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
