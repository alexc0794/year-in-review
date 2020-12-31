import json
import os
from cached_property import cached_property
from typing import Dict, Any, List, Optional
from models.instagram.connection import Connection


class ConnectionsParser:
    year: Optional[int]
    connections_data: Dict[str, Any]

    def __init__(self, year: Optional[int]=None) -> None:
        self.year = year
        filepath = "{0}/data/instagram/connections.json".format(os.getcwd())

        try:
            with open(filepath) as file:
                self.connections_data = json.load(file)
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise

    @cached_property
    def followers(self) -> List[Connection]:
        followers_data = self.connections_data["followers"]
        connections = [Connection(name=name, timestamp=followers_data[name]) for name in list(followers_data.keys())]
        if self.year:
            return [connection for connection in connections if connection.date.year == self.year]
        return connections

    @cached_property
    def following(self) -> List[Connection]:
        following_data = self.connections_data["following"]
        connections = [Connection(name=name, timestamp=following_data[name]) for name in list(following_data.keys())]
        if self.year:
            return [connection for connection in connections if connection.date.year == self.year]
        return connections

    def get_followers_by_month(self) -> List[List[Connection]]:
        connections_by_month = [[] for _ in range(12)]
        for connection in self.followers:
            connections_by_month[connection.date.month - 1].append(connection)
        return connections_by_month

    def get_following_by_month(self) -> List[List[Connection]]:
        connections_by_month = [[] for _ in range(12)]
        for connection in self.following:
            connections_by_month[connection.date.month - 1].append(connection)
        return connections_by_month
