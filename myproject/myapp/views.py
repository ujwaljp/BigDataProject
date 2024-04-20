from django.shortcuts import render
import pandas as pd
import plotly.express as px
import json
import numpy as np
from myproject.settings import BASE_DIR
from django.http import JsonResponse
import bar_chart_race as bcr
from . import dash_app

# Create your views here.
def home(request) :
    selected_commodity = request.GET.get('commodity', 'MEAT AND EDIBLE MEAT OFFAL.')

    # Read the dataset
    df = pd.read_csv(BASE_DIR / 'myapp/archive/2010_2021_HS2_export.csv')
   
    # Filter data for the selected commodity
    commodity_data = df[df['Commodity'] == selected_commodity]

    # Group by country and sum total trade value
    country_total_trade = commodity_data.groupby('country')['value'].sum().reset_index()
    country_total_trade['normalized_value'] = country_total_trade['value'] / country_total_trade['value'].max()

    dash_app.run_dash_app(selected_commodity, df)
    
    return render(request, 'home.html',  {'commodity_values' : df['Commodity'].unique(), 'selected_commodity' : selected_commodity})

def commodity_selection(request) :
    return render(request, 'commodity_selection.html')

def country_selection(request) :
    selected_country = request.GET.get('country', 'AFGHANISTAN')
    start_year = int(request.GET.get('start_year', 2010))
    end_year = int(request.GET.get('end_year', 2021))

    # Read the dataset
    df = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_export.csv')
    df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')
    # Load geojson data
    with open(BASE_DIR / 'myapp/archive/countries.geo.json', 'r') as f:
        geojson_data = json.load(f)

    df['year'] = df['year'].astype(int)
    df2['year'] = df2['year'].astype(int)
    # Filter data for the selected country
    country_export_data = df[(df['country'] == selected_country) & (df['year'] >= start_year) & (df['year'] <= end_year)]
    country_import_data = df2[(df2['country'] == selected_country) & (df2['year'] >= start_year) & (df2['year'] <= end_year)]
    # Group by country and sum total trade value
    country_total_export = country_export_data.groupby('Commodity')['value'].sum().reset_index()
    top_commodities_export = country_total_export.nlargest(6, 'value')

    country_total_import = country_import_data.groupby('Commodity')['value'].sum().reset_index()
    top_commodities_import = country_total_import.nlargest(6, 'value')    
    
    other_value_export = country_total_export[~country_total_export['Commodity'].isin(top_commodities_export['Commodity'])]['value'].sum()
    top_commodities_export.loc[len(top_commodities_export)] = ['Others', other_value_export]

    other_value_import = country_total_import[~country_total_import['Commodity'].isin(top_commodities_import['Commodity'])]['value'].sum()
    top_commodities_import.loc[len(top_commodities_import)] = ['Others', other_value_import]

    # Create dummy DataFrame with the selected country
    dummy_df = pd.DataFrame({'country': [selected_country]})

    # Create choropleth map
    fig = px.choropleth(
        data_frame=dummy_df,
        locations='country',
        locationmode='country names',
        color=[1],  # Dummy color value
        hover_name='country',
        geojson=geojson_data,
        # color_continuous_scale=['blue'],  # Set color to highlight the selected country
    )

    fig.update_layout(
        title='Selected Country: ' + selected_country,
        height=800,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_geos(
        fitbounds='locations',
        showcountries=True,
        projection_type="orthographic",
        showocean=True,
        oceancolor="LightBlue"
    )


    fig1 = px.pie(top_commodities_export, values='value', names='Commodity', hole=.3)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.update_layout(title=f'Top 6 Commodities Exported by {selected_country} and Others')

    fig2 = px.pie(top_commodities_import, values='value', names='Commodity', hole=.3)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(title=f'Top 6 Commodities Imported by {selected_country} and Others')
    return render(request, 'country_selection.html', {'globe' : fig.to_html(), 'country_values' : df['country'].unique(), 'selected_country' : selected_country, 'pie_chart_export' : fig1.to_html(), 'pie_chart_import' : fig2.to_html(), 'year_values' : np.arange(2010, 2022), 'start_year' : start_year, 'end_year' : end_year})

def racing_bar_chart(request) :
    selected_commodity = request.GET.get('commodity', 'MEAT AND EDIBLE MEAT OFFAL.')
    start_year = int(request.GET.get('start_year', 2010))
    end_year = int(request.GET.get('end_year', 2021))

    # Read the dataset
    df = pd.read_csv(BASE_DIR / 'myapp/archive/2010_2021_HS2_export.csv')
    # Filter the dataset to only include the selected commodity

    # Convert the 'year' column to datetime type
    df['year'] = pd.to_datetime(df['year'], format='%Y')

    # Aggregate total trade for each country for each year
    country_year_total = df.groupby(['country', pd.Grouper(key='year', freq='Y')])['value'].sum().unstack(fill_value=0)

    # Create the bar chart race
    bcr.bar_chart_race(
        df=country_year_total, 
        filename='trading_data_bar_chart_race.mp4',
        orientation='h',  # Set orientation to horizontal (country names on y-axis)
        title='Total Trade by Country over Time',  # Set title of the race
        steps_per_period=10,  # Adjust speed: lower value makes it slower
        period_length=1000,  # Adjust duration of each period in milliseconds
        figsize=(8, 6)  # Set figure size
    )