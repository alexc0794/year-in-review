from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import utc_timestamp_to_datetime


@dataclass
class Stream:
    end_time: datetime
    artist_name: str
    track_name: str
    duration_milliseconds: int

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Stream':
        return Stream(
            end_time=utc_timestamp_to_datetime(data['endTime']),
            artist_name=data['artistName'],
            track_name=data['trackName'],
            duration_milliseconds=data['msPlayed']
        )

    @property
    def skipped(self) -> bool:
        return self.duration_milliseconds < 10000  # Is determined to be skipped if listened to less than 10 seconds
