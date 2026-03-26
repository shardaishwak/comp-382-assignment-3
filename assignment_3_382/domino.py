
from __future__ import annotations

from dataclasses import dataclass
import random


ALPHABET = ("R", "G", "B")


@dataclass(frozen=True)
class Domino:
    top: str
    bottom: str

    def key(self) -> tuple[str, str]:
        return (self.top, self.bottom)


def generate_random_string(min_length: int = 1, max_length: int = 3) -> str:
    length = random.randint(min_length, max_length)
    return "".join(random.choice(ALPHABET) for _ in range(length))


def generate_unique_dominoes(count: int) -> list[Domino]:
    if count <= 0:
        raise ValueError("count must be greater than 0")

    dominoes: list[Domino] = []
    seen: set[tuple[str, str]] = set()

    while len(dominoes) < count:
        top = generate_random_string()
        bottom = generate_random_string()
        candidate = Domino(top=top, bottom=bottom)

        if candidate.key() in seen:
            continue

        seen.add(candidate.key())
        dominoes.append(candidate)

    return dominoes