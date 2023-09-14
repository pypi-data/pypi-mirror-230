from dataclasses import dataclass


@dataclass
class TargetTextLocationLink:
    target_text_id: int
    location_id: int
    source_segment_start_id: int
    source_segment_end_id: int
