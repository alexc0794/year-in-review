import pytz
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from models import utc_timestamp_to_datetime


@dataclass
class Chat:
    body: str
    date: datetime

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Chat':
        return Chat(
            body=data["body"],
            date=utc_timestamp_to_datetime(timestamp=data["timestamp"]),
        )

    def __str__(self) -> str:
        return str(self.body)
