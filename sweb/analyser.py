"""Analyses similaerwebsites data."""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio


def get_webvisits_timeseries(sqlite_file: Path, variable: str) -> pd.DataFrame:
    """Get timeseries from webvisits table.

    Args:
        sqlite_file: file path to the SQLite DB to query.
        variable: column whose values to get.

    Returns:
        A total visits dataframe with
            column per domain
            a row per date
    """
    with sqlite3.connect(sqlite_file.as_posix()) as conn:
        query = f"""
            SELECT domain, date, {variable}
            FROM webvisits
            ORDER BY date
        """
        dataframe = pd.read_sql(query, conn, parse_dates=["date"])
    pivot = pd.pivot_table(dataframe, values=variable, index="date", columns="domain")
    pivot.columns.name = None
    return pivot


def get_visits_growth(sqlite_file: Path) -> pd.DataFrame:
    """Get visits month-on-month growth timeseries.

    Args:
        sqlite_file: file path to the SQLite DB to query.

    Returns:
        A total visits dataframe with
            column per domain
            a row per date
    """
    return get_webvisits_timeseries(sqlite_file, "total_visits")


def get_ranks_growth(sqlite_file: Path) -> pd.DataFrame:
    """Get ranks month-on-month growth timeseries.

    Args:
        sqlite_file: file path to the SQLite DB to query.

    Returns:
        A ranks dataframe with
            a column per domain
            a row per date
    """
    return get_webvisits_timeseries(sqlite_file, "category_rank")


def rank_websites(sqlite_file: Path) -> pd.DataFrame:
    """Rank websites with a relative scale.

    Args:
        sqlite_file: file path to the SQLite DB to query.

    Returns:
        A dataframe with columns (domain, rank) representing the websites rank.
    """
    visits = get_visits_growth(sqlite_file)
    category_ranks = get_ranks_growth(sqlite_file)
    visits_change_growth = visits.pct_change().dropna().sum()
    category_ranks_growth = category_ranks.pct_change().dropna().sum()
    growth = visits_change_growth.add(category_ranks_growth)
    min_growth = growth.min()
    growth_interval = growth.max() - min_growth
    relative_growth = growth.apply(lambda x: (x - min_growth) / growth_interval)
    relative_growth_sum = relative_growth.sum()
    rank = relative_growth.apply(lambda x: x / relative_growth_sum)
    rank = rank.apply(lambda x: round(x, 2))
    rank = rank.sort_values(ascending=False)
    return rank


def plot_timeseries(
    series: pd.DataFrame,
    chart_file: Path,
    title: str,
    unit: str,
    reversed_y: bool = False,
) -> None:
    """Plots a set of timeseries.

    Args:
        series: dataframe with a columns per series,
                a row per month within the given interval,
                indexed by date.
        chart_file: file where to plot the timeseries chart.
        title: chart title.
        unit: the unit of y-axis.
        reversed_y: flag to reverse the y axis.
    """
    fig = px.line(
        series, x=series.index, y=list(series.columns), log_y=True, title=title
    )
    fig.update_xaxes(
        title_text="month", tickmode="array", tickvals=series.index, tickformat="%b %Y"
    )
    fig.update_yaxes(title_text=unit)
    if reversed_y:
        fig.update_layout(
            yaxis={"autorange": "reversed", "range": [series.max().max(), 0]}
        )
    pio.write_image(fig, chart_file.as_posix())


def plot_rank(
    rank: pd.Series,
    chart_file: Path,
    title: str,
) -> None:
    """Plots a set of timeseries.

    Args:
        rank: series with rank values, indexed by website.
        chart_file: file where to plot the timeseries chart.
        title: chart title.
    """
    fig = px.bar(rank.sort_values(), title=title, orientation="h")
    fig.update_traces(showlegend=False)
    fig.update_layout(xaxis_title="", yaxis_title="", legend_title="")
    pio.write_image(fig, chart_file.as_posix())
