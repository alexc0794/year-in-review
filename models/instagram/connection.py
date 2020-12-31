from dataclasses import dataclass
from datetime import datetime
from dataclasses import dataclass
from cached_property import cached_property
from models import utc_timestamp_to_datetime


@dataclass
class Connection:
    name: str
    date: datetime

    def __init__(self, name: str, timestamp: str) -> None:
        self.name = name
        self.date = utc_timestamp_to_datetime(timestamp=timestamp)
