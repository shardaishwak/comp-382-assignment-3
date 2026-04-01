import random
import uuid
from typing import Optional

COLORS = ["R", "G", "B"]
MINIMUM_SEQUENCE_LENGTH = 1
MAXIMUM_SEQUENCE_LENGTH = 4
DEFAULT_SIZE = 6\

class Domino:
    def __init__(self, id: int, top: list, bottom: list):
        self.id: int = id
        self.top: list[str] = top
        self.bottom: list[str] = bottom
    
    @property
    def top_str(self) -> str:
        return "".join(self.top)

    @property
    def bottom_str(self) -> str:
        return "".join(self.bottom)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "top": self.top,
            "bottom": self.bottom
        }
    
    def __repr__(self):
        return f"Domino(id={self.id}, top={self.top}, bottom={self.bottom})"
    

class PlacedDomino:
    def __init__(self, domino: Domino, position: int):
        self.domino: Domino = domino
        self.positionId: str = str(uuid.uuid4())
        self.position: int = position

    def to_dict(self) -> dict:
        return {
        "id": self.domino.id,
        "top": self.domino.top,
        "bottom": self.domino.bottom,
        "placementId": self.positionId,
        "position": self.position
        }
    
    def __repr__(self):
        return f"PlacedDomino(id={self.domino.id}. pos={self.position})"
    
class PCPGameState:
    def __init__(self, set_size: int = DEFAULT_SIZE, seed: Optional[int] = None):
        self._rng = random.Random(seed)
        self.instance: list[Domino] = []
        self.sequence: list[PlacedDomino] = []
        self._top_str: str = ""
        self._bottom_str: str = ""
        self.new_game(set_size)

    @classmethod
    def from_dominoes(cls, dominoes: list["Domino"]) -> "PCPGameState":
        obj = cls.__new__(cls)
        obj._rng = None
        obj.instance = list(dominoes)
        obj.sequence = []
        obj._top_str = ""
        obj._bottom_str = ""
        return obj

    @property
    def is_solved(self) -> bool:
        return bool(self._top_str) and self._top_str == self._bottom_str
    
    @property
    def prefixMatch(self) -> int:
        count = 0
        for a, b in zip(self._top_str, self._bottom_str):
            if a == b:
                count += 1
            else:
                break
        return count
    
    @property
    def validNextIds(self) -> list:
        valid = []
        for domino in self.instance:
            new_top_str = self._top_str + domino.top_str
            new_bottom_str = self._bottom_str + domino.bottom_str
            if self._is_compatible(new_top_str, new_bottom_str):
                valid.append(domino.id)
        return valid
    
    @property
    def isDeadEnd(self) -> bool:
        return len(self.validNextIds) == 0 and not self.is_solved
    
    def place_domino(self,domino_id: int) -> PlacedDomino:
        if self.is_solved:
            raise RuntimeError("Puzzle already solved, call reset() or new_game() to start a new game.")
        
        domino = self._get_domino(domino_id)
        tile = PlacedDomino(domino=domino, position = len(self.sequence))
        self.sequence.append(tile)
        self._top_str += domino.top_str
        self._bottom_str += domino.bottom_str
        return tile
    
    def undo(self) -> Optional[PlacedDomino]:
        if not self.sequence:
            return None
        tile = self.sequence.pop()
        self._top_str = "".join(t.domino.top_str for t in self.sequence)
        self._bottom_str = "".join(t.domino.bottom_str for t in self.sequence)
        return tile
    
    def reset(self):
        self.sequence = []
        self._top_str = ""
        self._bottom_str = ""
    
    def new_game(self, set_size: int = DEFAULT_SIZE) -> None:
        if set_size < 1:
            raise ValueError("set_size must be at least 1.")
        self.instance = self._generate_instance(set_size)
        self.reset()

    def snapshot(self) -> dict:
        return {
            "instance": [d.to_dict() for d in self.instance],
            "sequence": [t.to_dict() for t in self.sequence],
            "topString": self._top_str,
            "bottomString": self._bottom_str,
            "isSolved": self.is_solved,
            "validNextIds": self.validNextIds,
            "isDeadEnd": self.isDeadEnd,
            "prefixMatch": self.prefixMatch,
        }
    def _generate_instance(self, set_size: int) -> list:
        seen = set()
        result = []
        max_attempts = set_size * 2000

        for _ in range(max_attempts):
            if len(result) == set_size:
                break
            tl = self._rng.randint(MINIMUM_SEQUENCE_LENGTH, MAXIMUM_SEQUENCE_LENGTH)
            bl = self._rng.randint(MINIMUM_SEQUENCE_LENGTH, MAXIMUM_SEQUENCE_LENGTH)
            top = [self._rng.choice(COLORS) for _ in range(tl)]
            bottom = [self._rng.choice(COLORS) for _ in range(bl)]
            key = (tuple(top), tuple(bottom))

            if key in seen or top == bottom:
                continue

            seen.add(key)
            result.append(Domino(id=len(result), top=top, bottom=bottom))

        if len(result) < set_size:
            raise RuntimeError(f"Could not generate enough unique dominoes.")
        return result
    
    def _get_domino(self, domino_id: int) -> Domino:
        for d in self.instance:
            if d.id == domino_id:
                return d
        raise ValueError(
            f"Domino with id {domino_id} not found in the current instance."
            f"valid ids: {[d.id for d in self.instance]}"
        )
    
    @staticmethod
    def _is_compatible(top: str, bot: str) -> bool:
        n = min(len(top), len(bot))
        return top[:n] == bot[:n]
    
    def __repr__(self):
        return (
            f"PCPGameState("
            f"set_size={len(self.instance)}, "
            f"moves={len(self.sequence)}, "
            f"solved={self.is_solved}, -"
        )

