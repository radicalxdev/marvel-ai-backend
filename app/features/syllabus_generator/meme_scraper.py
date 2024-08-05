import requests
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


def get_web_results(self):
        # we scrap the link to find the tables components and store them in listes
        link = self.scrap_data()
        return pd.read_html(link)
 