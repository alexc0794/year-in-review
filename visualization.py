import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional
from dash.dependencies import Input, Output
from constants import WEEKDAYS, MONTHS
from models.hinge.match import Match
from parsers.youtube.views_parser import ViewsParser as YoutubeViewsParser
from parsers.netflix.views_parser import ViewsParser as NetflixViewsParser
from parsers.hinge.matches_parser import MatchesParser as HingeMatchesParser
from parsers.instagram.connections_parser import ConnectionsParser as InstagramConnectionsParser
from parsers.instagram.likes_parser import LikesParser as InstagramLikesParser
from parsers.spotify.streaming_history_parser import StreamingHistoryParser as SpotifyStreamingHistoryParser


PRODUCTS = ['YouTube', 'Netflix', 'Hinge', 'Instagram', 'Spotify']

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(className='page', children=[
    html.Div(className='year-dropdown-wrapper', children=[
        dcc.Dropdown(
            className='year-dropdown',
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in range(2016,2021)],
            placeholder='Select Year...',
            value=2020,
        ),
    ]),
    dcc.Tabs(
        id='tabs',
        value='Spotify-tab',
        className='tab',
        children=[dcc.Tab(label=product, value='{0}-tab'.format(product)) for product in PRODUCTS]
    ),
    html.Div(id='tabs-content'),
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render(tab):
    if tab == 'Netflix-tab':
        return html.Div(className='tab-content', children=[
            html.Div(className='input-wrapper', children=[
                dcc.Input(
                    id='Netflix-profile-input',
                    debounce=True,
                    name='profile',
                    className='input',
                    placeholder='Profile'
                ),
                # html.Label(htmlFor='profile', className='input-label', children='Profile')
            ]),
            html.H1(id='Netflix-total-hours'),
            html.Div(className='tab-content-list', children=[
                html.H2(children='Most Watched TV Shows', className='list-title'),
                html.Ol(id='Netflix-top-tv-shows', className='list', children='Loading...'),
            ]),
            html.Div(className='tab-content-grid', children=[
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Hours Watched per Weekday', className='chart-title'),
                    dcc.Graph(id='Netflix-weekday-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Hours Watched by Month', className='chart-title'),
                    dcc.Graph(id='Netflix-month-bar-chart')
                ]),
            ]),
        ]),
    elif tab == 'YouTube-tab':
        return html.Div(className='tab-content', children=[
            html.Div(className='tab-content-grid', children=[
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Videos Viewed per Weekday', className='chart-title'),
                    dcc.Graph(id='YouTube-weekday-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Channels Viewed by Month', className='chart-title'),
                    dcc.Graph(id='YouTube-month-bar-chart')
                ]),
            ]),
        ]),
    elif tab == 'Hinge-tab':
        return html.Div(className='tab-content', children=[
            html.Div(className='tab-content-grid', children=[
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Match Results by Weekday', className='chart-title'),
                    dcc.Graph(id='Hinge-matches-weekday-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Match Results by Month', className='chart-title'),
                    dcc.Graph(id='Hinge-matches-month-bar-chart')
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Messages Sent per Weekday', className='chart-title'),
                    dcc.Graph(id='Hinge-messages-weekday-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Messages Sent per Month', className='chart-title'),
                    dcc.Graph(id='Hinge-messages-month-bar-chart')
                ]),
            ]),
        ])
    elif tab == 'Instagram-tab':
        return html.Div(className='tab-content', children=[
            html.Div(className='tab-content-grid', children=[
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Followers/Following by Month', className='chart-title'),
                    dcc.Graph(id='Instagram-connections-month-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Likes Given by Month', className='chart-title'),
                    dcc.Graph(id='Instagram-likes-month-bar-chart'),
                ]),
            ]),
        ])
    elif tab == 'Spotify-tab':
        return html.Div(className='tab-content', children=[
            html.Div(className='tab-content-grid', children=[
                html.Div(className='tab-content-list', children=[
                    html.H2(children='Most Streamed Artists', className='list-title'),
                    html.Ol(id='Spotify-top-artists', className='list', children='Loading...'),
                ]),
                html.Div(className='tab-content-list', children=[
                    html.H2(children='Most Streamed Tracks', className='list-title'),
                    html.Ol(id='Spotify-top-tracks', className='list', children='Loading...'),
                ]),
            ]),
            html.Div(className='tab-content-grid', children=[
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Streaming Activity per Weekday', className='chart-title'),
                    dcc.Graph(id='Spotify-streaming-weekday-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Streaming Activity per Month', className='chart-title'),
                    dcc.Graph(id='Spotify-streaming-month-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Artists Streamed per Month', className='chart-title'),
                    dcc.Graph(id='Spotify-artists-month-bar-chart'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Artists Streamed per Month', className='chart-title'),
                    dcc.Graph(id='Spotify-artists-month-sunburst'),
                ]),
                html.Div(className='tab-content-chart', children=[
                    html.H2(children='Tracks Streamed per Month', className='chart-title'),
                    dcc.Graph(id='Spotify-tracks-month-bar-chart'),
                ]),
                # html.Div(className='tab-content-chart', children=[
                #     html.H2(children='Top Artist Timeline', className='chart-title'),
                #     dcc.Graph(id='Spotify-top-artist-gantt-chart'),
                # ]),
            ]),
        ])



