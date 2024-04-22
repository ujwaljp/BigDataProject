import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, simpledialog

# Function to check if a URL exists
def url_exists(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Function to scrape stock data from Moneycontrol
def scrape_stock_data(url,type):
    # Send an HTTP request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table containing company data
    if(type=="sector"):
        table = soup.find("table", class_="tbldata14 bdrtpg")
    else:
        table1 = soup.find("div", class_="ReuseTable_bsr_table__eVZZf")
        table = table1.find("table")

    # Create a set to store unique companies
    unique_stocks = set()

    # Extract company names
    for row in table.find_all("tr")[1:]:  # Skip the header row
        columns = row.find_all("td")
        company_name = columns[0].text.strip()
        unique_stocks.add(company_name)
        
    return unique_stocks

# Function to handle commodity selection
def select_hscode(choice):
    file_name = 'sectors.csv'

    merged_df = pd.read_csv(file_name)

    # Combine stock lists
    combined_stock_list = set()

    # Filter merged DataFrame based on HSCode
    selected_df = merged_df
    # Iterate through filtered DataFrame
    for index, row in selected_df.iterrows():
        url = f"https://www.moneycontrol.com/india/stockmarket/sector-classification/marketstatistics/nse/{row['Sector']}.html?classic=true"
        if url_exists(url):
            stock_list = scrape_stock_data(url,"sector")
            combined_stock_list.update(stock_list)
        else:
            print(f"URL {url} does not exist.")
        break
    # Write combined stock list to a file
    with open(choice + '_data.txt', 'w') as file:
        for stock in combined_stock_list:
            file.write(stock + '\n')

    print("Combined stock list written to combined_stock_list.txt")

# Prompt user to select import or export
root = Tk()
root.withdraw()
choice = simpledialog.askstring("Input", "Enter 'import' or 'export': ")

# Call select_hscode function with selected choice
select_hscode(choice)
