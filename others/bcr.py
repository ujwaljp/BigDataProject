import pandas as pd
import bar_chart_race as bcr

# Read the dataset
df = pd.read_csv('2010_2021_HS2_export.csv')  # Replace 'your_dataset.csv' with the path to your dataset file

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
