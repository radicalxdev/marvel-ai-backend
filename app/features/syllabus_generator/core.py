from app.features.syllabus_generator.tools import SyllabusGenerator
from app.services.logger import setup_logger
import os

logger = setup_logger()

def executor(grade_level: str, subject: str, verbose=True):
    output = SyllabusGenerator(grade_level, subject)
    result = output.compile()
    if verbose:
        print(result)
    return result
