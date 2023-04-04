"""Tests parsing website pages from Similarweb."""
from pathlib import Path

import parsel.selector

from sweb.model import SimilarwebSite
from sweb.parser import parse, parse_number


def test_parse_number() -> None:
    """Test parsing a number."""
    assert parse_number("10") == 10
    assert parse_number("10,000") == 10000


def test_parse(html_file: Path, similarweb_site: SimilarwebSite) -> None:
    """Tests parsing website pages from Similarweb.

    Args:
        html_file: HTML file for tests.
        similarweb_site: SimilarwebSite data expected for the test HTML file.
    """
    dom = parsel.selector.Selector(text=html_file.read_text())
    assert parse(dom) == similarweb_site
