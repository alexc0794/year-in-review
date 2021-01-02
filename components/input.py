import dash
import dash_core_components as dcc
import dash_html_components as html
from typing import Optional


def input(id: str, placeholder: Optional[str]):
    return html.Div(className='input-wrapper', children=[
        dcc.Input(
            id=id,
            debounce=True,
            name=id,
            className='input',
            placeholder=placeholder
        ),
        html.Label(htmlFor=id, className='input-label', children=placeholder)
    ])
