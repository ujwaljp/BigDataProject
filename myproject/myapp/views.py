from django.shortcuts import render
import pandas as pd
import plotly.express as px
import json
import numpy as np
from myproject.settings import BASE_DIR
from django.conf import settings
import bar_chart_race as bcr
from . import dash_app
import os
import plotly.graph_objs as go
from django.http import JsonResponse

# Create your views here.
def home(request) :
    selected_commodity = request.GET.get('commodity', 'MEAT AND EDIBLE MEAT OFFAL.')
    start_year = int(request.GET.get('start_year', 2010))
    end_year = int(request.GET.get('end_year', 2021))
    globe_type = request.GET.get('globe_type', 'export')
    # Read the dataset
    df = pd.read_csv(BASE_DIR / 'myapp/archive/2010_2021_HS2_export.csv')
    df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')
    # Filter data for the selected commodity
    # commodity_data = df[df['Commodity'] == selected_commodity]

    # # Group by country and sum total trade value
    # country_total_trade = commodity_data.groupby('country')['value'].sum().reset_index()
    # country_total_trade['normalized_value'] = country_total_trade['value'] / country_total_trade['value'].max()
    df['year'] = df['year'].astype(int)
    df2['year'] = df2['year'].astype(int)
    dash_app.run_dash_app(selected_commodity, df if globe_type == 'export' else df2)
    # Filter data for the selected commodity
    commodity_export_data = df[(df['Commodity'] == selected_commodity) & (df['year'] >= start_year) & (df['year'] <= end_year)]
    commodity_import_data = df2[(df2['Commodity'] == selected_commodity) & (df2['year'] >= start_year) & (df2['year'] <= end_year)]
    # Group by country and sum total trade value
    commodity_total_export = commodity_export_data.groupby('country')['value'].sum().reset_index()
    top_countries_export = commodity_total_export.nlargest(6, 'value')

    commodity_total_import = commodity_import_data.groupby('country')['value'].sum().reset_index()
    top_countries_import = commodity_total_import.nlargest(6, 'value')    

    # print(top_countries_export)

    other_value_export = commodity_total_export[~commodity_total_export['country'].isin(top_countries_export['country'])]['value'].sum()
    # Create a new row as a dictionary
    new_row = {'country': ['OTHERS'], 'value': [other_value_export]}
    # Append the new row to the DataFrame
    top_countries_export=pd.concat([top_countries_export, pd.DataFrame(new_row)], ignore_index=True)

    other_value_import = commodity_total_import[~commodity_total_import['country'].isin(top_countries_import['country'])]['value'].sum()

    # Create a new row as a dictionary
    new_row = {'country': ['OTHERS'], 'value': [other_value_import]}

    # Append the new row to the DataFrame
    top_countries_import=pd.concat([top_countries_import, pd.DataFrame(new_row)], ignore_index=True)
    top_countries_export['Shortened_Name'] = top_countries_export['country']
    top_countries_import['Shortened_Name'] = top_countries_import['country']

    fig1 = px.pie(top_countries_export, values='value', names='Shortened_Name', hover_name='country', hole=.3)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.update_layout(title=f'Top 6 Countries Exporting {selected_commodity} and Others', margin=dict(t=0, b=0, l=0, r=0))

    fig2 = px.pie(top_countries_import, values='value', names='Shortened_Name', hover_name='country', hole=.3)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(title=f'Top 6 Countries Importing {selected_commodity} and Others', margin=dict(t=0, b=0, l=0, r=0))

    return render(request, 'home.html',  {'commodity_values' : df['Commodity'].unique(), 'selected_commodity' : selected_commodity, 'pie_chart_export' : fig1.to_html(), 'pie_chart_import' : fig2.to_html(), 'year_values' : np.arange(2010, 2022), 'start_year' : start_year, 'end_year' : end_year, 'globe_type': globe_type})

def running_bar_chart_country(request):
    selected_country = request.GET.get('country', 'AFGHANISTAN')
    trade_type = request.GET.get('trade_type', 'export')
    df = pd.read_csv(BASE_DIR / f'myapp/archive/2010_2021_HS2_{trade_type}.csv')
    start_year = 2010
    end_year = 2021
    country_export_data = df[(df['country'] == selected_country) & (df['year'] >= start_year) & (df['year'] <= end_year)]
    country_export_data['year'] = pd.to_datetime(df['year'], format='%Y')

    # Group the data by year and commodity to calculate the total export value for each commodity in each year
    country_export_data_grouped = country_export_data.groupby(['year', 'Commodity'])['value'].sum().reset_index()

    # Sort the data for each year based on the total export value of commodities
    country_export_data_sorted = country_export_data_grouped.sort_values(['year', 'value'], ascending=[True, False])

    # Initialize an empty list to store the top 10 commodities for each year
    top_commodities_by_year = []

    # Iterate over each year and select the top 10 commodities
    for year in country_export_data_sorted['year'].unique():
        top_commodities_by_year.append(country_export_data_sorted[country_export_data_sorted['year'] == year].head(10))

    # Concatenate the dataframes to create a single dataframe containing the top 10 commodities for each year
    top_commodities_df = pd.concat(top_commodities_by_year, ignore_index=True)
    # top_commodities_df.to_csv(BASE_DIR/'myapp/archive/original.csv', index = False)
    top_commodities_df['Commodity'] = top_commodities_df['Commodity'].apply(lambda x: x[:20])  # Truncate to the first 20 character

    df_pivot = top_commodities_df.pivot(index='year', columns='Commodity', values='value')

    # Create the Bar Chart Race
    bcr.bar_chart_race(
        df=df_pivot,
        filename=f'static/commodity_valuation_race_{trade_type}.mp4',  # Output filename
        # orientation='h',  # Horizontal bars
        n_bars=10,  # Number of bars to include in the chart
        steps_per_period=10,  # Number of steps per year
        period_length=1000,  # Length of each period in milliseconds
        title=f'Commodity Valuation Race {trade_type}',  # Title of the chart
        figsize=(10, 6),  # Figure size
    )
    f_string = f'commodity_valuation_race_{trade_type}.mp4' 
    video_path = os.path.join(settings.STATIC_URL, f_string)
    return JsonResponse({'video_path': video_path})

