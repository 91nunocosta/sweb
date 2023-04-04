"""Defines test fixtures."""
from pathlib import Path

from pytest import fixture

from sweb.model import SimilarwebSite


@fixture()
def data_dir() -> Path:
    """Returns test data directory.

    Returns:
        Path to testing data directory.
    """
    return Path(__file__).parent.parent / "results"


@fixture()
def source_html_dir() -> Path:
    """Returns the path to the directory containing the testing source HTML files.

    Returns:
        Path to testing HTML directory.
    """
    return Path(__file__).parent.parent / "source_html"


@fixture()
def html_file(source_html_dir: Path) -> Path:  # pylint: disable=redefined-outer-name
    """Returns the HTML file for testing.

    Args:
        source_html_dir: Path to directory containing the HTML files.

    Returns:
        Path to the HTML file for testing.
    """
    return source_html_dir / "similarweb-pitchbook-com.html"


@fixture()
def csv_file(data_dir: Path) -> Path:  # pylint: disable=redefined-outer-name
    """Returns the csv file for testing.

    Args:
        data_dir: Path to testing data directory.

    Returns:
        Path to the csv file for testing.
    """
    return data_dir / "webvisits.csv"


@fixture()
def sqlite_file(data_dir: Path) -> Path:  # pylint: disable=redefined-outer-name
    """Returns the sqlite file for testing.

    Args:
        data_dir: Path to testing data directory.

    Returns:
        Path to the csv file for testing.
    """
    return data_dir / "webvisits.db"


@fixture()
def similarweb_site() -> SimilarwebSite:
    """Returns the Similarweb Site page for testing.

    Returns:
        Similarweb Site page for testing.
    """
    return SimilarwebSite(
        domain="pitchbook.com",
        date="December 2022",
        global_rank="18,054",
        total_visits="2.5M",
        bounce_rate="36.03%",
        avg_visit_duration="00:04:08",
        past_category_ranks=[
            47,
            43,
            51,
        ],
        past_total_visits=["2.8M", "3.0M", "2.5M"],
        top_countries=[
            ("United States", "48.83%"),
            ("India", "8.87%"),
            ("United Kingdom", "6.66%"),
            ("Canada", "3.48%"),
            ("Germany", "2.29%"),
            ("Others", "29.88%"),
        ],
        age_distribution=["19.45%", "34.57%", "21.40%", "12.86%", "7.43%", "4.29%"],
    )
