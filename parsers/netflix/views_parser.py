import os
import csv
import math
from cached_property import cached_property
from dateutil.parser import parse
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple
from models.netflix.view import View
from models.netflix.show import Show

FIVE_MINUTES_IN_SECONDS = 10 * 60
DEFAULT_SHOW_TITLE = 'Other (i.e. Movie)'

class ViewsParser:
    profile: Optional[str]
    year: Optional[int]
    views_columns: List[str]
    views_data: List[List[str]]

    def __init__(self, profile: Optional[str] = None, year: Optional[int] = None) -> None:
        self.profile = profile
        self.year = year
        filepath = '{0}/data/netflix-report/Content_Interaction/ViewingActivity.csv'.format(os.getcwd())

        try:
            with open(filepath) as file:
                views_data = list(csv.reader(file, delimiter=','))
                self.views_columns = views_data[0]
                self.views_data = views_data[1:]
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise

    @property
    def columns_to_index_map(self) -> Dict[str, int]:
        map = {}
        for i in range(len(self.views_columns)):
            column_name = self.views_columns[i]
            map[column_name] = i
        return map

    @cached_property
    def views(self) -> List[View]:
        views = []
        for view_data in self.views_data:
            views.append(View.from_csv(columns=self.columns_to_index_map, data=view_data))

        views = [view for view in views if not view.supplemental_video_type and view.duration_seconds > FIVE_MINUTES_IN_SECONDS]
        if self.profile:
            views = [view for view in views if view.profile == self.profile]
        if self.year:
            views = [view for view in views if view.start_time.year == self.year]
        return views

    @cached_property
    def shows(self) -> List[Show]:
        map = {}
        for view in self.views:
            title = view.show_title or DEFAULT_SHOW_TITLE
            map[title] = map.get(title, []) + [view]

        shows = []
        for show_title in list(map.keys()):
            shows.append(Show(title=show_title, views=map[show_title]))

        return shows

    def get_most_viewed_shows_by_duration_seconds(self) -> List[Show]:
        shows = self.shows
        shows.sort(key=lambda show: show.duration_seconds, reverse=True)
        return shows

    def get_view_duration_seconds(self) -> int:
        return sum([view.duration_seconds for view in self.views])

    def get_views_by_weekday(self) -> List[List[View]]:
        views_by_weekday = [[] for _ in range(7)]
        for view in self.views:
            views_by_weekday[view.start_time.weekday()].append(view)
        return views_by_weekday

    def get_view_duration_by_weekday(self) -> List[int]:
        views_by_weekday = self.get_views_by_weekday()
        view_duration_by_weekday = [0]*7
        for weekday in range(7):
            views = views_by_weekday[weekday]
            view_duration_by_weekday[weekday] = sum([view.duration_seconds for view in views])

        return view_duration_by_weekday

    def get_views_by_month(self) -> List[List[View]]:
        """
        Index 0 represents January, 11 represents December
        """
        views_by_month = [[] for _ in range(12)]
        for view in self.views:
            views_by_month[view.start_time.month-1].append(view)
        return views_by_month

    def get_view_duration_by_month(self) -> List[int]:
        views_by_month = self.get_views_by_month()
        view_duration_by_month = [0]*12
        for month in range(12):
            views = views_by_month[month]
            view_duration_by_month[month] = sum([view.duration_seconds for view in views])

        return view_duration_by_month

    def get_shows_by_month(self) -> List[List[Show]]:
        shows_by_month = [[] for _ in range(12)]
        views_by_month = self.get_views_by_month()
        for month in range(len(views_by_month)):
            views = views_by_month[month]
            map = {}
            for view in views_by_month[month]:
                title = view.show_title or DEFAULT_SHOW_TITLE
                map[title] = map.get(title, []) + [view]
            shows = []
            for show_title in list(map.keys()):
                shows.append(Show(title=show_title, views=map[show_title]))
            shows.sort(key=lambda show: show.duration_seconds, reverse=True)
            shows_by_month[month] = shows

        return shows_by_month
