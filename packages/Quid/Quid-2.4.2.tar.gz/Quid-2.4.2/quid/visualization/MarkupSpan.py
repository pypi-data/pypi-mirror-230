from dataclasses import dataclass


@dataclass
class MarkupSpan:
    klass: str
    closed: bool = False
    used: bool = False
