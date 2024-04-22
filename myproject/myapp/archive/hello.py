def commodity_country_selection(request) :
    selected_commodity = request.GET.get('Commodity', 'RUSSIA')
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
        