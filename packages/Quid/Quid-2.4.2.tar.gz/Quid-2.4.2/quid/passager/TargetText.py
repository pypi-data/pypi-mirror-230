from dataclasses import dataclass
from typing import List

from quid.passager.TargetLocation import TargetLocation


@dataclass
class TargetText:
    my_id: int
    filename: str
    target_locations: List[TargetLocation]

    def __hash__(self) -> int:  # pragma: no cover
        return hash((self.my_id, self.filename, hash(self.target_locations)))

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, TargetText):
            return NotImplemented

        return self.my_id == other.my_id
