
from app.features.syllabus_generator.core import executor
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

def test_executor():
    assert executor 