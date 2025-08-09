import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# URL for Arsenal's latest transfers
url = "https://www.transfermarkt.com/fc-arsenal/transfers/verein/11/saison_id/2023"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')


def parse_transfers(table):
    transfers = []
    for row in table.find_all('tr', class_=['odd', 'even']):
        try:
            name = row.find('td', class_='hauptlink').get_text(strip=True)
            position = row.find('td', class_='inline-table').get_text(strip=True)
            age = row.find('td', class_='zentriert').get_text(strip=True)
            nationality = row.find('img', class_='flaggenrahmen')['title']
            fee_text = row.find_all('td', class_='rechts')[0].get_text(strip=True)


            if 'loan' in fee_text.lower():
                fee = 'Loan'
            elif 'free' in fee_text.lower():
                fee = 'Free'
            elif 'End of loan' in fee_text:
                fee = 'Loan Return'
            else:
                fee = re.sub(r'[^\d.]', '', fee_text) + 'm' if fee_text else 'N/A'

            transfers.append({
                'Name': name,
                'Position': position,
                'Age': int(age),
                'Nationality': nationality,
                'Fee': fee
            })
        except (AttributeError, TypeError):
            continue
    return transfers


# Extract arrivals
arrivals_table = soup.find('div', id='yw1').find('table', class_='items')
arrivals = parse_transfers(arrivals_table)

# Extract departures
departures_table = soup.find('div', id='yw2').find('table', class_='items')
departures = parse_transfers(departures_table)

# Create DataFrames
df_arrivals = pd.DataFrame(arrivals)
df_departures = pd.DataFrame(departures)

# Add transfer type columns
df_arrivals['Transfer_Type'] = 'Arrival'
df_departures['Transfer_Type'] = 'Departure'

# Combine data
df_transfers = pd.concat([df_arrivals, df_departures], ignore_index=True)

# Save to CSV
df_transfers.to_csv('arsenal_transfers_2023.csv', index=False)
print("Transfer data saved to 'arsenal_transfers_2023.csv'")

# Optional: Print sample data
print("\nSample transfer data:")
print(df_transfers.head())