import pytz
from dataclasses import dataclass
from dateutil.parser import parse
from datetime import datetime
from tzlocal import get_localzone
from typing import Dict, Any, List, Optional


@dataclass
class View:
    title: str
    url: Optional[str]
    date: datetime
    channel_name: Optional[str]

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'View':
        date = parse(data['time'])
        date = date.astimezone(get_localzone())

        subtitles = data.get('subtitles', [])
        return View(
            title=data['title'],
            url=data.get('titleUrl'),
            date=date,
            channel_name=subtitles[0]['name'] if len(subtitles) > 0 else None
        )
