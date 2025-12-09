import numpy as np
import pandas as pd
from utils.query_helpers import (
    find_permitted_naics_indexes,
    explode_delimited_lists,
    explode_code,
    exclude_naics_codes,
    exclude_naics_names,
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
                "A 456 index to include; Not a 456 but include it",
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
                "Not a 456 but include it",
                "78911",
                "7891",
                "789",
            ],
        ],
    )
    actual = find_permitted_naics_indexes(district_uses, naics_codes)
    assert actual["Use NAICS Code"].to_list() == ["123", "456 (select)", "456 (select)"]
    assert actual["NAICS Code"].to_list() == ["123111", "456111", "789111"]
    assert actual["NAICS Title"].to_list() == [
        "Industry to include",
        "A 456 index to include",
        "Not a 456 but include it",
    ]
    assert actual["Is Allowed"].to_list() == ["Yes", "Yes", "Yes"]


def test_explode_delimited_lists():
    input = pd.DataFrame(
        columns=["id", "listy"],
        data=[
            ["123", "a, b, c"],
            ["1231", "d"],
        ],
    )
    actual = explode_delimited_lists(input, "listy")
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


def test_explode_delimited_lists_spaces():
    input = pd.DataFrame(
        columns=["id", "listy"],
        data=[
            [
                "123",
                "Aerobic dance and exercise centers; Athletic club facilities, physical fitness; Body building studios, physical fitness; Dance centers, aerobic; Exercise centers; Fitness centers; Fitness salons; Fitness spas without accommodations; Gymnasiums; Gyms, physical fitness; Handball club facilities; Health club facilities, physical fitness; Health spas without accommodations, physical fitness; Health studios, physical fitness; Physical fitness centers; Physical fitness facilities; Physical fitness studios; Pilates fitness studios or centers; Racquetball club facilities; Recreational sports club facilities; Spas without accommodations, fitness; Sports club facilities, physical fitness; Squash club facilities; Strength development centers; Tennis club facilities; Tennis courts; Weight training centers; Yoga fitness studios or centers; Billiard parlors; Billiard rooms; Pool halls; Pool parlors;  Pool rooms;  Escape rooms; Racetracks, slot car (i.e., amusement devices)",
            ],
            ["1231", "d"],
        ],
    )
    actual = explode_delimited_lists(input, "listy", delimiter=";")
    assert len(actual) == 36
    assert "Escape rooms" in actual["listy"].to_list()


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
            ["1234", "Other industry to drop; Another industry to drop"],
        ],
    )
    actual = exclude_naics_names(permitted_use_codes, district_uses)
    expected = pd.DataFrame(
        columns=["Permitted value", "NAICS Code", "NAICS Title"],
        data=[
            ["123", "123111", "Industry to keep"],
            ["1234", "123411", "An industry to keep"],
        ],
    )
    pd.testing.assert_frame_equal(actual, expected)
