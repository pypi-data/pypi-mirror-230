from dataclasses import dataclass


@dataclass
class SourceSegment:
    my_id: int
    start: int
    end: int
    frequency: int
    token_length: int
    text: str

    @classmethod
    def from_frequency(cls, my_id, start, end, frequency):
        return cls(my_id, start, end, frequency, 0, '')

    def increment_frequency(self):
        self.frequency += 1

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, SourceSegment):
            return NotImplemented

        return self.my_id == other.my_id
