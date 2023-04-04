"""Defines the base model."""
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import sqlmodel


@dataclass()
class SimilarwebSite:  # pylint: disable=too-many-instance-attributes
    """Represents website page scraped from Similarweb.

    All properties represent the literal strings or string lists scraped from the HTML.
    Properties are assigned with empty strings or lists by default.
    """

    domain: str = ""
    date: str = ""
    global_rank: str = ""
    total_visits: str = ""
    bounce_rate: str = ""
    avg_visit_duration: str = ""
    past_category_ranks: List[int] = field(default_factory=lambda: [-1, -1, -1])
    past_total_visits: List[str] = field(default_factory=lambda: ["", "", ""])
    top_countries: List[Tuple[str, str]] = field(default_factory=lambda: [])
    age_distribution: List[str] = field(default_factory=lambda: [])


class WebVisits(
    sqlmodel.SQLModel, table=True
):  # pylint: disable=too-many-instance-attributes
    """Visit stats for a web page."""

    domain: str = sqlmodel.Field(primary_key=True)
    date: datetime.date = sqlmodel.Field(primary_key=True)
    total_visits: int
    category_rank: int
    global_rank: Optional[int] = sqlmodel.Field(default=None)
    bounce_rate: Optional[float] = sqlmodel.Field(default=None)
    avg_visit_duration: Optional[int] = sqlmodel.Field(default=None)


class VisitsByAge(sqlmodel.SQLModel, table=True):
    """Web page visists by age."""

    domain: str = sqlmodel.Field(primary_key=True)
    date: datetime.date = sqlmodel.Field(primary_key=True)
    min_age: int = sqlmodel.Field(primary_key=True)
    visits: float


@dataclass()
class CountryVisitsShare(sqlmodel.SQLModel, table=True):
    """Web page visits share for a top visitor country."""

    domain: str = sqlmodel.Field(primary_key=True)
    date: datetime.date = sqlmodel.Field(primary_key=True)
    country: str = sqlmodel.Field(primary_key=True)
    share: float = sqlmodel.Field()
