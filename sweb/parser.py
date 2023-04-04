"""Parses website pages from Similarweb."""
from typing import List

import parsel.selector

from sweb.model import SimilarwebSite


def parse_number(text: str) -> float:
    """Parses an integer string.

    Args:
        text: string representing the integer number.

    Returns:
        The integer represented by the string.
    """
    return float(text.replace(",", ""))


def _parse_series_chart_ordinates(
    chart_svg: parsel.selector.SelectorList[parsel.selector.Selector],
) -> List[int]:
    """Parses the ordinates (y-axis values) from an highcharts series chart.

    Args:
        chart_svg: the SVG HTML element defining the chart.

    Returns:
        the ordinates (y-axis values) of the series points.
    """
    height = int(chart_svg.attrib["height"])
    yaxis = list(
        map(parse_number, chart_svg.css(".highcharts-yaxis-labels text::text").getall())
    )
    min_y, max_y = yaxis[0], yaxis[-1]
    scale = (max_y - min_y) / height
    series_y = (
        float(d.split()[2])
        for d in chart_svg.css(".highcharts-markers path::attr(d)").getall()
    )
    return [round(scale * y + min_y) for y in series_y]


def parse(dom: parsel.selector.Selector) -> SimilarwebSite:
    """Parses website pages from Similarweb.

    The function doesn't handle unexpected format.
    It looks up the data where expected and returns the literal strings it finds,
    or empty string if it doesn't find anything.

    Args:
        dom (parsel.selector.Selector): Similarweb page HTML selector.

    Returns:
        SimilarwebSite containing the scraped values.
    """

    def _txt_at(css_selector: str) -> str:
        return dom.css(css_selector + "::text").get(default="")

    def _txt_list_at(css_selector: str) -> List[str]:
        return dom.css(css_selector + "::text").getall()

    def _engagement_overview_item(position: int) -> str:
        return _txt_at(
            "#overview .wa-overview__column--engagement"
            f" .engagement-list__item:nth-child({position})"
            " .engagement-list__item-value"
        )

    return SimilarwebSite(
        domain=_txt_at("#overview .wa-overview__title"),
        date=_txt_at("#overview .wa-overview__text--date"),
        global_rank=_txt_at(
            "#overview .wa-rank-list__item--global .wa-rank-list__value"
        ),
        total_visits=_engagement_overview_item(1),
        bounce_rate=_engagement_overview_item(2),
        avg_visit_duration=_engagement_overview_item(4),
        past_category_ranks=_parse_series_chart_ordinates(
            chart_svg=dom.css("#ranking svg.highcharts-root"),
        ),
        past_total_visits=_txt_list_at("#traffic .wa-traffic__chart-data-label"),
        top_countries=list(
            zip(
                _txt_list_at("#geography .wa-geography__country-name"),
                _txt_list_at("#geography .wa-geography__country-traffic-value"),
            )
        ),
        age_distribution=_txt_list_at("#demographics .wa-demographics__age-data-label"),
    )
