from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sys

# Read the dataset
df = pd.read_csv('2010_2021_HS2_export.csv')  # Replace 'your_dataset.csv' with the path to your dataset file

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Analysis of the trading data'),
    dcc.Graph(id="graph"),
    html.P("Commodity:"),
    dcc.Dropdown(id='commodity',
        options=[{'label': commodity, 'value': commodity} for commodity in df['Commodity'].unique()],
        value=df['Commodity'].unique()[0], clearable=False
    ),
    html.P("Value:"),
    dcc.Dropdown(id='value',
        options=[{'label': 'Value of Import', 'value': 'value'}],
        value='value', clearable=False
    ),
])


@app.callback(
    Output("graph", "figure"), 
    Input("commodity", "value"), 
    Input("value", "value"))
def generate_chart(commodity, value):
    commodity_data = df[df['Commodity'] == commodity]
    # commodity_data_sorted = commodity_data.sort_values(by=value, ascending=False)
    
    country_data = commodity_data.groupby('country')['value'].sum().reset_index()
    top_countries = country_data.nlargest(6, 'value')
    
    # Append 'Others' row
    other_value = country_data[~country_data['country'].isin(top_countries['country'])]['value'].sum()
    top_countries.loc[len(top_countries)] = ['Others', other_value]

    fig = px.pie(top_countries, values=value, names='country', hole=.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title=f'Top 6 Countries Importing {commodity} and Others')
    return fig


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <commodity>")
        sys.exit(1)
    
    commodity_input = sys.argv[1]
    app.run_server(debug=True)
