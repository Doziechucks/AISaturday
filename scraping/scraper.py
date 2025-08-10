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


def text_or_none(el):
    return el.get_text(strip=True) if el else None

def parse_transfers(table):
    if not table:
        return []
    transfers = []
    for row in table.select("tr.odd, tr.even"):
        # get all tds to choose by position if needed
        tds = row.find_all('td')
        try:
            # safer ways to grab cells
            name_el = row.find('td', class_='hauptlink')
            name = text_or_none(name_el)

            pos_el = row.find('td', class_='inline-table')
            position = text_or_none(pos_el)

            # better: pick the exact td index for age if class ambiguous
            age = None
            if len(tds) > 3:
                age_str = tds[3].get_text(strip=True)  # adjust index
                try:
                    age = int(re.sub(r'\D','', age_str))
                except:
                    age = None

            img = row.find('img', class_='flaggenrahmen')
            nationality = img.get('title') if img else 'N/A'

            fee_td = row.find_all('td', class_='rechts')
            fee_text = fee_td[0].get_text(strip=True) if fee_td else ''

            # normalize fee (very simple)
            fee = 'N/A'
            if 'loan' in fee_text.lower():
                fee = 'Loan'
            elif 'free' in fee_text.lower():
                fee = 'Free'
            else:
                cleaned = re.sub(r'[^\d.,kKmM]', '', fee_text)
                fee = cleaned if cleaned else 'N/A'

            transfers.append({
                'Name': name,
                'Position': position,
                'Age': age,
                'Nationality': nationality,
                'Fee': fee
            })
        except Exception as e:
            # log or print e for debugging
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

print(response.status_code)
print(response.text[:1200])

# Optional: Print sample data
print("\nSample transfer data:")
print(df_transfers.head())