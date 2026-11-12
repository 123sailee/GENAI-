
from dataclasses import dataclass, field


@dataclass
class Record:
    id: int
    place: str
    district: str
    category: str
    best_season: str
    how_to_reach: str
    source_url: str
    verified_in_sources: list[str] = field(default_factory=list)
