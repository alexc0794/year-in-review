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


PRODUCTS = ["YouTube", "Netflix", "Hinge"]

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
        value='Netflix-tab',
        className='tab',
        children=[dcc.Tab(label=product, value='{0}-tab'.format(product)) for product in PRODUCTS]
    ),
    html.Div(id='tabs-content'),
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'Netflix-tab':
        return html.Div(className="tab-content", children=[
            html.Div(className='tab-content-row', children=[
                html.Div(className='chart', children=[
                    html.H2(children="Hours Watched per Weekday", className='chart-title'),
                    dcc.Graph(id='Netflix-weekday-bar-chart'),
                ]),
                html.Div(className='chart', children=[
                    html.H2(children='Hours Watched by Month', className='chart-title'),
                    dcc.Graph(id='Netflix-month-bar-chart')
                ]),
            ]),
        ]),
    elif tab == 'YouTube-tab':
        return html.Div(className="tab-content", children=[
            html.Div(className='tab-content-row', children=[
                html.Div(className='chart', children=[
                    html.H2(children='Videos Viewed per Weekday', className='chart-title'),
                    dcc.Graph(id='YouTube-weekday-bar-chart'),
                ]),
                html.Div(className='chart', children=[
                    html.H2(children='Videos Viewed by Month', className='chart-title'),
                    dcc.Graph(id='YouTube-month-bar-chart')
                ]),
            ]),
        ]),
    elif tab == 'Hinge-tab':
        return html.Div(className="tab-content", children=[
            html.Div(className='tab-content-row', children=[
                html.Div(className='chart', children=[
                    html.H2(children='Match Results by Weekday', className='chart-title'),
                    dcc.Graph(id='Hinge-matches-weekday-bar-chart'),
                ]),
                html.Div(className='chart', children=[
                    html.H2(children='Match Results by Month', className='chart-title'),
                    dcc.Graph(id='Hinge-matches-month-bar-chart')
                ]),
            ]),
            html.Div(className='tab-content-row', children=[
                html.Div(className='chart', children=[
                    html.H2(children='Messages Sent per Weekday', className='chart-title'),
                    dcc.Graph(id='Hinge-messages-weekday-bar-chart'),
                ]),
                html.Div(className='chart', children=[
                    html.H2(children='Messages Sent per Month', className='chart-title'),
                    dcc.Graph(id='Hinge-messages-month-bar-chart')
                ]),
            ]),
        ])

