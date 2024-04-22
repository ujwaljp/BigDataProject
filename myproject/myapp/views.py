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
import json
import yfinance as yf



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
    selected_commodity = request.GET.get('sommodity', 'MEAT AND EDIBLE MEAT OFFAL.')
    start_year = int(request.GET.get('start_year', 2010))
    end_year = int(request.GET.get('end_year', 2021))

     # Read the dataset
    df = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_export.csv')
    df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')

    # Filter data for the selected country
    country_export_data = df[(df['country'] == selected_country) & (df['Commodity'] == selected_commodity) & (df['year'] >= start_year) & (df['year'] <= end_year)]
    country_import_data = df2[(df2['country'] == selected_country) & (df2['Commodity'] == selected_commodity) & (df2['year'] >= start_year) & (df2['year'] <= end_year)]

     # Create a bar chart with export and import data using Plotly
    # Create a line chart with export and import data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=country_export_data['year'], y=country_export_data['value'], mode='lines+markers', name='Export', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=country_import_data['year'], y=country_import_data['value'], mode='lines+markers', name='Import', line=dict(color='orange')))
    fig.update_layout(title=f'Export and Import Valuation of {selected_commodity} in {selected_country} ({start_year}-{end_year})',
                      xaxis_title='Year',
                      yaxis_title='Valuation')

    return render(request, 'country_commodity_selection.html', {'bar_chart_html': fig.to_html(), 'year_values' : np.arange(2010, 2022), 'start_year' : start_year, 'end_year' : end_year, 'country_values' : df['country'].unique(), 'selected_country' : selected_country, 'commodity_values' : df['Commodity'].unique()})


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

    if 'export_commodity' in request.GET or 'import_commodity' in request.GET :
        # Create a bar chart with export and import data using Plotly
        # Create a line chart with export and import data
        import_commodity = request.GET.get('import_commodity', 'MEAT AND EDIBLE MEAT OFFAL.')
        export_commodity = request.GET.get('export_commodity', 'MEAT AND EDIBLE MEAT OFFAL.')

        country_commodity_export_data = df[(df['country'] == selected_country) & (df['Commodity'] == export_commodity)]
        country_commodity_import_data = df2[(df2['country'] == selected_country) & (df2['Commodity'] == import_commodity)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=country_commodity_export_data['year'], y=country_commodity_export_data['value'], mode='lines+markers', name='Export', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=country_commodity_import_data['year'], y=country_commodity_import_data['value'], mode='lines+markers', name='Import', line=dict(color='orange')))
        fig.update_layout(title=f'Export and Import Valuation of {import_commodity} and {export_commodity} in {selected_country} ({start_year}-{end_year})',
                        xaxis_title='Year',
                        yaxis_title='Valuation')
        
        return render(request, 'country_commodity_selection.html', {'line_chart_html': fig.to_html(), 'country_values' : df['country'].unique(), 'selected_country' : selected_country, 'import_commodity_values' : top_commodities_import['Commodity'].unique(), 'export_commodity_values' : top_commodities_export['Commodity'].unique(), 'import_commodity' : import_commodity, 'export_commodity' : export_commodity})
        
    else :
        # Group by country and sum total trade value    

        return render(request, 'country_commodity_selection.html', {'country_values' : df['country'].unique(), 'selected_country' : selected_country, 'import_commodity_values' : top_commodities_import['Commodity'].unique(), 'export_commodity_values' : top_commodities_export['Commodity'].unique(), 'import_commodity' :top_commodities_import['Commodity'].unique()[0], 'export_commodity' :top_commodities_export['Commodity'].unique()[0]})
    

# Function to extract close prices for specific dates from Yahoo Finance
def extract_close_prices(ticker):
    # Fetch OHLC data from Yahoo Finance
    try:
        data = yf.download(ticker, start='2010-03-31', end='2021-12-31', interval='3mo')['Close']
        # Check if any data is missing
        if data.empty or data.isnull().values.any():
            return None
        else:
            return data
    except ValueError:
        return None

# Function to calculate yearly average close price
def calculate_yearly_avg_close(close_prices):
    yearly_avg_close = close_prices.groupby(close_prices.index.year).mean().reset_index()
    yearly_avg_close.columns = ['year', 'value']
    return yearly_avg_close

