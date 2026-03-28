"""Game state and hint system."""

from enum import Enum
from dataclasses import dataclass

class HintType(Enum):
    PERFECT_MATCH  = 5
    EXACT_PREFIX   = 4
    PARTIAL_PREFIX = 3
    BALANCING      = 2
    EXPLORATORY    = 1

@dataclass
class Hint:
    idx: int
    score: float
    explanation: str
    htype: HintType