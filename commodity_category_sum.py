import pandas as pd

# Read the CSV files
import_export = "import"

# Assuming the input category is provided
input_category = "Meat and Fish"

categories_df = pd.read_csv('archive/categories.csv')
import_export_df = pd.read_csv(f'archive/2010_2021_HS2_{import_export}.csv')



# Filter commodities belonging to the given category
filtered_commodities = categories_df[categories_df['Category'] == input_category]['Commodity']

# Filter import data based on filtered commodities
filtered_import_export_data = import_export_df[import_export_df['Commodity'].isin(filtered_commodities)]


# Group by year and sum the values for each year
total_value_per_year = filtered_import_export_data.groupby('year')['value'].sum().reset_index()

# Display the resulting DataFrame
print(total_value_per_year)