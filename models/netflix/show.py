from dataclasses import dataclass
from typing import List
from models.netflix.view import View

@dataclass
class Show:
    title: str
    views: List[View]

    @property
    def duration_seconds(self) -> int:
        return sum([view.duration_seconds for view in self.views])

    @property
    def duration_hours(self) -> float:
        return round(self.duration_seconds / 60 / 60, 2)
