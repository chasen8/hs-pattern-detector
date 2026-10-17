"""Transparent five-pivot baseline; no market data or strategy logic."""
from math import isfinite
from numbers import Real
from typing import Iterable

from .models import Pattern, Pivot


def detect_patterns(
    prices: Iterable[float], *, pivot_window: int = 1,
    shoulder_tolerance: float = 0.25,
    neckline_tolerance: float = 0.30,
    min_head_prominence: float = 0.10,
    max_time_ratio: float = 2.0,
) -> list[Pattern]:
    """Find consecutive alternating five-pivot HS/IHS candidates.

    Price tolerances are fractions of head-to-neckline height, not price.
    Pivots need ``pivot_window`` later observations for confirmation.
    ``confirmed_at`` records when the right shoulder becomes observable;
    it does NOT mean a neckline breakout. See README for exact rules.
    """
    if isinstance(pivot_window, bool) or not isinstance(pivot_window, int):
        raise TypeError("pivot_window must be an integer")
    if pivot_window < 1:
        raise ValueError("pivot_window must be at least 1")
    parameters = {
        "shoulder_tolerance": shoulder_tolerance,
        "neckline_tolerance": neckline_tolerance,
        "min_head_prominence": min_head_prominence,
        "max_time_ratio": max_time_ratio,
    }
    for name, value in parameters.items():
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{name} must be a real number")
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if not 0 <= shoulder_tolerance <= 1 or not 0 <= neckline_tolerance <= 1:
        raise ValueError("shoulder and neckline tolerances must be in [0, 1]")
    if not 0 < min_head_prominence < 1:
        raise ValueError("min_head_prominence must be in (0, 1)")
    if max_time_ratio < 1:
        raise ValueError("max_time_ratio must be at least 1")
    if isinstance(prices, (str, bytes)):
        raise TypeError("prices must be an iterable of real numbers")
    try:
        raw = list(prices)
    except TypeError as exc:
        raise TypeError("prices must be an iterable of real numbers") from exc
    values = []
    for value in raw:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError("each price must be a real number")
        value = float(value)
        if not isfinite(value) or value <= 0:
            raise ValueError("prices must be finite and strictly positive")
        values.append(value)

    pivots: list[tuple[str, Pivot]] = []
    w = pivot_window
    for i in range(w, len(values) - w):
        neighbors = values[i-w:i] + values[i+1:i+w+1]
        kind = "high" if values[i] > max(neighbors) else (
            "low" if values[i] < min(neighbors) else None
        )
        if kind is None:
            continue
        pivot = Pivot(i, values[i])
        if pivots and pivots[-1][0] == kind:
            old = pivots[-1][1]
            if (kind == "high" and pivot.price > old.price) or (
                kind == "low" and pivot.price < old.price
            ):
                pivots[-1] = kind, pivot
        else:
            pivots.append((kind, pivot))

    results = []
    for start in range(len(pivots) - 4):
        group = pivots[start:start+5]
        ls, n1, head, n2, rs = [p for _, p in group]
        sign = 1 if group[0][0] == "high" else -1
        neck = lambda i: n1.price + (n2.price-n1.price) * (i-n1.index)/(n2.index-n1.index)
        height = sign * (head.price - neck(head.index))
        if height <= 0:
            continue
        # Require the head to exceed both shoulders in raw price as well.
        prominence = min(sign*(head.price-ls.price), sign*(head.price-rs.price))/height
        left_height = sign*(ls.price-neck(ls.index))
        right_height = sign*(rs.price-neck(rs.index))
        shoulder_error = abs(left_height-right_height)/height
        neck_error = abs(n1.price-n2.price)/height
        left_time, right_time = head.index-ls.index, rs.index-head.index
        time_ratio = max(left_time, right_time)/min(left_time, right_time)
        if (left_height <= 0 or right_height <= 0
                or prominence < min_head_prominence
                or shoulder_error > shoulder_tolerance
                or neck_error > neckline_tolerance
                or time_ratio > max_time_ratio):
            continue
        # Descriptive geometry only; not calibrated accuracy or probability.
        fit = max(0.0, 1.0 - (shoulder_error + neck_error)/2.0)
        results.append(Pattern(
            "HS" if sign == 1 else "IHS", ls, n1, head, n2, rs,
            rs.index+w, fit,
        ))
    return results
