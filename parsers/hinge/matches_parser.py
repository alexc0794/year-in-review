import os
import csv
import json
import math
import numpy as np
from cached_property import cached_property
from statistics import median
from typing import Dict, Any, List, Optional
from models.hinge.match import Match
from models.hinge.chat import Chat

SECONDS_IN_A_DAY = 86400

def reject_outliers(matches: List[Match], m=10) -> List[bool]:
    """
    This is to filter out extremely long conversations. Lowering m will include more outliers, highering m will exclude.
    """
    chat_lengths: List[int] = [len(match.chats) for match in matches]
    return abs(chat_lengths - np.mean(chat_lengths)) < m * np.std(chat_lengths)


class MatchesParser:
    year: Optional[int]
    matches_data: List[Dict[str, Any]]

    def __init__(self, year: Optional[int] = None) -> None:
        self.year = year
        filepath = '{0}/data/hinge/export/matches.json'.format(os.getcwd())
        try:
            with open(filepath) as file:
                self.matches_data = json.load(file)
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise

    @cached_property
    def matches(self) -> List[Match]:
        matches = [Match.from_json(data=match_data) for match_data in self.matches_data]
        if self.year:
            return [match for match in matches if match.date.year == self.year]
        return matches

    @property
    def like_accepted_matches(self) -> List[Match]:
        return [match for match in self.matches if match.like_accepted]

    @property
    def like_rejected_matches(self) -> List[Match]:
        return [match for match in self.matches if match.like_rejected]

    @property
    def user_accepted_matches(self) -> List[Match]:
        return [match for match in self.matches if match.user_accepted]

    @property
    def user_rejected_matches(self) -> List[Match]:
        return [match for match in self.matches if match.user_rejected]

    @property
    def no_chat_matches(self) -> List[Match]:
        return [match for match in self.matches if match.accepted and not match.chatted]

    @property
    def chatted_matches(self) -> List[Match]:
        return [match for match in self.matches if match.chatted]

    @property
    def chat_durations_seconds(self) -> List[int]:
        return [match.chat_duration_seconds for match in self.matches if match.chat_duration_seconds]

    def get_chat_lengths(self, exclude_empty_chats: bool=True) -> List[int]:
        if exclude_empty_chats:
            return [len(match.chats) for match in self.matches if len(match.chats) > 0]
        return [len(match.chats) for match in self.matches]

    def get_average_days_between_first_and_last_chat(self) -> float:
        return round(sum(self.chat_durations_seconds) / len(self.chat_durations_seconds) / SECONDS_IN_A_DAY, 2)

    def get_median_days_between_first_and_last_chat(self) -> float:
        return round(median(self.chat_durations_seconds) / SECONDS_IN_A_DAY, 2)

    def get_seconds_between_chats(self) -> List[int]:
        duration_seconds: List[int] = []
        for match in self.matches:
            for i in range(1, len(match.chats)):
                first_chat = match.chats[i-1]
                second_chat = match.chats[i]
                duration_seconds.append((second_chat.date - first_chat.date).total_seconds())
        return duration_seconds

    def get_average_seconds_between_chats(self) -> float:
        duration_seconds = self.get_seconds_between_chats()
        return math.ceil(sum(duration_seconds) / len(duration_seconds))

    def get_median_seconds_between_chats(self) -> float:
        duration_seconds = self.get_seconds_between_chats()
        return median(duration_seconds)

    def get_average_chats_sent(self, exclude_empty_chats: bool=True) -> float:
        chat_lengths = self.get_chat_lengths(exclude_empty_chats=exclude_empty_chats)
        return round(sum(chat_lengths) / len(chat_lengths), 0)

    def get_median_chats_sent(self, exclude_empty_chats: bool=True) -> float:
        chat_lengths = self.get_chat_lengths(exclude_empty_chats=exclude_empty_chats)
        return median(chat_lengths)

    def get_matches_by_weekday(self) -> List[List[Match]]:
        matches_by_weekday = [[] for _ in range(7)]
        for match in self.matches:
            matches_by_weekday[match.date.weekday()].append(match)
        return matches_by_weekday

    def get_matches_by_month(self) -> List[List[Match]]:
        matches_by_month = [[] for _ in range(12)]
        for match in self.matches:
            matches_by_month[match.date.month - 1].append(match)
        return matches_by_month

    def get_chats_by_weekday(self) -> List[List[Chat]]:
        chats_by_weekday = [[] for _ in range(7)]
        validity_map = reject_outliers(self.matches)
        for i in range(len(self.matches)):
            match = self.matches[i]
            if not validity_map[i]:
                continue
            for chat in match.chats:
                chats_by_weekday[chat.date.weekday()].append(chat)
        return chats_by_weekday

    def get_chats_by_month(self) -> List[List[Chat]]:
        chats_by_month = [[] for _ in range(12)]
        for match in self.matches:
            for chat in match.chats:
                chats_by_month[chat.date.month - 1].append(chat)
        return chats_by_month

    def print(self) -> None:
        print("Likes sent that were accepted: {0}".format(len(self.like_accepted_matches)))
        print("Likes sent that were ignored or rejected: {0}".format(len(self.like_rejected_matches)))
        print("Others acceptance rate of you {0}%".format(round(100 * len(self.like_accepted_matches) / (len(self.like_accepted_matches) + len(self.like_rejected_matches)), 1)))
        print("Likes received that you accepted: {0}".format(len(self.user_accepted_matches)))
        print("Likes received that you rejected: {0}".format(len(self.user_rejected_matches)))
        print("Your acceptance rate {0}%".format(round(100 * len(self.user_accepted_matches) / (len(self.user_accepted_matches) + len(self.user_rejected_matches)), 1)))
        print("Matches with no messages: {0}".format(len(self.no_chat_matches)))
        print("Matches you sent a message to: {0}".format(len(self.chatted_matches)))
        print("Average time between first and last message sent to match: {0} days".format(self.get_average_days_between_first_and_last_chat()))
        print("Median time between first and last message sent to match: {0} days".format(self.get_median_days_between_first_and_last_chat()))
        print("Average time between messages: {0} hours".format(self.get_average_seconds_between_chats() / 60 / 60))
        print("Median time between messages: {0} seconds".format(self.get_median_seconds_between_chats()))
        print("Average chat messages sent to match (excluding ignored chats): {0}".format(self.get_average_chats_sent()))
        print("Median chat messages sent to match (excluding ignored chats): {0}".format(self.get_median_chats_sent()))
