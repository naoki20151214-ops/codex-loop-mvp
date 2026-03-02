from datetime import UTC, datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core import format_jst


def test_format_jst_converts_aware_datetime() -> None:
    dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)

    assert format_jst(dt) == "2024-01-01 09:00:00 JST"


def test_format_jst_treats_naive_as_utc() -> None:
    dt = datetime(2024, 1, 1, 0, 0, 0)

    assert format_jst(dt) == "2024-01-01 09:00:00 JST"
