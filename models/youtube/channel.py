from dataclasses import dataclass
from typing import List
from models.youtube.view import View


@dataclass
class Channel:
    name: str
    views: List[View]

    def __str__(self) -> str:
        return '{0} ({1} views)'.format(self.name, len(self.views))
