import dash
import dash_core_components as dcc
import dash_html_components as html

def loading():
    return html.Div(className='lds-roller', children=[
        html.Div(), html.Div(), html.Div(), html.Div(), html.Div(), html.Div(), html.Div(), html.Div(),
    ])
