"""Loads a csv file of SimilarwebSites into a SQLite DB."""
import calendar
import datetime
from pathlib import Path
from typing import Iterable

import dateutil.parser
import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from sweb.model import CountryVisitsShare, SimilarwebSite, VisitsByAge, WebVisits


def parse_csv(csv_file: Path) -> Iterable[SimilarwebSite]:
    """Parses SimilarwebSites from a csv file.

    Args:
        csv_file: path to the csv file containing the SimilarwebSites.

    Yields:
        The SimilarwebSites in csv_file.
    """
    dataframe = pd.read_csv(csv_file)
    items = dataframe.to_dict(orient="records")
    for record in items:
        if record["total_visits"] != "< 5K":
            for key in [
                "past_category_ranks",
                "past_total_visits",
                "top_countries",
                "age_distribution",
            ]:
                record[key] = eval(record[key])  # nosec pylint: disable=eval-used
                # we can trust there isn't malicious Python injection in the csv cell
                # because we created it
            yield SimilarwebSite(**record)


def as_float(number_repr: str) -> float:
    """Normalizes a number string.

    Args:
        number_repr: number representation.

    Raises:
        ValueError: if the number starts with "<"

    Returns:
        The number represented by number_repr.
    """
    number_repr = number_repr.replace(",", "")
    if not number_repr or number_repr.startswith("<"):
        raise ValueError(f"{number_repr} doesn't represent a number!")
    if number_repr.endswith("K"):
        return float(number_repr[:-1]) * 1000
    if number_repr.endswith("M"):
        return float(number_repr[:-1]) * 1000000
    if number_repr.endswith("B"):
        return float(number_repr[:-1]) * 1000000000
    if number_repr.endswith("%"):
        return round(float(number_repr[:-1]) / 100, 4)
    return float(number_repr)


def as_int(number_repr: str) -> int:
    """Normalizes a number string.

    Args:
        number_repr: number representation.

    Returns:
        The number represented by number_repr.
    """
    return int(as_float(number_repr))


def as_seconds(time_repr: str) -> int:
    """Normalizes a time string into seconds.

    Args:
        time_repr: time representation.

    Returns:
        The seconds represented by number_repr.
    """
    time = dateutil.parser.parse(time_repr)
    return 3600 * time.hour + 60 * time.minute + time.second


def _get_date(date_repr: str) -> datetime.date:
    date = dateutil.parser.parse(date_repr).date()
    day = calendar.monthrange(date.year, date.month)[1]
    return datetime.date(date.year, date.month, day)


def get_webvisits(swsite: SimilarwebSite) -> Iterable[WebVisits]:
    """Obtains the WebVisits represented in a SimilarwebSite.

    Args:
        swsite: swsite with the visits to obtain.

    Yields:
        the WebVisits from swsite.
    """
    date = _get_date(swsite.date)
    for months_before, category_rank, total_visits in zip(
        [2, 1], swsite.past_category_ranks[:-1], swsite.past_total_visits[:-1]
    ):
        yield WebVisits(
            domain=swsite.domain,
            date=date - relativedelta(months=months_before),
            category_rank=category_rank,
            total_visits=as_int(total_visits),
        )
    yield WebVisits(
        domain=swsite.domain,
        date=date,
        global_rank=as_int(swsite.global_rank),
        category_rank=swsite.past_category_ranks[2],
        total_visits=as_int(swsite.total_visits),
        bounce_rate=as_float(swsite.bounce_rate),
        avg_visit_duration=as_seconds(swsite.avg_visit_duration),
    )


def get_visits_by_age(swsite: SimilarwebSite) -> Iterable[VisitsByAge]:
    """Obtains the visits by age from a SimilarwebSite.

    Args:
        swsite: swsite with the visits to obtain.

    Yields:
        the visits by age.
    """
    date = _get_date(swsite.date)
    for min_age, visits in zip(
        [18, 25, 35, 45, 55, 65],
        swsite.age_distribution,
    ):
        yield VisitsByAge(
            domain=swsite.domain,
            date=date,
            min_age=min_age,
            visits=as_float(visits),
        )


def get_country_visists_shares(swsite: SimilarwebSite) -> Iterable[CountryVisitsShare]:
    """Obtains the shares of top visiting countries from a SimilarwebSite.

    Args:
        swsite: swsite with the visits to obtain.

    Yields:
        country visits shares.
    """
    date = _get_date(swsite.date)
    for country, share in swsite.top_countries:
        if country != "Others":
            yield CountryVisitsShare(
                domain=swsite.domain,
                date=date,
                country=country,
                share=as_float(share),
            )


def create_sqlite_file_db_engine(sqlite_file: Path) -> Engine:
    """Returns a SQLAlchemy DB engine for a certain SQLite file.

    Args:
        sqlite_file: the sqlite file to store the DB.

    Returns:
        the SQLAlchemy engine for the DB stored at sqlite_file.
    """
    return create_engine(f"sqlite:///{sqlite_file.as_posix()}")


def load_csv_into_sqlite(csv_file: Path, sqlite_file: Path) -> None:
    """Loads SimilarwebSites from a csv file into a SQLite DB file.

    Args:
        csv_file: csv file to load.
        sqlite_file: sqlite_file where to load the csv_file.
    """
    engine = create_sqlite_file_db_engine(sqlite_file)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for swsite in parse_csv(csv_file):
            for webvisits in get_webvisits(swsite):
                session.add(webvisits)
            for visits_by_age in get_visits_by_age(swsite):
                session.add(visits_by_age)
            for country_visits_share in get_country_visists_shares(swsite):
                session.add(country_visits_share)
        session.commit()
