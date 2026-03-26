
from __future__ import annotations

from dataclasses import dataclass, field

from domino import Domino, generate_unique_dominoes


def _domino_sort_key(domino: Domino) -> tuple[int, int, str, str]:
    return (
        len(domino.top) + len(domino.bottom),
        len(domino.top),
        domino.top,
        domino.bottom,
    )


@dataclass
class GameState:
    available_dominoes: list[Domino] = field(default_factory=list)
    working_sequence: list[Domino] = field(default_factory=list)

    @property
    def top_string(self) -> str:
        return "".join(domino.top for domino in self.working_sequence)

    @property
    def bottom_string(self) -> str:
        return "".join(domino.bottom for domino in self.working_sequence)

    def reset_with_random_dominoes(self, count: int) -> None:
        generated = generate_unique_dominoes(count)
        self.available_dominoes = sorted(generated, key=_domino_sort_key)
        self.working_sequence = []

    def append_to_working_sequence(self, domino: Domino) -> None:
        if domino not in self.available_dominoes:
            return

        self.available_dominoes.remove(domino)
        self.working_sequence.append(domino)

    def remove_from_working_sequence(self, index: int) -> None:
        if index < 0 or index >= len(self.working_sequence):
            return

        domino = self.working_sequence.pop(index)
        self.available_dominoes.append(domino)
        self.available_dominoes.sort(key=_domino_sort_key)