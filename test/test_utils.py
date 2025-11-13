import numpy as np
import pandas as pd
from utils.query import (
    find_permitted_naics_indexes,
    explode_delimited_lists,
    explode_code,
    exclude_naics_codes,
    exclude_naics_names,
    get_naics_indexes_by_district,
    get_district_uses_by_naics_index,
)

pd.set_option("display.max_columns", None)


def test_find_permitted_naics_indexes_simple():
    district_uses = pd.DataFrame(
        columns=["Use NAICS Code", "Zoning District", "Not permitted", "Is Allowed"],
        data=[
            ["123", "A1", False, "Yes"],
            ["456", "A1", True, "No"],
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
            ["456111", "45611", "4561", "456"],
        ],
    )
    actual = find_permitted_naics_indexes(district_uses, naics_codes)
    assert actual["Use NAICS Code"].to_list() == ["123", "123", "123"]
    assert actual["Is Allowed"].to_list() == ["Yes", "Yes", "Yes"]


def test_find_permitted_naics_indexes_list():
    district_uses = pd.DataFrame(
        columns=["Use NAICS Code", "Zoning District", "Not permitted", "Is Allowed"],
        data=[
            ["123, 456", "A1", False, "For sure"],
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
            ["456111", "45611", "4561", "456"],
        ],
    )
    actual = find_permitted_naics_indexes(district_uses, naics_codes)
    assert actual["Use NAICS Code"].to_list() == ["123", "456"]
    assert actual["NAICS Code"].to_list() == ["123111", "456111"]
    assert actual["Is Allowed"].to_list() == ["For sure", "For sure"]


def test_find_permitted_naics_indexes_names():
    district_uses = pd.DataFrame(
        columns=[
            "Use NAICS Code",
            "NAICS index names to include",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            [
                "123, 456 (select)",
                "A 456 index to include; Another one",
                "A1",
                False,
                "Yes",
            ],
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
            [
                "123111",
                "Industry to include",
                "12311",
                "1231",
                "123",
            ],
            [
                "456111",
                "A 456 index to include",
                "45611",
                "4561",
                "456",
            ],
            [
                "456111",
                "A 456 index to drop",
                "45611",
                "4561",
                "456",
            ],
            [
                "789111",
                "Another one",
                "78911",
                "7891",
                "789",
            ],
        ],
    )
    actual = find_permitted_naics_indexes(district_uses, naics_codes)
    assert actual["Use NAICS Code"].to_list() == ["123", np.nan, np.nan]
    assert actual["NAICS Code"].to_list() == ["123111", "456111", "789111"]
    assert actual["NAICS Title"].to_list() == [
        "Industry to include",
        "A 456 index to include",
        "Another one",
    ]


def test_explode_delimited_lists():
    input = pd.DataFrame(
        columns=["id", "listy"],
        data=[
            ["123", "a, b, c"],
            ["1231", "d"],
        ],
    )
    actual = input.pipe(explode_delimited_lists, "listy")
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


def test_exclude_naics_names():
    permitted_use_codes = pd.DataFrame(
        columns=["Permitted value", "NAICS Code", "NAICS Title"],
        data=[
            ["123", "123111", "Industry to keep"],
            ["123", "123111", "Industry to drop"],
            ["1234", "123411", "An industry to keep"],
            ["1234", "123411", "Other industry to drop"],
            ["1234", "123411", "Another industry to drop"],
        ],
    )
    district_uses = pd.DataFrame(
        columns=["Use NAICS Code", "NAICS index names to subtract"],
        data=[
            ["123", "Industry to drop"],
            ["1234", "Other industry to drop;Another industry to drop"],
        ],
    )
    actual = permitted_use_codes.pipe(exclude_naics_names, district_uses)
    expected = pd.DataFrame(
        columns=["Permitted value", "NAICS Code", "NAICS Title"],
        data=[
            ["123", "123111", "Industry to keep"],
            ["1234", "123411", "An industry to keep"],
        ],
    )
    pd.testing.assert_frame_equal(actual, expected)


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
            ["123", "Shouldn't matter", "12312, 123141", "A2", False, "Yes pretty much"],
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
            "NAICS Code",
            "NAICS Title",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
            "Permitted reason",
            "Permitted value",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
        ],
        data=[
            [
                "123111",
                "Allowed in both",
                "A1",
                False,
                "Yes",
                "12311",
                "1231",
                "123",
                "Three-digit Group Code",
                "123",
                "123",
                "Shouldn't matter",
                "12312, 123141",
            ],
            [
                "123111",
                "Allowed in both",
                "A2",
                False,
                "Yes pretty much",
                "12311",
                "1231",
                "123",
                "Three-digit Group Code",
                "123",
                "123",
                "Shouldn't matter",
                "12312, 123141",
            ],
        ],
    )

    print(actual.columns)
    pd.testing.assert_frame_equal(actual, expected)
