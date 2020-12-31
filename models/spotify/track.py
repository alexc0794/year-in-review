from cached_property import cached_property
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from models.spotify.stream import Stream


@dataclass
class Track:
    name: str
    streams: List[Stream]

    @cached_property
    def streamed_duration_seconds(self) -> int:
        milliseconds = sum([stream.duration_milliseconds for stream in self.streams])
        return int(round(milliseconds / 1000, 0))

    def __str__(self) -> str:
        return self.name
