
from dataclasses import dataclass


@dataclass
class Record:
    id: int
    place: str
    district: str
    category: str
    best_season: str
    how_to_reach: str
    source_url: str
