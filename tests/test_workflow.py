"""Test the app."""
import os
import unittest.mock
from pathlib import Path

from sweb.workflow import (
    analyse_ranks_growth,
    analyse_visits_growth,
    extract_csv,
    load_sqlite,
    rank,
    run,
)


def test_extract_csv(source_html_dir: Path, tmp_path: Path) -> None:
    """Test extracting an SimilarwebSite into a csv file.

    Args:
        source_html_dir: directory containing the HTML files to parse.
        tmp_path: temporary directory for testing.
    """
    csv_file = tmp_path / "data.csv"
    extract_csv(html_dir=source_html_dir, csv_file=csv_file)
    assert csv_file.exists()
    csv_rows = csv_file.read_text().splitlines()
    assert len(csv_rows) == 6
    assert len(csv_rows[0].split(",")) == 10


def test_load(csv_file: Path, tmp_path: Path) -> None:
    """Test extracting an SimilarwebSite into a csv file.

    Args:
        csv_file: csv file containing testing data.
        tmp_path: temporary directory for testing.
    """
    sqlite_file = tmp_path / "webvisits.jpg"
    load_sqlite(csv_file, sqlite_file)
    assert sqlite_file.exists()


def test_analyse_vists_growth(sqlite_file: Path, tmp_path: Path) -> None:
    """Test plotting the visits growth into a chart image.

    Args:
        sqlite_file: SQLite database file containing the testing data.
        tmp_path: temporary directory for testing.
    """
    chart_file = tmp_path / "visits.jpeg"
    analyse_visits_growth(sqlite_file, chart_file)
    assert chart_file.exists()


def test_analyse_ranks_growth(sqlite_file: Path, tmp_path: Path) -> None:
    """Test plotting the ranks growth into a chart image.

    Args:
        sqlite_file: SQLite database file containing the testing data.
        tmp_path: temporary directory for testing.
    """
    chart_file = tmp_path / "ranks.jpeg"
    analyse_ranks_growth(sqlite_file, chart_file)
    assert chart_file.exists()


def test_plot_rank(sqlite_file: Path, tmp_path: Path) -> None:
    """Test plotting the websites rank into a chart image.

    Args:
        sqlite_file: SQLite database file containing the testing data.
        tmp_path: temporary directory for testing.
    """
    chart_file = tmp_path / "rank.jpeg"
    rank(sqlite_file, chart_file)
    assert chart_file.exists()


def test_run_pipeline(tmp_path: Path) -> None:
    """Test running all pipeline steps.

    Args:
        tmp_path: temporary directory for testing.
    """
    results_path = tmp_path / "results"
    results_path.mkdir()
    (results_path / "webvisits.db").touch()
    with unittest.mock.patch.dict(os.environ, {"RESULTS_DIR": results_path.as_posix()}):
        run()
    assert results_path.exists()
    assert (results_path / "webvisits.csv").exists()
    assert (results_path / "webvisits.db").exists()
    assert (results_path / "visits_growth.jpg").exists()
    assert (results_path / "ranks_growth.jpg").exists()
    assert (results_path / "websites_rank.jpg").exists()
