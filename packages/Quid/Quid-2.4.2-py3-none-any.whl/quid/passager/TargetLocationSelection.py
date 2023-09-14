from dataclasses import dataclass
from typing import List


@dataclass
class TargetLocationSelection:
    target_text_id: int
    target_location_ids: List[int]

    @classmethod
    def from_value(cls, target_text_id, target_location_id):  # pragma: no cover
        return cls(target_text_id, [target_location_id])

    def add_target_location_id(self, target_location_id):
        if target_location_id not in self.target_location_ids:
            self.target_location_ids.append(target_location_id)
