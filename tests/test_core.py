import re

from src.core import greet, today_iso


def test_today_iso_format() -> None:
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", today_iso())


def test_greet_name() -> None:
    assert greet("Naoki") == "Hello, Naoki!"


def test_greet_blank_defaults_to_friend() -> None:
    assert greet("   ") == "Hello, friend!"
