from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sys

def read() :
    # Read the dataset
    df = pd.read_csv('/home/akhil/Documents/CS661/BigDataProject/myproject/myapp/archive/2010_2021_HS2_export.csv')
    selected_country = 'AFGHANISTAN'
    start_year = 2010
    end_year = 2010
    df['year'] = df['year'].astype(int)
    # Filter data for the selected commodity
    country_data = df[(df['country'] == selected_country) & (df['year'] >= start_year) & (df['year'] <= end_year)]

    # Group by country and sum total trade value
    country_total_trade = country_data.groupby('Commodity')['value'].sum().reset_index()
    print('1\n')
    print(country_total_trade)

read()