import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional
from dash.dependencies import Input, Output
from parsers.youtube.views_parser import ViewsParser as YoutubeViewsParser
from parsers.netflix.views_parser import ViewsParser as NetflixViewsParser

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


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
        children=[dcc.Tab(label=product, value='{0}-tab'.format(product)) for product in ["YouTube", "Netflix"]]
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
            # html.H1(children='Netflix'),
            html.Div(className='chart', children=[
                html.H2(id='Netflix-weekday-title', className='chart-title'),
                dcc.Graph(id='Netflix-weekday-bar-chart'),
            ]),
            html.Div(className='chart', children=[
                html.H2(id='Netflix-month-title', className='chart-title'),
                dcc.Graph(id='Netflix-month-bar-chart')
            ]),
        ]),
    elif tab == 'YouTube-tab':
        return html.Div(className="tab-content", children=[
            # html.H1(children='YouTube'),
            html.Div(className='chart', children=[
                html.H2(id='YouTube-weekday-title', className='chart-title'),
                dcc.Graph(id='YouTube-weekday-bar-chart'),
            ]),
            html.Div(className='chart', children=[
                html.H2(id='YouTube-month-title', className='chart-title'),
                dcc.Graph(id='YouTube-month-bar-chart')
            ]),
        ]),


for product in ['YouTube', 'Netflix']:
    @app.callback(
        Output('{0}-weekday-title'.format(product), 'children'),
        Input('year-dropdown', 'value')
    )
    def update_weekday_title(year: Optional[int]):
        return 'Videos Viewed per Weekday: ({0})'.format(year or 'All Time')

    @app.callback(
        Output('{0}-month-title'.format(product), 'children'),
        Input('year-dropdown', 'value')
    )
    def update_month_title(year: Optional[int]):
        return 'Videos Viewed per Month: ({0})'.format(year or 'All Time')


@app.callback(
    Output('YouTube-weekday-bar-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_YouTube_weekday_bar_chart(year: Optional[int]):
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
def update_YouTube_month_bar_chart(year: Optional[int]):
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
def update_Netflix_weekday_bar_chart(year: Optional[int]):
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

        if show_views:
            types.append("Show")
            weekdays.append(WEEKDAYS[i])
            total_hours = round(sum([view.duration_seconds / 60 / 60 for view in show_views]), 2)
            duration_hours.append(round(total_hours / num_days_in_year, 2))

        if movie_views:
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
def update_Netflix_month_bar_chart(year: Optional[int]):
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


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
