
from app.features.syllabus_generator.core import executor
import os 

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'abolute file path'

def test_executor():
    assert executor 