# Function to get tickers based on category
def get_category_tickers(category):
    with open(BASE_DIR / 'myapp/archive/companies.json') as f :
        data = json.load(f)
    return data[category]

# Function to get stock data based on category
def find_stock_data(category):
    tickers = get_category_tickers(category)
    ticker_list = []
    company_list = []
    counter = 0
    for ticker in tickers :
        if counter == 3 :
            break 
        # Extract close prices for specific dates from Yahoo Finance
        close_prices = extract_close_prices(ticker)

        # Calculate yearly average close price if available
        if close_prices is not None:
            yearly_avg_close = calculate_yearly_avg_close(close_prices)
            # if not yearly_avg_close.empty:
            #     if len(yearly_avg_close) == 14:
            #         print(f"Yearly average close prices for {ticker}:")
            #         print(yearly_avg_close)
            #     else:
            #         print(f"Yearly average close prices for {ticker}:")
            #         print(yearly_avg_close)
            ticker_list.append(yearly_avg_close)
        company_list.append(yf.Ticker(ticker).info['longName'])
        counter += 1
        
    return ticker_list, company_list



def trend_analysis(request):
    
    sector_df = pd.read_csv(BASE_DIR / 'myapp/archive/categories.csv')

    if 'sector' in request.GET :
        selected_sector = request.GET.get('sector', 'Construction')

        # Read the dataset
        df = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_export.csv')
        df2 = pd.read_csv(BASE_DIR /'myapp/archive/2010_2021_HS2_import.csv')

        # Filter commodities belonging to the given category
        filtered_commodities = sector_df[sector_df['Category'] == selected_sector]['Commodity']

        # Filter import data based on filtered commodities
        filtered_import_data = df2[df2['Commodity'].isin(filtered_commodities)]

        # Group by year and sum the values for each year
        total_import_per_year = filtered_import_data.groupby('year')['value'].sum().reset_index()

        # Filter export data based on filtered commodities
        filtered_export_data = df[df['Commodity'].isin(filtered_commodities)]

        # Group by year and sum the values for each year
        total_export_per_year = filtered_export_data.groupby('year')['value'].sum().reset_index()

        stock_data, company_list = find_stock_data(selected_sector)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=total_export_per_year['year'], y=total_export_per_year['value'], mode='lines+markers', name='Export', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=total_import_per_year['year'], y=total_import_per_year['value'], mode='lines+markers', name='Import', line=dict(color='orange')))
        fig.update_layout(title=f'Export and Import Valuation of {selected_sector} in ({2010}-{2021})',
                        xaxis_title='Year',
                        yaxis_title='Valuation')
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=stock_data[0]['year'], y=stock_data[0]['value'], mode='lines+markers', name=company_list[0], line=dict(color='green')))

        if len(stock_data) > 1 :
            fig1.add_trace(go.Scatter(x=stock_data[1]['year'], y=stock_data[1]['value'], mode='lines+markers', name= company_list[1], line=dict(color='black')))

        if len(stock_data) > 2 :
            fig1.add_trace(go.Scatter(x=stock_data[2]['year'], y=stock_data[2]['value'], mode='lines+markers', name=company_list[2], line=dict(color='red')))

        fig1.update_layout(title=f'Export and Import Valuation of {selected_sector} in ({2010}-{2021})',
                        xaxis_title='Year',
                        yaxis_title='Valuation')
        
        return render(request, 'trend_analysis.html', {'line_chart_html' : fig.to_html(), 'sector_values' : sector_df['Category'].unique(), 'selected_sector' : selected_sector, 'company_chart_html' : fig1.to_html(), 'company_values' : company_list})

    elif 'company' in request.GET :
        selected_sector = request.GET.get('sector', 'Construction')
        selected_company = request.GET.get('company')
        
        return render(request, 'trend_analysis.html', {'line_chart_html' : fig.to_html(), 'sector_values' : sector_df['Category'].unique(), 'selected_sector' : selected_sector, 'company_chart_html' : fig1.to_html(), 'company_values' : company_list, 'selected_company' : selected_company})
    
    else :
        return render(request, 'trend_analysis.html', {'sector_values' : sector_df['Category'].unique()})
    
    