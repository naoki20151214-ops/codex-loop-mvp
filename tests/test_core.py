from datetime import UTC, datetime
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core import calc_risk_amount, format_jst, sqrt


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


def test_calc_risk_amount_for_one_percent() -> None:
    assert calc_risk_amount(100000, 1) == 1000


def test_calc_risk_amount_for_five_percent() -> None:
    assert calc_risk_amount(20000, 5) == 1000


@pytest.mark.parametrize(
    ("balance", "risk_pct"),
    [(-1, 1), (1000, -1), (-100, -1)],
)
def test_calc_risk_amount_raises_for_negative_inputs(
    balance: float, risk_pct: float
) -> None:
    with pytest.raises(ValueError):
        calc_risk_amount(balance, risk_pct)
