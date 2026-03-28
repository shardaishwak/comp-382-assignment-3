
from __future__ import annotations

from dataclasses import dataclass

from domino import ALPHABET, GeneratedInstance, generate_structured_instance


MIN_STRING_LENGTH = 1
MAX_STRING_LENGTH = 64

MIN_SEGMENT_LENGTH = 1
MAX_SEGMENT_LENGTH = 12

MIN_ARRAY_LENGTH = 1
MAX_ARRAY_LENGTH = 24

DEFAULT_STRING_LENGTH = 12
DEFAULT_MIN_SEGMENT_LENGTH = 1
DEFAULT_MAX_SEGMENT_LENGTH = 3
DEFAULT_ARRAY_LENGTH = 6


@dataclass
class GameState:
    string_length: int = DEFAULT_STRING_LENGTH
    min_segment_length: int = DEFAULT_MIN_SEGMENT_LENGTH
    max_segment_length: int = DEFAULT_MAX_SEGMENT_LENGTH
    array_length: int = DEFAULT_ARRAY_LENGTH

    generated_instance: GeneratedInstance | None = None
    error_message: str = ""

    @property
    def has_generated(self) -> bool:
        return self.generated_instance is not None

    def clear_output(self) -> None:
        self.generated_instance = None
        self.error_message = ""

    def can_generate(self) -> bool:
        minimum_total = self.array_length * self.min_segment_length
        maximum_total = self.array_length * self.max_segment_length
        return minimum_total <= self.string_length <= maximum_total

    def get_validation_error(self) -> str:
        if self.min_segment_length > self.max_segment_length:
            return "Min segment length cannot be greater than max segment length."

        minimum_total = self.array_length * self.min_segment_length
        maximum_total = self.array_length * self.max_segment_length

        if self.string_length < minimum_total:
            return (
                f"String length is too small. Minimum valid length is {minimum_total} "
                f"for array length {self.array_length} and min segment {self.min_segment_length}."
            )

        if self.string_length > maximum_total:
            return (
                f"String length is too large. Maximum valid length is {maximum_total} "
                f"for array length {self.array_length} and max segment {self.max_segment_length}."
            )

        return ""

    def generate(self) -> None:
        validation_error = self.get_validation_error()
        if validation_error:
            self.generated_instance = None
            self.error_message = validation_error
            return

        self.generated_instance = generate_structured_instance(
            string_length=self.string_length,
            array_length=self.array_length,
            min_segment_length=self.min_segment_length,
            max_segment_length=self.max_segment_length,
            alphabet=ALPHABET,
        )
        self.error_message = ""

    def adjust_string_length(self, delta: int) -> None:
        self.string_length = _clamp(
            self.string_length + delta,
            MIN_STRING_LENGTH,
            MAX_STRING_LENGTH,
        )
        self.error_message = ""

    def adjust_min_segment_length(self, delta: int) -> None:
        self.min_segment_length = _clamp(
            self.min_segment_length + delta,
            MIN_SEGMENT_LENGTH,
            MAX_SEGMENT_LENGTH,
        )
        if self.min_segment_length > self.max_segment_length:
            self.max_segment_length = self.min_segment_length
        self.error_message = ""

    def adjust_max_segment_length(self, delta: int) -> None:
        self.max_segment_length = _clamp(
            self.max_segment_length + delta,
            MIN_SEGMENT_LENGTH,
            MAX_SEGMENT_LENGTH,
        )
        if self.max_segment_length < self.min_segment_length:
            self.min_segment_length = self.max_segment_length
        self.error_message = ""

    def adjust_array_length(self, delta: int) -> None:
        self.array_length = _clamp(
            self.array_length + delta,
            MIN_ARRAY_LENGTH,
            MAX_ARRAY_LENGTH,
        )
        self.error_message = ""

    @property
    def source_string(self) -> str:
        if self.generated_instance is None:
            return ""

        return self.generated_instance.source_string

    @property
    def top_lengths(self) -> list[int]:
        if self.generated_instance is None:
            return []

        return self.generated_instance.top_lengths

    @property
    def bottom_lengths(self) -> list[int]:
        if self.generated_instance is None:
            return []

        return self.generated_instance.bottom_lengths

    @property
    def top_segments(self) -> list[str]:
        if self.generated_instance is None:
            return []

        return self.generated_instance.top_segments

    @property
    def bottom_segments(self) -> list[str]:
        if self.generated_instance is None:
            return []

        return self.generated_instance.bottom_segments

    @property
    def dominoes(self) -> list:
        if self.generated_instance is None:
            return []

        return self.generated_instance.dominoes


def _clamp(value: int, minimum: int, maximum: int) -> int:
    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value