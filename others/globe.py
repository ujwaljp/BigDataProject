import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import json
import numpy as np

# Read the dataset
df = pd.read_csv('archive/2010_2021_HS2_export.csv')

# Load geojson data
with open('countries.geo.json', 'r') as f:
    geojson_data = json.load(f)

# Create a Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1('Commodity Trade Analysis by Country'),
    dcc.Dropdown(
        id='commodity-dropdown',
        options=[{'label': commodity, 'value': commodity} for commodity in df['Commodity'].unique()],
        value=df['Commodity'].unique()[0],
        clearable=False,
        placeholder='Select a commodity'
    ),
    dcc.Graph(id='trade-heatmap')
])

# Define callback to update heatmap
@app.callback(
    Output('trade-heatmap', 'figure'),
    [Input('commodity-dropdown', 'value')]
)
def update_heatmap(selected_commodity):
    # Filter data for the selected commodity
    commodity_data = df[df['Commodity'] == selected_commodity]

    # Group by country and sum total trade value
    country_total_trade = commodity_data.groupby('country')['value'].sum().reset_index()
    country_total_trade['normalized_value'] = country_total_trade['value'] / country_total_trade['value'].max()


    colors = px.colors.sequential.Oranges

    # df["Density"] = np.log1p(df["2020"])
    edges = pd.cut(country_total_trade["normalized_value"], bins=len(colors)-1, retbins=True)[1]
    edges = edges[:-1] / edges[-1]
    # color scales don't like negative edges...
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
        color="normalized_value",  # Color represents the summed trade value
        hover_name="country",
        hover_data={"value": ":.2f"},  # Display value with two decimals on hover
        title='Total Trade Analysis for ' + selected_commodity,
        geojson=geojson_data, 
        color_continuous_scale=cc_scale,  # Using Viridis color scale
        # range_color=(0, 1),
    )

    fig.update_layout(
        coloraxis={
            "colorbar": {
                "tickmode": "array",
                "tickvals": ticks,
                "ticktext": np.expm1(ticks).round(3),
            }
        },
        height = 800,
        plot_bgcolor='rgba(0,0,0,0)' 
    )
    fig.update_geos(
        fitbounds='locations',
        showcountries=True,
        projection_type="orthographic",  # Set projection to 'orthographic' for a globe view
        showocean=True,
        oceancolor="LightBlue"
    )

    # fig.update_layout(
    #      # Set background color to transparent
    # )


    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
