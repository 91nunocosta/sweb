"""Tests loading a csv file of SimilarwebSites into a SQLite DB."""
from datetime import date
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, select

from sweb.loader import (
    as_float,
    as_int,
    as_seconds,
    create_sqlite_file_db_engine,
    get_country_visists_shares,
    get_visits_by_age,
    get_webvisits,
    load_csv_into_sqlite,
    parse_csv,
)
from sweb.model import CountryVisitsShare, SimilarwebSite, VisitsByAge, WebVisits


def test_parse_csv(csv_file: Path, similarweb_site: SimilarwebSite) -> None:
    """Tests parsesing SimilarwebSites from a csv file.

    Args:
        csv_file: csv file for tests.
        similarweb_site: SimilarwebSite data expected for the test HTML file.
    """
    result = list(parse_csv(csv_file))
    assert len(result) == 4  # site with < 5K visits isn't considered
    assert result[3] == similarweb_site


def test_as_number() -> None:
    """Tests normalizing a number string."""
    with pytest.raises(ValueError):
        assert as_float("") is None
    with pytest.raises(ValueError):
        assert as_float("< 5K") is None
    assert as_float("10.0") == 10.0
    assert as_float("10.0") == 10.0
    assert as_float("10,000.0") == 10000.0
    assert as_float("10.0K") == 10000.0
    assert as_float("1.0M") == 1000000.0
    assert as_float("10.0%") == 0.1
    assert as_float("7.43%") == 0.0743
    assert as_int("10") == 10


def test_as_seconds() -> None:
    """Tests normalizing a duration string."""
    assert as_seconds("01:02:03") == 60 * 60 + 2 * 60 + 3


def test_get_webvisits(similarweb_site: SimilarwebSite) -> None:
    """Tests obtaining the WebVisits represented in a SimilarwebSite.

    Args:
        similarweb_site: testing similarweb site page.
    """
    assert list(get_webvisits(similarweb_site)) == [
        WebVisits(
            domain="pitchbook.com",
            date=date(2022, 10, 31),
            total_visits=2800000,
            category_rank=47,
        ),
        WebVisits(
            domain="pitchbook.com",
            date=date(2022, 11, 30),
            total_visits=3000000,
            category_rank=43,
        ),
        WebVisits(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            global_rank=18054,
            total_visits=2500000,
            bounce_rate=0.3603,
            avg_visit_duration=248,
            category_rank=51,
        ),
    ]


def test_get_visits_by_age(similarweb_site: SimilarwebSite) -> None:
    """Tests obtaining the visits by age from a SimilarwebSite.

    Args:
        similarweb_site: testing similarweb site page.
    """
    assert list(get_visits_by_age(similarweb_site)) == [
        VisitsByAge(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            min_age=18,
            visits=0.1945,
        ),
        VisitsByAge(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            min_age=25,
            visits=0.3457,
        ),
        VisitsByAge(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            min_age=35,
            visits=0.2140,
        ),
        VisitsByAge(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            min_age=45,
            visits=0.1286,
        ),
        VisitsByAge(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            min_age=55,
            visits=0.0743,
        ),
        VisitsByAge(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            min_age=65,
            visits=0.0429,
        ),
    ]


def test_get_country_visists_shares(similarweb_site: SimilarwebSite) -> None:
    """Tests obtaining the shares of top visiting countries from a SimilarwebSite.

    Args:
        similarweb_site: testing similarweb site page.
    """
    assert list(get_country_visists_shares(similarweb_site)) == [
        CountryVisitsShare(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            country="United States",
            share=0.4883,
        ),
        CountryVisitsShare(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            country="India",
            share=0.0887,
        ),
        CountryVisitsShare(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            country="United Kingdom",
            share=0.0666,
        ),
        CountryVisitsShare(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            country="Canada",
            share=0.0348,
        ),
        CountryVisitsShare(
            domain="pitchbook.com",
            date=date(2022, 12, 31),
            country="Germany",
            share=0.0229,
        ),
    ]


def test_create_sqlite_file_db_engine(tmp_path: Path) -> None:
    """Test creating an sqlite3.Engine for a SQLite file.

    Args:
        tmp_path: temporary directory.
    """
    sqlite_file = tmp_path / "data.db"
    engine = create_sqlite_file_db_engine(sqlite_file)
    SQLModel.metadata.create_all(engine)


def test_load_csv_into_sqlite(tmp_path: Path, csv_file: Path) -> None:
    """Loads SimilarwebSites from a csv file into a SQLite DB file.

    Args:
        tmp_path: temporary directory.
        csv_file: csv file for testing.
    """
    sqlite_file = tmp_path / "data.sqlite"
    load_csv_into_sqlite(csv_file, sqlite_file)
    engine = create_sqlite_file_db_engine(sqlite_file)
    with Session(engine) as session:
        assert sum(1 for _ in session.exec(select(WebVisits)).all()) == 3 * 4

        assert sum(1 for _ in session.exec(select(VisitsByAge)).all()) == 6 * 4

        assert sum(1 for _ in session.exec(select(CountryVisitsShare)).all()) == 5 * 4
