import pandas as pd

df = pd.read_csv('2010_2023_HS2_export.csv')

df = df.dropna(subset=['value'])
df['value'] = df['value'].astype(float) 
df = df[df['value'] != 0]
print(type(df['value'][0]))

df.to_csv('2010_2023_HS2_export.csv', index = False)
