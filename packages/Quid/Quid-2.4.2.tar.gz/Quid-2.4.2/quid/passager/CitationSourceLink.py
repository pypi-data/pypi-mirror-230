from dataclasses import dataclass
from typing import List
from quid.passager.TargetLocationSelection import TargetLocationSelection


@dataclass
class CitationSourceLink:
    citation_source_id: int
    target_location_selections: List[TargetLocationSelection]