############### YOUTUBE ###############

@app.callback(
    Output('YouTube-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_youtube_weekday(year: Optional[int]):
    parser = YoutubeViewsParser(year=year)
    views_by_weekday = parser.get_views_by_weekday()
    types: List[str] = []
    weekdays: List[str] = []
    view_counts: List[int] = []
    for i in range(7):
        views = views_by_weekday[i]
        num_days_in_year = np.busday_count(str(year - 1), str(year), weekmask=WEEKDAYS[i][:3]) if year else 52
        weekdays.append(WEEKDAYS[i])
        view_counts.append(round(len(views) / num_days_in_year, 2))

    figure = px.bar(
        pd.DataFrame({
            'Day': weekdays,
            'Views (Average)': view_counts,
        }),
        x='Day',
        y='Views (Average)',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': WEEKDAYS
        }
    })
    return figure

@app.callback(
    Output('YouTube-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_youtube_month(year: Optional[int]):
    parser = YoutubeViewsParser(year=year)
    channels_by_month = parser.get_channels_by_month()
    channel_names: List[str] = []
    months: List[str] = []
    view_counts: List[int] = []
    for i in range(12):
        channels = channels_by_month[i]
        channel_names += [channel.name for channel in channels]
        view_counts += [len(channel.views) for channel in channels]
        months += [MONTHS[i]] * len(channels)

    figure = px.bar(
        pd.DataFrame({
            'Month': months,
            'Views (Total)': view_counts,
            'Channel': channel_names,
        }),
        x='Month',
        y='Views (Total)',
        color='Channel',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure



############### NETFLIX ###############

@app.callback(
    Output('Netflix-total-hours', 'children'),
    Input('year-dropdown', 'value'),
    Input('Netflix-profile-input', 'value'),
)
def update_netflix_total_hours(year: Optional[int], profile: Optional[str]):
    netflix_views_parser = NetflixViewsParser(year=year, profile=profile)
    seconds = netflix_views_parser.get_view_duration_seconds()
    hours = round(seconds / 60 / 60, 2)
    if year:
        name = profile or 'you'
        return 'In {0}, {1} watched a total of {2} hours'.format(year, name, hours)
    name = profile or 'You'
    return '{0} watched a total of {1} hours'.format(name, hours)

@app.callback(
    Output('Netflix-top-tv-shows', 'children'),
    Input('year-dropdown', 'value'),
    Input('Netflix-profile-input', 'value'),
)
def update_netflix_top_tv_shows(year: Optional[int], profile: Optional[str]):
    netflix_views_parser = NetflixViewsParser(year=year, profile=profile)
    shows = netflix_views_parser.get_most_viewed_shows_by_duration_seconds()[:10]
    return [
        html.Li(
            children='{0}: {1} hours'.format(show.title, show.duration_hours)
        ) for show in shows
    ]

@app.callback(
    Output('Netflix-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('Netflix-profile-input', 'value'),
)
def update_netflix_weekday(year: Optional[int], profile: Optional[str]):
    netflix_views_parser = NetflixViewsParser(year=year, profile=profile)
    views_by_weekday = netflix_views_parser.get_views_by_weekday()
    types: List[str] = []
    weekdays: List[str] = []
    duration_hours: List[int] = []
    for i in range(7):
        views = views_by_weekday[i]
        show_views = [view for view in views if bool(view.show_title)]
        movie_views = [view for view in views if not bool(view.show_title)]
        num_days_in_year = np.busday_count(str(year - 1), str(year), weekmask=WEEKDAYS[i][:3])

        types.append('Show')
        weekdays.append(WEEKDAYS[i])
        total_hours = round(sum([view.duration_seconds / 60 / 60 for view in show_views]), 2)
        duration_hours.append(round(total_hours / num_days_in_year, 2))

        types.append('Movie')
        weekdays.append(WEEKDAYS[i])
        total_hours = round(sum([view.duration_seconds / 60 / 60 for view in movie_views]), 2)
        duration_hours.append(round(total_hours / num_days_in_year, 2))

    figure = px.bar(
        pd.DataFrame({
            'Day': weekdays,
            'Hours (Average)': duration_hours,
            'Type': types
        }),
        x='Day',
        y='Hours (Average)',
        color='Type',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': WEEKDAYS
        }
    })
    return figure

@app.callback(
    Output('Netflix-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('Netflix-profile-input', 'value'),
)
def update_netflix_month(year: Optional[int], profile: Optional[str]):
    netflix_views_parser = NetflixViewsParser(year=year, profile=profile)
    shows_by_month = netflix_views_parser.get_shows_by_month()
    show_titles: List[str] = []
    months: List[str] = []
    duration_hours: List[int] = []
    for i in range(12):
        shows = shows_by_month[i]
        show_titles += [show.title for show in shows]
        duration_hours += [round(show.duration_seconds / 60 / 60, 0) for show in shows]
        months += [MONTHS[i]] * len(shows)

    figure = px.bar(
        pd.DataFrame({
            'Month': months,
            'Hours (Total)': duration_hours,
            'Shows': show_titles,
        }),
        x='Month',
        y='Hours (Total)',
        color='Shows',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure



############### HINGE ###############

@app.callback(
    Output('Hinge-matches-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_matches_weekday(year: Optional[int]):
    parser = HingeMatchesParser(year=year)
    matches_by_weekday = parser.get_matches_by_weekday()
    types: List[str] = []
    weekdays: List[str] = []
    match_counts: List[int] = []

    for i in range(7):
        matches = matches_by_weekday[i]
        like_accepted_matches = [match for match in matches if match.like_accepted]
        user_accepted_matches = [match for match in matches if match.user_accepted]
        like_rejected_matches = [match for match in matches if match.like_rejected]
        user_rejected_matches = [match for match in matches if match.user_rejected]

        types.append('Likes sent that were accepted')
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(like_accepted_matches))

        types.append('Likes received that you accepted')
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(user_accepted_matches))

        types.append('Likes sent that were not accepted')
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(like_rejected_matches))

        types.append('Rejections given')
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(user_rejected_matches))

    figure = px.bar(
        pd.DataFrame({
            'Weekday': weekdays,
            'Matches': match_counts,
            'Type': types,
        }),
        x='Weekday',
        y='Matches',
        color='Type'
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': WEEKDAYS
        }
    })
    return figure

