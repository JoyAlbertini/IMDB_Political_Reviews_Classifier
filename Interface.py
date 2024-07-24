import asyncio

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from AnalysisCollector import get_film_html, find_html_and_extract_data
from FilmCollector import Film_collector
from Utils import extract_imdb_id

film_collector = Film_collector()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
document_options = find_html_and_extract_data()
app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='imdb-link-input',
            type='text',
            placeholder='Enter IMDb Link',
            style={'min-width': '700px', 'margin-right': '10px', 'flex': '1'}
        ),
        html.Button(
            'Fetch Movie',
            id='fetch-button',
            n_clicks=0,
            style={'margin-right': '10px'}
        ),
        dcc.Dropdown(
            id='document-dropdown',
            options=[],
            placeholder='Select an analysis document',
            style={'width': '400px', 'margin-right': '10px'}
        ),
        html.Button(
            'Get Movie',
            id='fetch-button2',
            n_clicks=0
        )
    ], style={'display': 'flex',
              'align-items': 'center',
              'width': '100%'
              }),
    dbc.Spinner(html.Div(id='movie-data')),
])


@app.callback(
    Output('document-dropdown', 'options'),
    Input('document-dropdown', 'value')
)
def update_dropdown_options(selected_value):
    # Update options every time a selection is made or dropdown is interacted with
    return find_html_and_extract_data()

def run_async_function_in_thread(id_imdb, update_function):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    html_content = loop.run_until_complete(get_film_html(id_imdb))
    loop.close()

    update_function(html_content)


@app.callback(
    Output('movie-data', 'children'),
    [Input('fetch-button', 'n_clicks'),
     Input('fetch-button2', 'n_clicks')],
    [State('imdb-link-input', 'value'),
     State('document-dropdown', 'value')]
)
def unified_update_output(n_clicks1, n_clicks2, imdb_link, id_imdb):
    # determine which button was pressed
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'fetch-button':
        if imdb_link is None:
            return 'Invalid link'
        imdb_id = extract_imdb_id(imdb_link)
        return fetch_data(n_clicks1, imdb_id)
    elif button_id == 'fetch-button2':
        return fetch_data(n_clicks2, id_imdb)


def fetch_data(n_clicks, imdb_id):
    def get_film_html_sync(imdb_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        html_content = loop.run_until_complete(get_film_html(imdb_id))
        loop.close()
        return html_content

    if n_clicks > 0 and imdb_id:
        html_content = get_film_html_sync(imdb_id)
        if html_content:
            return html.Iframe(
                srcDoc=html_content,
                style={"width": "100%", "height": "1000px"}
            )
        else:
            return "No data fetched or error occurred."

    return "No data fetched."


if __name__ == '__main__':
    app.run_server(debug=True, port=8100)