def _demo():
    SEP = "=" * 56
    print (SEP)
    print ("PCP Game State Manager - example demonstration")
    print (SEP)

    gs = PCPGameState.__new__(PCPGameState)
    gs._rng = None
    gs.sequence = []
    gs._top_str = ""
    gs._bottom_str = ""
    gs.instance = [
        Domino(id=0, top=["R"], bottom=["R","G"]),
        Domino(id=1, top=["G"], bottom=["G", "R"]),
        Domino(id=2, top=["G","R"], bottom=["R"]),
        Domino(id=3, top=["R","G","B"], bottom=["B"]),
    ]

    print ("\n instance (domino set):")
    for d in gs.instance:
        print(f"    id={d.id}  top={''.join(d.top):<6}  bot={''.join(d.bottom)}")
    
    solution = [0, 1, 2, 0, 3]

    print (f"\napplying solution sequence: {solution}")
    print (f"{'move':<6} {'domino':<8} {'topString':<12} {'bottomString':<12} {'prefixMatch':<12} {'isSolved'}")
    print ("" + "-" * 60 )

    for domino_id in solution:
        gs.place_domino(domino_id)
        snap = gs.snapshot()
        print (
            f" place ({domino_id})"
            f" id={domino_id:<5} "
            f" top = {snap['topString']:<12} "
            f" bot = {snap['bottomString']:<12} "
            f" prefixMatch={snap['prefixMatch']:<6} "
            f" solved={snap['isSolved']}"
        )
    
    print (f"\n Final topString: {gs._top_str}")
    print (f" Final bottomString: {gs._bottom_str}")
    print (f" Puzzle solved: {gs.is_solved}")
    assert gs._top_str == "RGGRRRGB", f"top mismatch: {gs._top_str}"
    assert gs._bottom_str == "RGGRRRGB", f"bottom mismatch: {gs._bottom_str}"
    assert gs.is_solved == True
    print ("\n top == bottom == RGGRRRGB -> Solution is correct!")

    print (f"\n{SEP}")

if __name__ == "__main__":
    _demo()




class GeneratedStructuredInstance:
    def __init__(
        self,
        source_string: str,
        top_lengths: list[int],
        bottom_lengths: list[int],
        top_segments: list[str],
        bottom_segments: list[str],
        dominoes: list[Domino],
    ):
        self.source_string = source_string
        self.top_lengths = top_lengths
        self.bottom_lengths = bottom_lengths
        self.top_segments = top_segments
        self.bottom_segments = bottom_segments
        self.dominoes = dominoes


def generate_source_string(length: int, alphabet: tuple[str, ...] = tuple(COLORS)) -> str:
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
    alphabet: tuple[str, ...] = tuple(COLORS),
) -> GeneratedStructuredInstance:
    if string_length <= 0:
        raise ValueError("string_length must be greater than 0")

    source_string = generate_source_string(length=string_length, alphabet=alphabet)

    # Regenerate partitions until no single domino has top == bottom
    # (a self-solving domino makes the puzzle trivial)
    for _ in range(200):
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

        if all(top_segments[i] != bottom_segments[i] for i in range(array_length)):
            break

    dominoes = [
        Domino(
            id=index,
            top=list(top_segments[index]),
            bottom=list(bottom_segments[index]),
        )
        for index in range(array_length)
    ]

    return GeneratedStructuredInstance(
        source_string=source_string,
        top_lengths=top_lengths,
        bottom_lengths=bottom_lengths,
        top_segments=top_segments,
        bottom_segments=bottom_segments,
        dominoes=dominoes,
    )