import json
import os
from cached_property import cached_property
from typing import Dict, Any, List, Optional
from models.instagram.like import Like


class LikesParser:
    year: Optional[int]
    likes_data: Dict[str, Any]

    def __init__(self, year: Optional[int]=None) -> None:
        self.year = year
        filepath = "{0}/data/instagram/likes.json".format(os.getcwd())

        try:
            with open(filepath) as file:
                self.likes_data = json.load(file)
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise

    @cached_property
    def likes(self) -> None:
        likes = [Like(name=like_data[1], timestamp=like_data[0]) for like_data in self.likes_data["media_likes"]]
        if self.year:
            return [like for like in likes if like.date.year == self.year]
        return likes
