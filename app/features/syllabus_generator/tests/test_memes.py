from app.features.syllabus_generator.tools import Meme_generator_with_reddit, Meme_generator_with_scraper
from app.features.syllabus_generator import credentials
import pytest


Meme_Generator = Meme_generator_with_reddit(
        'Civil Engineering',
        credentials['client_id'],
        credentials['client_secret'],
        credentials['user_agent'],
        credentials['username'],
        credentials['password']
)

@pytest.mark.skip(reason="Skipping this test we don't use it")
def test_meme_generator_with_scraper():
    Meme_Generator = Meme_generator_with_scraper(
        'University',
        'Civil Engineering',
        credentials['api_key'],
        credentials['search_engine_id']
    )
    result = Meme_Generator.scrap_data()
    assert result
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)

def test_meme_generator_with_reddit():
    result = Meme_Generator.get_memes()
    print(result)
    assert isinstance(result, list)
    if result:
        assert all(isinstance(item, str) for item in result)
        assert all(item.endswith(('jpg', 'jpeg', 'png', 'gif')) for item in result)
