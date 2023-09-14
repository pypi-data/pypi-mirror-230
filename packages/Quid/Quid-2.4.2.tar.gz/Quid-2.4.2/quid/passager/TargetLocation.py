from dataclasses import dataclass


@dataclass
class TargetLocation:
    my_id: int
    start: int
    end: int
    text: str

    def __hash__(self) -> int:  # pragma: no cover
        return hash((self.my_id, self.start, self.end))

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, TargetLocation):
            return NotImplemented

        return self.my_id == other.my_id
