import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, simpledialog, OptionMenu

# Function to scrape stock data from Moneycontrol
def scrape_stock_data(url, type):
    # Send an HTTP request to the URL
    response = requests.get(url)
    if type=="Sector":
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table containing company data
        table = soup.find("table", class_="tbldata14 bdrtpg")

        # Create a set to store unique industries
        unique_stocks = set()

        # Extract company names and industries
        for row in table.find_all("tr")[1:]:  # Skip the header row
            columns = row.find_all("td")
            company_name = columns[0].text.strip()
            # industry = columns[1].text.strip()
            unique_stocks.add(company_name)
        return unique_stocks
    else:
        span_class = "ReuseTable_gld13__HzxFN undefined"

        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find all span elements with the specified class
            spans = soup.find_all("span", {"class": span_class})

            # Create a set to store unique industries
            unique_stocks = set()

            # Extract and print the company names and links
            for span in spans:
                # Extract company name
                company_name = span.find('a').text.strip() if span.find('a') else span.text.strip()
                
                # Extract link if available
                link = span.find('a')['href'] if span.find('a') else None
                
                unique_stocks.add(company_name)
            return unique_stocks
        else:
            print("Failed to retrieve the webpage.")

# Function to handle commodity selection
def select_hscode(hscode):
    # Read corresponding CSV file
    if choice.lower() == 'import':
        file_name = 'archive/2010_2021_HS2_import.csv'
    elif choice.lower() == 'export':
        file_name = 'archive/2010_2021_HS2_export.csv'
    else:
        print("Invalid choice. Please enter 'import' or 'export'.")
        return

    # Read CSV files into DataFrames
    commodities_df = pd.read_csv('archive/unique_commodities.csv')
    data_df = pd.read_csv(file_name)

    # Merge DataFrames based on commodity column
    merged_df = pd.merge(commodities_df, data_df, on='Commodity', how='inner')

    # Remove rows with blank entries
    merged_df.dropna(inplace=True)

    # Filter merged DataFrame based on selected commodity
    selected_df = merged_df[merged_df['HSCode'] == hscode]

    # Iterate through filtered DataFrame
    for index, row in selected_df.iterrows():
        print(row["Commodity"])
        if row['Sector']=="NAN":
            url = f"https://www.moneycontrol.com/stocks/marketstats/industry-classification/nse/{row['Industries']}.html"
            stock_list = scrape_stock_data(url, "Industries")
            print(f"Stocks in {row['Industries']} industry:")
            print(', '.join(stock_list))
        elif row['Industries']=="NAN":
            url = f"https://www.moneycontrol.com/india/stockmarket/sector-classification/marketstatistics/nse/{row['Sector']}.html?classic=true"
            stock_list = scrape_stock_data(url, "Sector")
            print(f"Stocks in {row['Sector']} sector:")
            print(', '.join(stock_list))
        else:
            print("No missing data found.")
        break

# Prompt user to select import or export
root = Tk()
root.withdraw()
choice = simpledialog.askstring("Input", "Enter 'import' or 'export': ")

# Prompt user to input HSCode value
hscode = simpledialog.askinteger("Input", "Enter an HSCode value between 0 and 98: ", minvalue=0, maxvalue=98)

# Call select_hscode function with selected HSCode
select_hscode(hscode)