@app.callback(
    Output('Hinge-matches-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_matches_month(year: Optional[int]):
    parser = HingeMatchesParser(year=year)
    matches_by_month = parser.get_matches_by_month()
    types: List[str] = []
    months: List[str] = []
    match_counts: List[int] = []

    for i in range(12):
        matches = matches_by_month[i]
        like_accepted_matches = [match for match in matches if match.like_accepted]
        user_accepted_matches = [match for match in matches if match.user_accepted]
        like_rejected_matches = [match for match in matches if match.like_rejected]
        user_rejected_matches = [match for match in matches if match.user_rejected]

        types.append('Likes sent that were accepted')
        months.append(MONTHS[i])
        match_counts.append(len(like_accepted_matches))

        types.append('Likes received that you accepted')
        months.append(MONTHS[i])
        match_counts.append(len(user_accepted_matches))

        types.append('Likes sent that were not accepted')
        months.append(MONTHS[i])
        match_counts.append(len(like_rejected_matches))

        types.append('Rejections given')
        months.append(MONTHS[i])
        match_counts.append(len(user_rejected_matches))

    figure = px.bar(
        pd.DataFrame({
            'Month': months,
            'Matches': match_counts,
            'Type': types,
        }),
        x='Month',
        y='Matches',
        color='Type'
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure


@app.callback(
    Output('Hinge-messages-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_messages_weekday(year: Optional[int]):
    parser = HingeMatchesParser(year=year)
    chats_by_weekday = parser.get_chats_by_weekday()
    figure = px.bar(
        pd.DataFrame({
            'Weekday': WEEKDAYS,
            'Messages Sent (Total)': [len(chats) for chats in chats_by_weekday],
        }),
        x='Weekday',
        y='Messages Sent (Total)',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': WEEKDAYS
        }
    })
    return figure

@app.callback(
    Output('Hinge-messages-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_messages_month(year: Optional[int]):
    parser = HingeMatchesParser(year=year)
    chats_by_month = parser.get_chats_by_month()
    figure = px.bar(
        pd.DataFrame({
            'Month': MONTHS,
            'Messages Sent (Total)': [len(chats) for chats in chats_by_month],
        }),
        x='Month',
        y='Messages Sent (Total)',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure



############### INSTAGRAM ###############

@app.callback(
    Output('Instagram-connections-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_instagram_connections_month(year: Optional[int]):
    parser = InstagramConnectionsParser(year=year)
    followers_by_month = parser.get_followers_by_month()
    following_by_month = parser.get_following_by_month()

    figure = px.bar(
        pd.DataFrame({
            'Month': MONTHS*2,
            'Connections': [len(followers) for followers in followers_by_month] + [len(following) for following in following_by_month],
            'Type': ['Followers']*12 + ['Following']*12
        }),
        x='Month',
        y='Connections',
        color='Type'
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure

@app.callback(
    Output('Instagram-likes-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_instagram_likes_month(year: Optional[int]):
    parser = InstagramLikesParser(year=year)
    likes_by_month = parser.get_likes_by_month()
    figure = px.bar(
        pd.DataFrame({
            'Month': MONTHS,
            'Likes': [len(likes) for likes in likes_by_month],
        }),
        x='Month',
        y='Likes',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure



############### SPOTIFY ###############

@app.callback(
    Output('Spotify-top-artists', 'children'),
    Input('year-dropdown', 'value'),
)
def update_spotify_top_artists(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    artists = streaming_history_parser.get_most_streamed_artists_by_duration()[:10]
    return [
        html.Li(
            children='{0}: {1} hours'.format(artist.name, round(artist.streamed_duration_seconds / 60 / 60, 1))
        ) for artist in artists
    ]

@app.callback(
    Output('Spotify-top-tracks', 'children'),
    Input('year-dropdown', 'value'),
)
def update_spotify_top_tracks(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    tracks = streaming_history_parser.get_most_streamed_tracks_by_duration()[:10]
    return [
        html.Li(
            children='{0}: {1} hours'.format(track.name, round(track.streamed_duration_seconds / 60 / 60, 1))
        ) for track in tracks
    ]

@app.callback(
    Output('Spotify-streaming-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_spotify_streaming_weekday(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    stream_duration_by_weekday = streaming_history_parser.get_stream_duration_by_weekday()
    figure = px.bar(
        pd.DataFrame({
            'Weekday': WEEKDAYS,
            'Duration (Hours)': [round(stream_duration / 60 / 60, 0) for stream_duration in stream_duration_by_weekday],
        }),
        x='Weekday',
        y='Duration (Hours)',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': WEEKDAYS
        }
    })
    return figure

@app.callback(
    Output('Spotify-streaming-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_spotify_streaming_month(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    stream_duration_by_month = streaming_history_parser.get_stream_duration_by_month()
    figure = px.bar(
        pd.DataFrame({
            'Month': MONTHS,
            'Duration (Hours)': [round(stream_duration / 60 / 60, 0) for stream_duration in stream_duration_by_month],
        }),
        x='Month',
        y='Duration (Hours)',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure

@app.callback(
    Output('Spotify-artists-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_spotify_artists_month(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    artists_by_month = streaming_history_parser.get_artists_by_month(min_threshold_stream_duration_seconds=60*60)  # Exclude artists listened less than an hour
    artist_names: List[str] = []
    months: List[str] = []
    duration_hours: List[int] = []
    for i in range(12):
        artists = artists_by_month[i]
        artist_names += [artist.name for artist in artists]
        duration_hours += [round(artist.streamed_duration_seconds / 60 / 60, 1) for artist in artists]
        months += [MONTHS[i]] * len(artists)

    figure = px.bar(
        pd.DataFrame({
            'Month': months,
            'Hours (Total)': duration_hours,
            'Artists': artist_names,
        }),
        x='Month',
        y='Hours (Total)',
        color='Artists',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure

@app.callback(
    Output('Spotify-tracks-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_spotify_tracks_month(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    tracks_by_month = streaming_history_parser.get_tracks_by_month(min_threshold_stream_duration_seconds=30*60)  # Exlude tracks listened less than 30 minutes
    track_names: List[str] = []
    months: List[str] = []
    duration_hours: List[int] = []
    for i in range(12):
        tracks = tracks_by_month[i]
        track_names += [track.name for track in tracks]
        duration_hours += [round(track.streamed_duration_seconds / 60 / 60, 1) for track in tracks]
        months += [MONTHS[i]] * len(tracks)

    figure = px.bar(
        pd.DataFrame({
            'Month': months,
            'Hours (Total)': duration_hours,
            'Track': [track_name[:25] for track_name in track_names],
        }),
        x='Month',
        y='Hours (Total)',
        color='Track',
    )
    figure.update_layout({
        'xaxis':{
            'categoryorder': 'array',
            'categoryarray': MONTHS
        }
    })
    return figure


@app.callback(
    Output('Spotify-artists-month-sunburst', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_spotify_artists_month_sunburst(year: Optional[int]):
    streaming_history_parser = SpotifyStreamingHistoryParser(year=year)
    tracks_by_month = streaming_history_parser.get_tracks_by_month(min_threshold_stream_duration_seconds=60*60)  # Exlude tracks listened less than an hour
    track_names: List[str] = []
    artist_names: List[str] = []
    months: List[str] = []
    duration_hours: List[int] = []
    for i in range(12):
        tracks = tracks_by_month[i]
        track_names += [track.name for track in tracks]
        artist_names += [track.artist_name for track in tracks]
        duration_hours += [round(track.streamed_duration_seconds / 60 / 60, 1) for track in tracks]
        months += [MONTHS[i]] * len(tracks)

    figure = px.sunburst(
        pd.DataFrame({
            'Month': months,
            'Hours (Total)': duration_hours,
            'Artist': artist_names,
            'Track': [track_name[:25] for track_name in track_names],
        }),
        path=['Month', 'Artist', 'Track'],
        values='Hours (Total)',
    )
    return figure


@app.callback(
    Output('Spotify-top-artist-gantt-chart', 'figure'),
    Input('year-dropdown', 'value'),
)
def update_spotify_artists_month_gantt(year: Optional[int]):
    """
    Timeline of the top artist throughout the year
    """
    pass


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
