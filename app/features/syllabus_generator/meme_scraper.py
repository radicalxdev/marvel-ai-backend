import requests
from bs4 import BeautifulSoup
from tools import Search_engine
import pd 

def scrap_data():
        url = 'https://www.googleapis.co m/customsearch/v1'

        params = {
            'q': f'Memes of {Search_engine.grade} {Search_engine.subject}',
            'key': Search_engine.API_KEY,
            'cx': Search_engine.SEARCH_ENGINE_ID
        }

        response = requests.get(url,params=params).json()
        links = [item['link'] for item in response['items']]
        return links[0]


def get_web_results():
    # Scrap the link to find image components
    link = scrap_data()
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image tags and extract their 'src' attributes
    images = []
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            images.append(img_url)

    return images