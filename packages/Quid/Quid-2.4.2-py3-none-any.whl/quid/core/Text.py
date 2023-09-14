from dataclasses import dataclass


@dataclass
class Text:
    tk_start_pos: int
    tk_end_pos: int
