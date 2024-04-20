from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Assuming you have loaded your CSV data into a DataFrame called df
df = pd.read_csv('./archive/2010_2021_HS2_export.csv')
app = Dash(__name__)

app.layout = html.Div([
    html.H4('Analysis of the restaurant sales'),
    dcc.Graph(id="graph"),
    html.P("Select a country:"),
    dcc.Dropdown(id='country',
        options=[{'label': c, 'value': c} for c in df['country'].unique()],
        value=df['country'].iloc[0], clearable=False
    )
])

@app.callback(
    Output("graph", "figure"), 
    Input("country", "value"))
def generate_chart(country):
    # Filter data for the selected country
    country_data = df[df['country'] == country]
    
    # Group by commodity and calculate total export value
    commodity_data = country_data.groupby('Commodity')['value'].sum().reset_index()
    
    # Get the top 5 commodities by total export value
    top_commodities = commodity_data.nlargest(5, 'value')
    
    # Sum of values for other commodities
    other_value = commodity_data[~commodity_data['Commodity'].isin(top_commodities['Commodity'])]['value'].sum()
    
    # Add 'Others' category
    top_commodities.loc[len(top_commodities)] = ['Others', other_value]
    
    fig = px.pie(top_commodities, values='value', names='Commodity', hole=.3)
    fig.update_layout(title=f'Top 5 Commodities and Others for {country}')
    
    return fig

app.run_server(debug=True)
