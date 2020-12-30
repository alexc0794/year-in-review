import pytz
from dataclasses import dataclass
from dateutil.parser import parse
from datetime import datetime
from tzlocal import get_localzone
from typing import Dict, Any


@dataclass
class Chat:
    body: str
    date: datetime

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Chat':
        date = parse(data["timestamp"])
        utc = pytz.timezone('UTC')
        date = utc.localize(date)
        date = date.astimezone(get_localzone())
        return Chat(
            body=data["body"],
            date=date,
        )

    def __str__(self) -> str:
        return str(self.body)
