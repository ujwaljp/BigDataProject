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

def run_dash_app(selected_commodity=None, df=None, selected_country=None, geojson_data=None):
    fig = None
    if selected_country is None:
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
            height=500,
            plot_bgcolor='rgba(1,1,1,0)'
        )
        fig.update_geos(
            fitbounds='locations',
            showcountries=True,
            projection_type="orthographic",
            showocean=True,
            oceancolor="LightBlue"
        )
          # Update the figure in the layout
    else:
        unique_countries = df['country'].unique()

        # Create a DataFrame from the unique countries
        unique_countries_df = pd.DataFrame({'country': unique_countries})

        # Add a new column 'value' with default value 0
        unique_countries_df['value'] = 0
        unique_countries_df.loc[unique_countries_df['country'] == selected_country, 'value'] = 1
        # Create choropleth map
        fig = px.choropleth(
            unique_countries_df,
            locations='country',
            locationmode='country names',
            color="value",
            hover_name='country', 
            color_continuous_scale=['rgb(220, 220,220)', 'red'],  # Set color to highlight the selected country in red
            range_color=[0, 1],  # Set range to correctly map the colors
            # Note: Setting color_discrete_map to {} hides the color scale
            color_discrete_map={},
        )

        # Update layout
        fig.update_layout(
            title='Selected Country: ' + selected_country,
            height=500,
            plot_bgcolor='rgba(1,1,1,0)',
            coloraxis_showscale=False,  # Hide the color scale
            geo=dict(
                showcountries=True,
                projection_type="orthographic",
                showocean=True,
                oceancolor="LightBlue",
                showland=True,
                landcolor="white",
                fitbounds="locations",  # Zoom in on the selected country
            )
        )
    app.layout.children[0].figure = fig

    return None  # Return None to avoid returning anything to the client
