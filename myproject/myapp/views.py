from django.shortcuts import render
import pandas as pd
import plotly.express as px
import json
import numpy as np
from myproject.settings import BASE_DIR
from django.http import JsonResponse

# Create your views here.
def home(request) :
    selected_commodity = request.GET.get('commodity', 'MEAT AND EDIBLE MEAT OFFAL.')

    # Read the dataset
    df = pd.read_csv(BASE_DIR / 'myapp/archive/2010_2021_HS2_export.csv')
    # Load geojson data
    with open('/home/akhil/Documents/CS661/BigDataProject/myproject/myapp/archive/countries.geo.json', 'r') as f:
        geojson_data = json.load(f)
   
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
    return render(request, 'home.html',  {'globe' : fig.to_html(), 'commodity_values' : df['Commodity'].unique(), 'selected_commodity' : selected_commodity})

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
    with open('/home/akhil/Documents/CS661/BigDataProject/myproject/myapp/archive/countries.geo.json', 'r') as f:
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