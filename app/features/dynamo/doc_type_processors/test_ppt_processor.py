# test_ppt_processor.py
import pandas as pd
from ppt_processor import PPTProcessor
from langchain_google_vertexai import VertexAI  # Make sure this import is correct or mock it

# Mock the VertexAI object if not available
class MockVertexAI:
    pass

# Replace 'your_ppt_file.pptx' with the path to your actual PPT file
ppt_file_path = 'mips_tutorial.ppt'
model = MockVertexAI()

# Initialize the PPTProcessor
processor = PPTProcessor(file_path=ppt_file_path, model=model)

# Read the PPT file
df = processor.read_ppt()

# Print the DataFrame
print(df)

# Generate and print the summary
summary = processor.generate_summary(df)
print("Summary:\n", summary)

# Example summary, examples, and format_instructions for generating flashcards
examples = '[{"concept": "Example Concept", "definition": "Example Definition"}]'
format_instructions = '{"concept": "string", "definition": "string"}'
flashcards = processor.generate_flashcards(summary, examples, format_instructions)

# Print the generated flashcards
for flashcard in flashcards:
    print(flashcard.json())

