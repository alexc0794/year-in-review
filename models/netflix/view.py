from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import utc_timestamp_to_datetime


@dataclass
class View:
    profile: str
    start_time: datetime
    duration_seconds: int
    title: str
    device: str
    supplemental_video_type: Optional[str]

    @property
    def show_title(self) -> Optional[str]:
        colon_index = self.title.find(':')
        if colon_index > 0:
            return self.title[:colon_index]

    @staticmethod
    def from_csv(columns: Dict[str, int], data: List[str]) -> 'View':
        start_time = utc_timestamp_to_datetime(timestamp=data[columns['Start Time']])
        h, m, s = data[columns['Duration']].split(':')
        duration_seconds = int(h) * 3600 + int(m) * 60 + int(s)

        return View(
            profile=data[columns['Profile Name']],
            title=data[columns['Title']],
            device=data[columns['Device Type']],
            supplemental_video_type=data[columns['Supplemental Video Type']] or None,
            start_time=start_time,
            duration_seconds=duration_seconds,
        )
