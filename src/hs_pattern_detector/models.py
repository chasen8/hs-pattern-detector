"""Immutable results; indices are zero-based positions in the input."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Pivot:
    index: int
    price: float


@dataclass(frozen=True)
class Pattern:
    pattern_type: Literal["HS", "IHS"]
    left_shoulder: Pivot
    n1: Pivot
    head: Pivot
    n2: Pivot
    right_shoulder: Pivot
    confirmed_at: int
    geometric_fit: float

    @property
    def neckline(self) -> tuple[Pivot, Pivot]:
        return self.n1, self.n2

    def neckline_at(self, index: int) -> float:
        return self.n1.price + (self.n2.price - self.n1.price) * (
            (index - self.n1.index) / (self.n2.index - self.n1.index)
        )
