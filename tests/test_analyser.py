"""Tests analysing similaerwebsites data."""
from pathlib import Path

import pandas as pd

from sweb.analyser import (
    get_ranks_growth,
    get_visits_growth,
    plot_rank,
    plot_timeseries,
    rank_websites,
)


def test_get_visits_growth(sqlite_file: Path) -> None:
    """Test getting visits month-on-month growth timeseries.

    Args:
        sqlite_file: SQLite DB file for testing.
    """
    series = get_visits_growth(sqlite_file)
    assert set(series.columns) == {
        "google.com",
        "crunchbase.com",
        "stripe.com",
        "pitchbook.com",
    }
    assert len(series.index.tolist()) == 3
    assert all(isinstance(value, pd.Timestamp) for value in series.index.tolist())
    assert all(len(series[col].tolist()) == 3 for col in series)
    assert all(
        isinstance(value, int) for col in series for value in series[col].tolist()
    )
    assert series["google.com"].tolist() == [87000000000, 85100000000, 86400000000]


def test_get_ranks_growth(sqlite_file: Path) -> None:
    """Test getting ranks month-on-month growth timeseries.

    Args:
        sqlite_file: SQLite DB file for testing.
    """
    series = get_ranks_growth(sqlite_file)
    assert set(series.columns) == {
        "google.com",
        "crunchbase.com",
        "stripe.com",
        "pitchbook.com",
    }
    assert len(series.index.tolist()) == 3
    assert all(isinstance(value, pd.Timestamp) for value in series.index.tolist())
    assert all(len(series[col].tolist()) == 3 for col in series)
    assert all(
        isinstance(value, int) for col in series for value in series[col].tolist()
    )
    assert series["google.com"].tolist() == [1, 1, 1]


def test_rank_websites(sqlite_file: Path) -> None:
    """Test ranking websites.

    Args:
        sqlite_file: SQLite DB file for testing.
    """
    rank = rank_websites(sqlite_file)
    expected_rank = pd.Series(
        [0.64, 0.20, 0.16, 0.0],
        index=["crunchbase.com", "pitchbook.com", "stripe.com", "google.com"],
    )
    assert isinstance(rank, pd.Series)
    assert rank.equals(expected_rank)


def test_plot_timeseries(
    tmp_path: Path,
) -> None:
    """Tests plotting a set of timeseries.

    Args:
        tmp_path: temporary directory.
    """
    chart_file = tmp_path / "chart.jpg"
    print(f"generated chart file at: {chart_file.as_posix()}")
    timeseries = pd.DataFrame(
        {
            "series1": [1, 2, 3],
            "series2": [3, 2, 1],
            "series3": [5, 5, 5],
        },
    )
    timeseries.index = [
        pd.Timestamp("2022-10-30"),
        pd.Timestamp("2022-11-30"),
        pd.Timestamp("2022-12-30"),
    ]
    plot_timeseries(
        series=timeseries,
        chart_file=chart_file,
        title="example chart",
        unit="rank",
        reversed_y=True,
    )
    assert chart_file.exists()


def test_plot_rank(
    tmp_path: Path,
) -> None:
    """Tests plotting a rank on a bar chart.

    Args:
        tmp_path: temporary directory.
    """
    chart_file = tmp_path / "chart.jpg"
    print(f"generated chart file at: {chart_file.as_posix()}")
    rank = pd.Series(
        [0.64, 0.20, 0.16, 0.0],
        index=["crunchbase.com", "pitchbook.com", "stripe.com", "google.com"],
    )
    plot_rank(
        rank=rank,
        chart_file=chart_file,
        title="example chart",
    )
    assert chart_file.exists()
