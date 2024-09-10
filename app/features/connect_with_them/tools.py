import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from langchain import hub
from langchain.agents import AgentExecutor,create_react_agent,tool
from langchain_core.prompts import PromptTemplate
from langchain.tools.base import StructuredTool
from langchain_groq import ChatGroq
# from langchain_core.tools import Tool , StructuredTool
#from langchain_google_vertexai import VertexAI
#model = VertexAI(model_name='gemini-1.5-flash', temperature=0.1) #gemini-pro
from langchain.pydantic_v1 import BaseModel, Field
from Credentials import credentials,categories_mapping
from prompt.Prompts import Prompt_query

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import Literal
# import html2markdown

model_name = 'llama-3.1-70b-versatile'

llm = ChatGroq(model=model_name,temperature=0.5,api_key=credentials['GROQ_API_KEY'])

class GetSubredditsModel(BaseModel):
    Topic: str = Field(description='Topic that you want to get subreddits for')
class ScrapePageModel(BaseModel):
    category: str = Field(description='Category that you want to get some information about')

def get_subreddits(topic:str ,limit:int=10 ):
    params = {'q': topic, 'type': 'sr', 'sort': 'relevance', 'limit': limit}
    data = {'grant_type': 'password', 'username': credentials['NAME'], 'password': credentials['PASSWORD']}
    headers = {'User-Agent': credentials['USER_AGENT']}
    try:
        auth = HTTPBasicAuth(credentials['CLIENT_ID'], credentials['CLIENT_SECRET'])
        res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
        res.raise_for_status()
        token = res.json()['access_token']
        headers['Authorization'] = f'bearer {token}'
        response = requests.get('https://oauth.reddit.com/subreddits/search', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()['data']['children']
        subreddits = [post['data']['display_name'] for post in data]
        return f"These are the subreddits related to '{topic}': {', '.join(subreddits)}"
    except RequestException as e:
        print(f"An error occurred during the request: {e}")
        return f"No subreddits found for '{topic}'. Error: {str(e)}"
#! this function should be fixed not always work
def scrape_page(category:str ):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(f"https://www.edutopia.org/{categories_mapping[category]}")

    driver.implicitly_wait(4)
    try:
        first_image = driver.find_element(By.TAG_NAME, "img")
    except NoSuchElementException:
        print("First image not found. Continuing...")
        driver.quit()
        return

    try:
        parent_element = first_image.find_element(By.XPATH, '..')
        parent_element.click()
    except NoSuchElementException:
        print("Parent element of the image not found. Continuing...")
        driver.quit()
        return

    driver.implicitly_wait(2)

    try:
        close_button = driver.find_element(By.XPATH, "//button[text()='Close']")
        close_button.click()
    except NoSuchElementException:
        print("Close button not found. Skipping...")

    try:
        body = driver.find_element(By.TAG_NAME, "body").get_attribute('innerHTML')
    except NoSuchElementException:
        print("Body content not found. Continuing...")
        driver.quit()
        return

    soup = BeautifulSoup(body, 'html.parser')

    for tag in soup(['style', 'script']):
        tag.decompose()

    paragraphs = soup.find_all('p')
    try:
        result = '/n'.join([p.get_text(strip=True) for p in paragraphs])
        return result
    except Exception as e:
        return "No content found"
    finally:
        driver.quit()

tools = [
    StructuredTool.from_function(
        name='Get subreddits',
        func=get_subreddits,
        description= '''Get a List of subreddits about a certain topic ,
        this tool is useful when you want to suggest a list of subreddits in the end of a response to visit for more information about a topic
        it takes a Topic as argument''',
        args_schema= GetSubredditsModel
    ),
    # StructuredTool.from_function(
    #     name='scrape_page',
    #     func=scrape_page,
    #     description= f'''Get a some informations about a certain category from edutopia website ,
    #     this tool is useful when you want to have more informations from the web about a certain teaching category that is included in {list(categories_mapping.keys())}
    #     it takes a category as argument''',
    #     args_schema= ScrapePageModel
    # )
]

prompt = hub.pull("hwchase17/react") #structured-chat-agent
agent = create_react_agent(llm,tools,prompt)

Agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors="Check your output formatting, ensure correct syntax.",
    max_iterations=6
)

# user_input = 'I teach data analysis to undergrade students from new york and they love memes and music'

# result = Agent_executor.invoke({'input':Prompt_query(user_input)})

# print(result['output'])
