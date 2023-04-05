"""Provide the command line interface prototype_python_library."""
import logging
import os
from pathlib import Path

import pandas as pd
import parsel.selector

from sweb.analyser import (
    get_ranks_growth,
    get_visits_growth,
    plot_rank,
    plot_timeseries,
    rank_websites,
)
from sweb.loader import load_csv_into_sqlite
from sweb.parser import parse

LOGGER = logging.getLogger(__name__)


def extract_csv(html_dir: Path, csv_file: Path) -> None:
    """Parse a collection of Similarweb site page HTML files and export it into a csv.

    Args:
        html_dir: Path to the directory containing the HTML files to parse.
        csv_file: Path to the csv file where to write the parsed content.
    """
    items = []
    for html_file in html_dir.glob("*.html"):
        dom = parsel.selector.Selector(text=html_file.read_text())
        similarweb_item = parse(dom)
        items.append(vars(similarweb_item))
    pd.DataFrame(items).to_csv(csv_file, index=False)


def load_sqlite(csv_file: Path, sqlite_file: Path) -> None:
    """Loads a collection of SimilarwebSite from a csv
    into the appropriate normalized tables in a SQLite DB.

    Args:
        csv_file: Path to the csv file with the content to load.
        sqlite_file: Path to the sqlite file where to load the content.
    """
    load_csv_into_sqlite(csv_file, sqlite_file)


def analyse_visits_growth(sqlite_file: Path, chart_file: Path) -> None:
    """Plots the visits growth into a chart image.

    Args:
        sqlite_file: Path to the sqlite file where to query the visits.
        chart_file: Path to the jpeg file where to output the chart.
    """
    visits = get_visits_growth(sqlite_file)
    plot_timeseries(visits, chart_file, "Total visits", "visits")


def analyse_ranks_growth(sqlite_file: Path, chart_file: Path) -> None:
    """Plots the ranks growth into a chart image.

    Args:
        sqlite_file: Path to the sqlite file where to query the visits.
        chart_file: Path to the jpeg file where to output the chart.
    """
    ranks = get_ranks_growth(sqlite_file)
    plot_timeseries(ranks, chart_file, "Category ranks", "rank", reversed_y=True)


def rank(sqlite_file: Path, chart_file: Path) -> None:
    """Rank the websites and plot the rank in a bar chart image.

    Args:
        sqlite_file: Path to the sqlite file where to query the visits.
        chart_file: Path to the jpeg file where to output the chart.
    """
    websites_rank = rank_websites(sqlite_file)
    plot_rank(websites_rank, chart_file, title="Websites rank")


def run() -> None:
    """Run entire workflow:
    1. extract data from HTML files into a csv file
    2. load csv's data into a SQLite database file
    3. plot analysis charts:
        - visits growth
        - category ranks growth
        - websites rank
    """
    logging.basicConfig(level=logging.INFO)
    source_html_dir = Path(os.environ.get("HTML_DIR", default="./source_html"))
    results_path = Path(os.environ.get("RESULTS_DIR", default="./results"))
    csv_file = results_path / "webvisits.csv"
    sqlite_file = results_path / "webvisits.db"
    visits_growth_chart_file = results_path / "visits_growth.jpg"
    ranks_growth_chart_file = results_path / "ranks_growth.jpg"
    websites_rank_chart_file = results_path / "websites_rank.jpg"
    results_path.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Extracting website visits into csv %s", csv_file)
    extract_csv(source_html_dir, csv_file)
    if sqlite_file.exists():
        LOGGER.info("Deleting %s", sqlite_file)
        sqlite_file.unlink()
    LOGGER.info("Loading csv's data into SQLite database file %s", sqlite_file)
    load_sqlite(csv_file, sqlite_file)
    LOGGER.info("Plotting websites visits growth into %s", visits_growth_chart_file)
    analyse_visits_growth(sqlite_file, visits_growth_chart_file)
    LOGGER.info(
        "Plotting websites category rank growth into %s", ranks_growth_chart_file
    )
    analyse_ranks_growth(sqlite_file, ranks_growth_chart_file)
    LOGGER.info("Plotting websites rank into %s", websites_rank_chart_file)
    rank(sqlite_file, websites_rank_chart_file)
    LOGGER.info("Done!")
