import csv

import requests
from bs4 import BeautifulSoup

# Base URL with a placeholder for the page number
base_url = "https://factcheck.afp.com/list/all/all/all/38558/19?page="

# Define the range of pages you want to scrape
start_page = 1
end_page = 70  # Change this to the last page you want to scrape

# Create an empty dictionary to store the data
data_dict = {}

for page_number in range(start_page, end_page + 1):
    # Construct the URL for the current page
    url = f"{base_url}{page_number}"

    # Make an HTTP request and create a BeautifulSoup object
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the webpage for page {page_number}.")
        continue  # Skip to the next page if the request fails

    # Find all <div> elements with class "card"
    card_divs = soup.find_all('div', class_='card')

    # Find all <h2> elements with class "h4 card-title"
    h2_elements = soup.find_all('h2', class_='h4 card-title')

    # Loop through each "card" div and "h4 card-title" h2
    for i in range(min(len(card_divs), len(h2_elements))):
        card_div = card_divs[i]
        h2_element = h2_elements[i]

        # Extract the links from the "card" div
        links = card_div.find_all('a')
        for link in links:
            href = link.get('href')
            abs_href = 'https://factcheck.afp.com' + href # get the absolute path 

        # Extract the text from the "h4 card-title" h2
        raw_title_text = h2_element.text
        title_text = raw_title_text.strip() #remove leading and trailing whitespace

        title_text_low = title_text.lower()
        if "video" in title_text_low or "clip" in title_text_low or "photo" in title_text_low or "footage" in title_text_low or "image" in title_text_low or "picture" in title_text_low:
            continue


        # Store the data in the dictionary with title text as the key and link as the value
        data_dict[title_text] = abs_href

# # Print or manipulate the data dictionary as needed
# for title_text, link in data_dict.items():
#     print(f"Title Text: {title_text} - Link: {link}")

csv_file = 'data_africa.csv'

# Extract keys and values as rows
rows = [(key, value) for key, value in data_dict.items()]

with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the rows
    writer.writerows(rows)