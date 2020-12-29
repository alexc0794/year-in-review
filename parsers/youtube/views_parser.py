import json
import os
from cached_property import cached_property
from typing import Dict, Any, List, Optional
from models.youtube.view import View
from models.youtube.channel import Channel


class ViewsParser:
    year: Optional[int]
    views_data: List[Dict[str, Any]]

    def __init__(self, year: Optional[int]=None) -> None:
        self.year = year
        filepath = "{0}/data/Takeout/YouTube and YouTube Music/history/watch-history.json".format(os.getcwd())

        try:
            with open(filepath) as file:
                self.views_data = json.load(file)
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise

    @cached_property
    def views(self) -> List[View]:
        views = []
        for view_data in self.views_data:
            view = View.from_json(data=view_data)
            if not view.url:
                continue
            if not view.channel_name:
                continue
            if self.year is not None and view.date.year != self.year:
                continue
            views.append(view)
        return views

    @cached_property
    def channels(self) -> List[Channel]:
        map = {}
        for view in self.views:
            if not view.channel_name:
                continue
            map[view.channel_name] = map.get(view.channel_name, []) + [view]

        channels = []
        for channel_name in list(map.keys()):
            channels.append(Channel(name=channel_name, views=map[channel_name]))

        return channels

    def get_most_viewed_channels_by_count(self) -> List[Channel]:
        channels = self.channels
        channels.sort(key=lambda channel: len(channel.views), reverse=True)
        return channels[:10]

    def get_views_by_weekday(self) -> List[List[View]]:
        views_by_weekday = [[] for _ in range(7)]
        for view in self.views:
            views_by_weekday[view.date.weekday()].append(view)
        return views_by_weekday

    def get_views_by_month(self) -> List[List[View]]:
        views_by_month = [[] for _ in range(12)]
        for view in self.views:
            views_by_month[view.date.month - 1].append(view)
        return views_by_month

    def get_channels_by_month(self) -> List[List[Channel]]:
        channels_by_month = [[] for _ in range(12)]
        views_by_month = self.get_views_by_month()
        for month in range(12):
            views = views_by_month[month]
            map = {}
            for view in views_by_month[month]:
                if not view.channel_name:
                    continue
                name = view.channel_name
                map[name] = map.get(name, []) + [view]
            channels = []
            for channel_name in list(map.keys()):
                channel_views = map[channel_name]
                if len(channel_views) <= 1:
                    continue
                channels.append(Channel(name=channel_name, views=map[channel_name]))
            channels.sort(key=lambda channel: len(channel.views), reverse=True)
            channels_by_month[month] = channels

        return channels_by_month