def running_bar_chart_home(request):
    selected_commodity = request.GET.get('commodity', 'MEAT AND EDIBLE MEAT OFFAL.')
    trade_type = request.GET.get('trade_type', 'export')
    df = pd.read_csv(BASE_DIR / f'myapp/archive/2010_2021_HS2_{trade_type}.csv')
    start_year = 2010
    end_year = 2021
    commodity_export_data = df[(df['Commodity'] == selected_commodity) & (df['year'] >= start_year) & (df['year'] <= end_year)]
    commodity_export_data['year'] = pd.to_datetime(df['year'], format='%Y')

    # Group the data by year and country to calculate the total export value for each country in each year
    commodity_export_data_grouped = commodity_export_data.groupby(['year', 'country'])['value'].sum().reset_index()

    # Sort the data for each year based on the total export value of countries
    commodity_export_data_sorted = commodity_export_data_grouped.sort_values(['year', 'value'], ascending=[True, False])

    # Initialize an empty list to store the top 10 countries for each year
    top_countries_by_year = []

    # Iterate over each year and select the top 10 countries
    for year in commodity_export_data_sorted['year'].unique():
        top_countries_by_year.append(commodity_export_data_sorted[commodity_export_data_sorted['year'] == year].head(10))

    # Concatenate the dataframes to create a single dataframe containing the top 10 countries for each year
    top_countries_df = pd.concat(top_countries_by_year)

    top_countries_df['country'] = top_countries_df['country']
    df_pivot = top_countries_df.pivot(index='year', columns='country', values='value')

    # Create the Bar Chart Race
    bcr.bar_chart_race(
        df=df_pivot,
        filename=f'static/country_valuation_race_{trade_type}.mp4',  # Output filename
        # orientation='h',  # Horizontal bars
        n_bars=10,  # Number of bars to include in the chart
        steps_per_period=10,  # Number of steps per year
        period_length=1000,  # Length of each period in milliseconds
        title=f'Country Valuation Race for {trade_type}',  # Title of the chart
        figsize=(10, 6),  # Figure size
    )
    f_string = f'country_valuation_race_{trade_type}.mp4'
    video_path = os.path.join(settings.STATIC_URL, f_string)
    return JsonResponse({'video_path': video_path})

def commodity_selection(request) :
    return render(request, 'commodity_selection.html')

def country_selection(request) :

    selected_country = request.GET.get('country', 'AFGHANISTAN')
    start_year = int(request.GET.get('start_year', 2010))
    end_year = int(request.GET.get('end_year', 2021))

    # Read the dataset
    df = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_export.csv')
    df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')

    # # Load geojson data
    # with open(BASE_DIR / 'myapp/archive/countries.geo.json', 'r') as f:
    #     geojson_data = json.load(f)

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
    # Create a new row as a dictionary
    new_row = {'Commodity': ['OTHERS'], 'value': [other_value_export]}
    # Append the new row to the DataFrame
    top_commodities_export=pd.concat([top_commodities_export, pd.DataFrame(new_row)], ignore_index=True)

    other_value_import = country_total_import[~country_total_import['Commodity'].isin(top_commodities_import['Commodity'])]['value'].sum()
    
    # Create a new row as a dictionary
    new_row = {'Commodity': ['OTHERS'], 'value': [other_value_import]}

    # Append the new row to the DataFrame
    top_commodities_import=pd.concat([top_commodities_import, pd.DataFrame(new_row)], ignore_index=True)

    dash_app.run_dash_app(None, df, selected_country)

    top_commodities_export['Shortened_Name'] = top_commodities_export['Commodity'].apply(lambda x: x[:20])  # Truncate to the first 20 characters
    top_commodities_import['Shortened_Name'] = top_commodities_import['Commodity'].apply(lambda x: x[:20])  # Truncate to the first 20 characters

    fig1 = px.pie(top_commodities_export, values='value', names='Shortened_Name',hover_name = 'Commodity', hole=.3)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.update_layout(title=f'Top 6 Commodities Exported by {selected_country} and Others',margin=dict(t=0, b=0, l=0, r=0))

    fig2 = px.pie(top_commodities_import, values='value', names='Shortened_Name',hover_name = 'Commodity', hole=.3)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(title=f'Top 6 Commodities Imported by {selected_country} and Others', margin=dict(t=0, b=0, l=0, r=0))

    return render(request, 'country_selection.html', {'country_values' : df['country'].unique(), 'selected_country' : selected_country, 'pie_chart_export' : fig1.to_html(), 'pie_chart_import' : fig2.to_html(), 'year_values' : np.arange(2010, 2022), 'start_year' : start_year, 'end_year' : end_year})

