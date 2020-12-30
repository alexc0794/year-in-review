import pytz
from dataclasses import dataclass
from dateutil.parser import parse
from datetime import datetime
from tzlocal import get_localzone
from dataclasses import dataclass
from statistics import median
from cached_property import cached_property
from typing import Dict, Any, List, Optional
from models.hinge.chat import Chat


@dataclass
class Match:
    liked: bool
    blocked: bool
    match_made: bool
    date: datetime
    chats: List[Chat]

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Match':
        liked = "like" in data
        blocked = "block" in data
        match_made = "match" in data

        date = None
        if "match" in data and len(data["match"]) > 0 and "timestamp" in data["match"][0]:
            date = parse(data["match"][0]["timestamp"])

        if not date and "block" in data and len(data["block"]) > 0 and "timestamp" in data["block"][0]:
            date = parse(data["block"][0]["timestamp"])

        if not date and "like" in data and len(data["like"]) > 0 and "timestamp" in data["like"][0]:
            date = parse(data["like"][0]["timestamp"])

        if date is None:
            raise

        utc = pytz.timezone('UTC')
        date = utc.localize(date)
        date = date.astimezone(get_localzone())

        return Match(
            liked=liked,
            blocked=blocked,
            match_made=match_made,
            date=date,
            chats=[Chat.from_json(data=chat_data) for chat_data in data.get('chats', [])],
        )

    @property
    def like_accepted(self) -> bool:
        """
        User sent a like and got a match
        """
        return self.liked and self.match_made

    @property
    def like_rejected(self) -> bool:
        """
        User sent a like and did not get a match
        """
        return self.liked and not self.match_made

    @property
    def user_accepted(self) -> bool:
        """
        User received a like and accepted the match
        """
        return not self.liked and self.match_made

    @property
    def user_rejected(self) -> bool:
        """
        User received a like but rejected the match
        """
        return not self.match_made and self.blocked

    @property
    def accepted(self) -> bool:
        return self.like_accepted or self.user_accepted

    @property
    def ghosted(self) -> bool:
        return NotImplemented()  # TODO

    @property
    def chatted(self) -> bool:
        return bool(self.chats)

    @property
    def chat_duration_seconds(self) -> Optional[int]:
        """
        Difference in time between your first and last sent message
        """
        if len(self.chats) < 2:
            return None

        first_chat = self.chats[0]
        last_chat = self.chats[-1]
        difference = last_chat.date - first_chat.date
        return difference.total_seconds()

    def get_frequency_by_hour(self) -> List[int]:
        frequency = [0]*24
        for chat in self.chats:
            frequency[chat.date.hour] += 1

        assert len(frequency) == 24
        return frequency

    def get_frequency_by_weekday(self) -> List[int]:
        frequency = [0]*7
        for chat in self.chats:
            frequency[chat.date.weekday()] += 1
        return frequency
