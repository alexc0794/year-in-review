from cached_property import cached_property
from typing import Dict, Any, List, Optional
from parsers import JsonParser
from models.instagram.like import Like


class LikesParser(JsonParser):

    def __init__(self, year: Optional[int]=None) -> None:
        super().__init__(relative_path='data/instagram/likes.json', year=year)

    @cached_property
    def likes(self) -> None:
        likes = [Like(name=like_data[1], timestamp=like_data[0]) for like_data in self.data["media_likes"]]
        if self.year:
            return [like for like in likes if like.date.year == self.year]
        return likes
