
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Tuple


ALPHABET: Tuple[str, ...] = ("R", "G", "B")


@dataclass(frozen=True)
class Domino:
    top: str
    bottom: str

    def key(self) -> tuple[str, str]:
        return (self.top, self.bottom)


@dataclass(frozen=True)
class GeneratedInstance:
    source_string: str
    top_lengths: list[int]
    bottom_lengths: list[int]
    top_segments: list[str]
    bottom_segments: list[str]
    dominoes: list[Domino]


def generate_source_string(length: int, alphabet: Tuple[str, ...] = ALPHABET) -> str:
    if length <= 0:
        raise ValueError("length must be greater than 0")

    return "".join(random.choice(alphabet) for _ in range(length))


def generate_partition(
    *,
    part_count: int,
    total_length: int,
    min_segment_length: int,
    max_segment_length: int,
) -> list[int]:
    if part_count <= 0:
        raise ValueError("part_count must be greater than 0")

    if min_segment_length <= 0:
        raise ValueError("min_segment_length must be greater than 0")

    if max_segment_length < min_segment_length:
        raise ValueError("max_segment_length must be greater than or equal to min_segment_length")

    minimum_total = part_count * min_segment_length
    maximum_total = part_count * max_segment_length

    if total_length < minimum_total or total_length > maximum_total:
        raise ValueError("total_length is not possible for the provided segment bounds and part count")

    partition = [min_segment_length for _ in range(part_count)]
    remaining = total_length - minimum_total

    while remaining > 0:
        candidate_indexes = [
            index for index, value in enumerate(partition) if value < max_segment_length
        ]
        if not candidate_indexes:
            break

        index = random.choice(candidate_indexes)
        partition[index] += 1
        remaining -= 1

    return partition


def slice_string_by_lengths(source_string: str, lengths: list[int]) -> list[str]:
    segments: list[str] = []
    cursor = 0

    for length in lengths:
        next_cursor = cursor + length
        segment = source_string[cursor:next_cursor]
        segments.append(segment)
        cursor = next_cursor

    if cursor != len(source_string):
        raise ValueError("lengths do not consume the full source_string")

    return segments


def generate_structured_instance(
    *,
    string_length: int,
    array_length: int,
    min_segment_length: int,
    max_segment_length: int,
    alphabet: Tuple[str, ...] = ALPHABET,
) -> GeneratedInstance:
    if string_length <= 0:
        raise ValueError("string_length must be greater than 0")

    source_string = generate_source_string(length=string_length, alphabet=alphabet)

    top_lengths = generate_partition(
        part_count=array_length,
        total_length=string_length,
        min_segment_length=min_segment_length,
        max_segment_length=max_segment_length,
    )
    bottom_lengths = generate_partition(
        part_count=array_length,
        total_length=string_length,
        min_segment_length=min_segment_length,
        max_segment_length=max_segment_length,
    )

    top_segments = slice_string_by_lengths(source_string, top_lengths)
    bottom_segments = slice_string_by_lengths(source_string, bottom_lengths)

    dominoes = [
        Domino(top=top_segments[index], bottom=bottom_segments[index])
        for index in range(array_length)
    ]

    return GeneratedInstance(
        source_string=source_string,
        top_lengths=top_lengths,
        bottom_lengths=bottom_lengths,
        top_segments=top_segments,
        bottom_segments=bottom_segments,
        dominoes=dominoes,
    )