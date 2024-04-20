from dash import Dash, dcc, html, Input, Output
from threading import Lock
import plotly.express as px
import numpy as np
import pandas as pd
from django_plotly_dash import DjangoDash
from urllib.parse import quote
import json
# Define a lock to ensure thread-safe Dash app updates
lock = Lock()

app = DjangoDash("dash_app")  # Use DjangoDash instead of Dash
app.layout = html.Div([
    dcc.Graph(id='trade-heatmap', figure={}),
    html.Div(id='selected-country', hidden=True)
])

# Update the figure based on the selected commodity
@app.callback(
    Output('selected-country', 'children'),
    [Input('trade-heatmap', 'clickData')],
    prevent_initial_call=True
)
def display_selected_country(clickData):
    if clickData is not None:
        selected_country = clickData['points'][0]['location']
        message = {'country': selected_country}
        # window.parent.postMessage(json.dumps(message), '*')
        return f'{selected_country}\n'
    else:
        return "Select a country by clicking on the heatmap"

# Define the layout of your Dash app

def run_dash_app(selected_commodity, df):
    # Filter data for the selected commodity
    commodity_data = df[df['Commodity'] == selected_commodity]

    # Group by country and sum total trade value
    country_total_trade = commodity_data.groupby('country')['value'].sum().reset_index()
    country_total_trade['normalized_value'] = country_total_trade['value'] / country_total_trade['value'].max()

    colors = px.colors.sequential.Oranges

    edges = pd.cut(country_total_trade["normalized_value"], bins=len(colors)-1, retbins=True)[1]
    edges = edges[:-1] / edges[-1]
    edges = np.maximum(edges, np.full(len(edges), 0))

    cc_scale = (
        [(0, colors[0])]
        + [(e, colors[(i + 1) // 2]) for i, e in enumerate(np.repeat(edges,2))]
        + [(1, colors[-1])]
    )

    ticks = np.linspace(country_total_trade["normalized_value"].min(), country_total_trade["normalized_value"].max(), len(colors))[1:-1]

    # Create heatmap on a geo layout
    fig = px.choropleth(
        country_total_trade,
        locations="country",
        locationmode='country names',
        color="normalized_value",
        hover_name="country",
        hover_data={"value": ":.2f"},
        title='Total Trade Analysis for ' + selected_commodity,
        color_continuous_scale=cc_scale,
    )

    fig.update_layout(
        coloraxis={
            "colorbar": {
                "tickmode": "array",
                "tickvals": ticks,
                "ticktext": np.expm1(ticks).round(3),
            }
        },
        height=800,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_geos(
        fitbounds='locations',
        showcountries=True,
        projection_type="orthographic",
        showocean=True,
        oceancolor="LightBlue"
    )
    app.layout.children[0].figure = fig  # Update the figure in the layout

    return None  # Return None to avoid returning anything to the client
