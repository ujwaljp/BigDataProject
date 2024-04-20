import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load datasets
df_export = pd.read_csv("archive/2010_2021_HS2_export.csv")
df_import = pd.read_csv("archive/2010_2021_HS2_import.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1("Export and Import Data Visualization"),
    html.Div([
        html.Label("Select Type:"),
        dcc.RadioItems(
            id="type-selector",
            options=[
                {'label': 'Export', 'value': 'export'},
                {'label': 'Import', 'value': 'import'}
            ],
            value='export'
        )
    ]),
    html.Div([
        html.Label("Select Commodity:"),
        dcc.Dropdown(
            id='commodity-dropdown',
            options=[{'label': commodity, 'value': commodity} for commodity in df_export['Commodity'].unique()],
            value=df_export['Commodity'].unique()[0]
        )
    ]),
    dcc.Graph(id='line-plot')
])

# Define callback to update the plot
@app.callback(
    Output('line-plot', 'figure'),
    [Input('type-selector', 'value'),
     Input('commodity-dropdown', 'value')]
)
def update_plot(type_selected, commodity_selected):
    if type_selected == 'export':
        df = df_export
    else:
        df = df_import

    df_filtered = df[df['Commodity'] == commodity_selected]
    yearly_total = df_filtered.groupby('year')['value'].sum().reset_index()

    fig = px.line(yearly_total, x='year', y='value', title=f'Total {type_selected.capitalize()} of {commodity_selected} from India (2010-2021)')
    fig.update_xaxes(title_text='Year')
    fig.update_yaxes(title_text=f'Total {type_selected.capitalize()} (million US $)')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
