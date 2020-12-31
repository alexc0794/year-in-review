from cached_property import cached_property
from typing import Dict, Any, List, Optional
from parsers import MultiJsonParser
from models.spotify.stream import Stream
from models.spotify.artist import Artist
from models.spotify.track import Track


class StreamingHistoryParser(MultiJsonParser):

    def __init__(self, year: Optional[int]=None) -> None:
        super().__init__(
            relative_path_to_directory='data/spotify/MyData',
            filename_prefix='StreamingHistory',
            year=year,
        )

    @cached_property
    def streams(self) -> List[Stream]:
        streams = []
        for stream_data in self.data:
            stream = Stream.from_json(data=stream_data)
            if self.year and stream.end_time.year != self.year:
                continue
            streams.append(stream)
        return streams

    @cached_property
    def artists(self) -> List[Artist]:
        map = {}
        for stream in self.streams:
            artist_name = stream.artist_name
            map[artist_name] = map.get(artist_name, []) + [stream]

        artists = []
        for artist_name in list(map.keys()):
            artists.append(Artist(name=artist_name, streams=map[artist_name]))

        return artists

    @cached_property
    def tracks(self) -> List[Track]:
        map = {}
        for stream in self.streams:
            track_name = stream.track_name
            map[track_name] = map.get(track_name, []) + [stream]

        tracks = []
        for track_name in list(map.keys()):
            tracks.append(Track(name=track_name, streams=map[track_name]))

        return tracks

    def get_most_streamed_artists_by_duration(self) -> List[Artist]:
        artists = self.artists
        artists.sort(key=lambda artist: artist.streamed_duration_seconds, reverse=True)
        return artists

    def get_most_streamed_tracks_by_duration(self) -> List[Track]:
        tracks = self.tracks
        tracks.sort(key=lambda track: track.streamed_duration_seconds, reverse=True)
        return tracks

    def get_streams_by_month(self) -> List[List[Stream]]:
        streams_by_month = [[] for _ in range(12)]
        for stream in self.streams:
            streams_by_month[stream.end_time.month-1].append(stream)
        return streams_by_month

    def get_stream_duration_by_month(self) -> List[int]:
        streams_by_month = self.get_streams_by_month()
        stream_duration_by_month = [0]*12
        for month in range(12):
            streams = streams_by_month[month]
            stream_duration_by_month[month] = int(round(sum([stream.duration_milliseconds for stream in streams]), 0))

        return stream_duration_by_month

    def get_artists_by_month(self) -> List[List[Artist]]:
        artists_by_month = [[] for _ in range(12)]
        streams_by_month = self.get_streams_by_month()
        for month in range(len(streams_by_month)):
            streams = streams_by_month[month]
            map = {}
            for stream in streams_by_month[month]:
                artist_name = stream.artist_name
                map[artist_name] = map.get(artist_name, []) + [stream]
            artists = []
            for artist_name in list(map.keys()):
                artists.append(Artist(name=artist_name, streams=map[artist_name]))
            artists.sort(key=lambda artist: artist.streamed_duration_seconds, reverse=True)
            artists_by_month[month] = artists

        return artists_by_month

    def get_tracks_by_month(self) -> List[List[Track]]:
        tracks_by_month = [[] for _ in range(12)]
        streams_by_month = self.get_streams_by_month()
        for month in range(len(streams_by_month)):
            streams = streams_by_month[month]
            map = {}
            for stream in streams_by_month[month]:
                track_name = stream.track_name
                map[track_name] = map.get(track_name, []) + [stream]
            tracks = []
            for track_name in list(map.keys()):
                tracks.append(Track(name=track_name, streams=map[track_name]))
            tracks.sort(key=lambda track: track.streamed_duration_seconds, reverse=True)
            tracks_by_month[month] = tracks

        return tracks_by_month
