import requests
from bs4 import BeautifulSoup
from tools import Search_engine
import pandas as pd

# Function to scrape data from Google Custom Search API
def scrap_data():
    # URL for the Google Custom Search API
    url = 'https://www.googleapis.com/customsearch/v1'

    # Parameters for the API request
    params = {
        'q': f'Memes of {Search_engine.grade} {Search_engine.subject}',  # Query for memes related to a specific grade and subject
        'key': Search_engine.API_KEY,  # API key for authentication
        'cx': Search_engine.SEARCH_ENGINE_ID  # Search engine ID
    }

    # Send a GET request to the API and get the JSON response
    response = requests.get(url, params=params).json()
    
    # Extract links from the response items
    links = [item['link'] for item in response['items']]
    
    # Return the first link
    return links[0]

# Function to get web results from the scraped link
def get_web_results():
    # Scrap the link to find image components
    link = scrap_data()  # Get the link from the scrap_data function
    response = requests.get(link)  # Send a GET request to the link
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

    # Find all image tags and extract their 'src' attributes
    images = []
    for img in soup.find_all('img'):
        img_url = img.get('src')  # Get the 'src' attribute of each image tag
        if img_url:
            images.append(img_url)  # Append the image URL to the images list

    return images  # Return the list of image URLs