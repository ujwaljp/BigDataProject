import pandas as pd
import bar_chart_race as bcr
df = pd.read_csv('2010_2021_HS2_export.csv')
# Assuming df contains your data
# Group by year and country to get the total export value for each country in each year
df_grouped = df.groupby(['year', 'country'])['value'].sum().reset_index()

# Pivot the data to have years as index and countries as columns
df_pivot = df_grouped.pivot(index='year', columns='country', values='value').fillna(0)

# Get the top 10 countries for each year
top_10_countries = df_pivot.sum().nlargest(10).index.tolist()

# Filter the DataFrame to include only the top 10 countries
df_filtered = df_pivot[top_10_countries]

# Create the bar chart race
bcr.bar_chart_race(df=df_filtered, filename='export_values_race.mp4', n_bars=10, title='Top 10 Exporting Countries', steps_per_period=10, period_length=1000)