@app.callback(
    Output('YouTube-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_youtube_weekday_bar_chart(year: Optional[int]):
    views_parser = YoutubeViewsParser(year=year)
    views_by_weekday = views_parser.get_views_by_weekday()
    types: List[str] = []
    weekdays: List[str] = []
    view_counts: List[int] = []
    for i in range(7):
        views = views_by_weekday[i]
        num_days_in_year = np.busday_count(str(year - 1), str(year), weekmask=WEEKDAYS[i][:3]) if year else 52
        weekdays.append(WEEKDAYS[i])
        view_counts.append(round(len(views) / num_days_in_year, 2))

    weekday_bar_chart = px.bar(
        pd.DataFrame({
            "Day": weekdays,
            "Views (Average)": view_counts,
        }),
        x="Day",
        y="Views (Average)",
    )
    return weekday_bar_chart

@app.callback(
    Output('YouTube-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_youtube_month_bar_chart(year: Optional[int]):
    views_parser = YoutubeViewsParser(year=year)
    channels_by_month = views_parser.get_channels_by_month()
    channel_names: List[str] = []
    months: List[str] = []
    view_counts: List[int] = []
    for i in range(12):
        channels = channels_by_month[i]
        channel_names += [channel.name for channel in channels]
        view_counts += [len(channel.views) for channel in channels]
        months += [MONTHS[i]] * len(channels)

    month_bar_chart = px.bar(
        pd.DataFrame({
            "Month": months,
            "Views (Total)": view_counts,
            "Channel": channel_names,
        }),
        x="Month",
        y="Views (Total)",
        color="Channel",
    )
    return month_bar_chart

@app.callback(
    Output('Netflix-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_netflix_weekday_bar_chart(year: Optional[int]):
    views_parser = NetflixViewsParser(year=year)
    views_by_weekday = views_parser.get_views_by_weekday()
    types: List[str] = []
    weekdays: List[str] = []
    duration_hours: List[int] = []
    for i in range(7):
        views = views_by_weekday[i]
        show_views = [view for view in views if bool(view.show_title)]
        movie_views = [view for view in views if not bool(view.show_title)]
        num_days_in_year = np.busday_count(str(year - 1), str(year), weekmask=WEEKDAYS[i][:3])

        types.append("Show")
        weekdays.append(WEEKDAYS[i])
        total_hours = round(sum([view.duration_seconds / 60 / 60 for view in show_views]), 2)
        duration_hours.append(round(total_hours / num_days_in_year, 2))

        types.append("Movie")
        weekdays.append(WEEKDAYS[i])
        total_hours = round(sum([view.duration_seconds / 60 / 60 for view in movie_views]), 2)
        duration_hours.append(round(total_hours / num_days_in_year, 2))

    weekday_bar_chart = px.bar(
        pd.DataFrame({
            "Day": weekdays,
            "Hours (Average)": duration_hours,
            "Type": types
        }),
        x="Day",
        y="Hours (Average)",
        color="Type",
    )

    return weekday_bar_chart

@app.callback(
    Output('Netflix-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_netflix_month_bar_chart(year: Optional[int]):
    views_parser = NetflixViewsParser(year=year)
    shows_by_month = views_parser.get_shows_by_month()
    show_titles: List[str] = []
    months: List[str] = []
    duration_hours: List[int] = []
    for i in range(12):
        shows = shows_by_month[i]
        show_titles += [show.title for show in shows]
        duration_hours += [round(show.duration_seconds / 60 / 60, 0) for show in shows]
        months += [MONTHS[i]] * len(shows)

    month_bar_chart = px.bar(
        pd.DataFrame({
            "Month": months,
            "Hours (Total)": duration_hours,
            "Shows": show_titles,
        }),
        x="Month",
        y="Hours (Total)",
        color="Shows",
    )
    return month_bar_chart

@app.callback(
    Output('Hinge-matches-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_matches_weekday_bar_chart(year: Optional[int]):
    matches_parser = HingeMatchesParser(year=year)
    matches_by_weekday = matches_parser.get_matches_by_weekday()
    types: List[str] = []
    weekdays: List[str] = []
    match_counts: List[int] = []

    for i in range(7):
        matches = matches_by_weekday[i]
        like_accepted_matches = [match for match in matches if match.like_accepted]
        user_accepted_matches = [match for match in matches if match.user_accepted]
        like_rejected_matches = [match for match in matches if match.like_rejected]
        user_rejected_matches = [match for match in matches if match.user_rejected]

        types.append("Likes sent that were accepted")
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(like_accepted_matches))

        types.append("Likes received that you accepted")
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(user_accepted_matches))

        types.append("Likes sent that were not accepted")
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(like_rejected_matches))

        types.append("Rejections given")
        weekdays.append(WEEKDAYS[i])
        match_counts.append(len(user_rejected_matches))

    weekday_bar_chart = px.bar(
        pd.DataFrame({
            "Weekday": weekdays,
            "Matches": match_counts,
            "Type": types,
        }),
        x="Weekday",
        y="Matches",
        color="Type"
    )
    return weekday_bar_chart

@app.callback(
    Output('Hinge-matches-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_matches_month_bar_chart(year: Optional[int]):
    matches_parser = HingeMatchesParser(year=year)
    matches_by_month = matches_parser.get_matches_by_month()
    types: List[str] = []
    months: List[str] = []
    match_counts: List[int] = []

    for i in range(12):
        matches = matches_by_month[i]
        like_accepted_matches = [match for match in matches if match.like_accepted]
        user_accepted_matches = [match for match in matches if match.user_accepted]
        like_rejected_matches = [match for match in matches if match.like_rejected]
        user_rejected_matches = [match for match in matches if match.user_rejected]

        types.append("Likes sent that were accepted")
        months.append(MONTHS[i])
        match_counts.append(len(like_accepted_matches))

        types.append("Likes received that you accepted")
        months.append(MONTHS[i])
        match_counts.append(len(user_accepted_matches))

        types.append("Likes sent that were not accepted")
        months.append(MONTHS[i])
        match_counts.append(len(like_rejected_matches))

        types.append("Rejections given")
        months.append(MONTHS[i])
        match_counts.append(len(user_rejected_matches))

    month_bar_chart = px.bar(
        pd.DataFrame({
            "Month": months,
            "Matches": match_counts,
            "Type": types,
        }),
        x="Month",
        y="Matches",
        color="Type"
    )
    return month_bar_chart


@app.callback(
    Output('Hinge-messages-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_messages_weekday_bar_chart(year: Optional[int]):
    matches_parser = HingeMatchesParser(year=year)
    chats_by_weekday = matches_parser.get_chats_by_weekday()
    weekday_bar_chart = px.bar(
        pd.DataFrame({
            "Weekday": WEEKDAYS,
            "Messages Sent (Total)": [len(chats) for chats in chats_by_weekday],
        }),
        x="Weekday",
        y="Messages Sent (Total)",
    )
    return weekday_bar_chart

@app.callback(
    Output('Hinge-messages-month-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_hinge_messages_month_bar_chart(year: Optional[int]):
    matches_parser = HingeMatchesParser(year=year)
    chats_by_month = matches_parser.get_chats_by_month()
    month_bar_chart = px.bar(
        pd.DataFrame({
            "Month": MONTHS,
            "Messages Sent (Total)": [len(chats) for chats in chats_by_month],
        }),
        x="Month",
        y="Messages Sent (Total)",
    )
    return month_bar_chart


if __name__ == '__main__':
    app.run_server(debug=True)
