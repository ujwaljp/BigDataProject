import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv("archive/unique_commodities.csv")

# Extract unique entries from the "Sector" column
unique_sectors = df['Sector'].unique()

# Print unique sector entries
print("Unique sector entries:")
for sector in unique_sectors:
    print(sector)
