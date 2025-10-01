# Makes objects available to all tests.
import pytest
import pandas as pd
from pathlib import Path

TEST_DIRECTORY = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def mock_uses_by_zoning_district():
    return pd.read_csv(
        TEST_DIRECTORY / "data/mock_uses_by_zoning_district.csv",
        index_col=False,
        dtype={
            "Use NAICS Code": str,
            "Not permitted": bool,
        },
    )


@pytest.fixture(scope="session")
def mock_naics_codes():
    return pd.read_csv(
        TEST_DIRECTORY / "data/mock_naics_codes.csv", index_col=False, dtype=str
    )