def country_commodity_selection(request) :
    selected_country = request.GET.get('country', 'RUSSIA')
    start_year = 2010
    end_year = 2021
     # Read the dataset
    df = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_export.csv')
    df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')

    # Filter data for the selected country
    country_export_data = df[(df['country'] == selected_country)]
    country_import_data = df2[(df2['country'] == selected_country)]

    country_total_export = country_export_data.groupby('Commodity')['value'].sum().reset_index()
    top_commodities_export = country_total_export.nlargest(6, 'value')

    country_total_import = country_import_data.groupby('Commodity')['value'].sum().reset_index()
    top_commodities_import = country_total_import.nlargest(6, 'value')
        # Create a bar chart with export and import data using Plotly
        # Create a line chart with export and import data
    import_commodity_values = top_commodities_import['Commodity'].unique()
    export_commodity_values = top_commodities_export['Commodity'].unique()
    import_commodity = request.GET.get('import_commodity', import_commodity_values[0])
    export_commodity = request.GET.get('export_commodity', export_commodity_values[0])
    if( 'commodity' in request.GET):
        import_commodity = export_commodity = request.GET.get('commodity')

    country_commodity_export_data = df[(df['country'] == selected_country) & (df['Commodity'] == export_commodity)]
    country_commodity_import_data = df2[(df2['country'] == selected_country) & (df2['Commodity'] == import_commodity)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=country_commodity_export_data['year'], y=country_commodity_export_data['value'], mode='lines+markers', name='Export', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=country_commodity_import_data['year'], y=country_commodity_import_data['value'], mode='lines+markers', name='Import', line=dict(color='orange')))
    fig.update_layout(title=f'Export and Import Valuation of {import_commodity} and {export_commodity} in {selected_country} ({start_year}-{end_year})',
                    xaxis_title='Year',
                    yaxis_title='Valuation')
    
    
    return render(request, 'country_commodity_selection.html', {'line_chart_html': fig.to_html(), 'country_values' : df['country'].unique(), 'selected_country' : selected_country, 'import_commodity_values' : import_commodity_values, 'import_commodity' : import_commodity, 'export_commodity' : export_commodity, 'export_commodity_values': export_commodity_values, 'commodity_values': df['Commodity'].unique()})
        
def commodity_country_selection(request) :
    selected_commodity = request.GET.get('Commodity', 'MEAT AND EDIBLE MEAT OFFAL.')
    start_year = 2010
    end_year = 2021
     # Read the dataset
    df = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_export.csv')
    df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')

    # Filter data for the selected commodity
    commodity_export_data = df[(df['Commodity'] == selected_commodity)]
    commodity_import_data = df2[(df2['Commodity'] == selected_commodity)]

    commodity_total_export = commodity_export_data.groupby('country')['value'].sum().reset_index()
    top_commodities_export = commodity_total_export.nlargest(6, 'value')

    commodity_total_import = commodity_import_data.groupby('country')['value'].sum().reset_index()
    top_commodities_import = commodity_total_import.nlargest(6, 'value')
        # Create a bar chart with export and import data using Plotly
        # Create a line chart with export and import data
    import_country_values = top_commodities_import['country'].unique()
    export_country_values = top_commodities_export['country'].unique()
    import_country = request.GET.get('import_country', import_country_values[0])
    export_country = request.GET.get('export_country', export_country_values[0])
    if( 'country' in request.GET):
        import_country = export_country = request.GET.get('country')

    commodity_country_export_data = df[(df['Commodity'] == selected_commodity) & (df['country'] == export_country)]
    commodity_country_import_data = df2[(df2['Commodity'] == selected_commodity) & (df2['country'] == import_country)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=commodity_country_export_data['year'], y=commodity_country_export_data['value'], mode='lines+markers', name='Export', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=commodity_country_import_data['year'], y=commodity_country_import_data['value'], mode='lines+markers', name='Import', line=dict(color='orange')))
    fig.update_layout(title=f'Export and Import Valuation of {import_country} and {export_country} in {selected_commodity} ({start_year}-{end_year})',
                    xaxis_title='Year',
                    yaxis_title='Valuation')
    
    
    return render(request, 'commodity_country_selection.html', {'line_chart_html': fig.to_html(), 'commodity_values' : df['Commodity'].unique(), 'selected_commodity' : selected_commodity, 'import_country_values' : import_country_values, 'import_country' : import_country, 'export_country' : export_country, 'export_country_values': export_country_values, 'country_values': df['country'].unique()})
        