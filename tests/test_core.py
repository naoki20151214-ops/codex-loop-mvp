from datetime import UTC, datetime
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core import format_jst, sqrt


def test_format_jst_converts_aware_datetime() -> None:
    dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)

    assert format_jst(dt) == "2024-01-01 09:00:00 JST"


def test_format_jst_treats_naive_as_utc() -> None:
    dt = datetime(2024, 1, 1, 0, 0, 0)

    assert format_jst(dt) == "2024-01-01 09:00:00 JST"


def test_sqrt_of_perfect_square() -> None:
    assert sqrt(9) == 3


def test_sqrt_of_two_is_approximate() -> None:
    assert sqrt(2) == pytest.approx(1.4142, abs=1e-4)


def test_sqrt_raises_for_negative_values() -> None:
    with pytest.raises(ValueError):
        sqrt(-1)
