from pydantic import BaseModel

# Input Schema
class TextRewriterInput(BaseModel):
    text: str
    instructions: str

# Output Schema
class TextRewriterOutput(BaseModel):
    original_text: str
    rewritten_text: str