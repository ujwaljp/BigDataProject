import pandas as pd

df = pd.read_csv('2010_2021_HS2_import.csv')

df = df.dropna(subset=['value'])
df = df[df['value'] != 0]

df.to_csv('2010_2021_HS2_import.csv', index = False)
