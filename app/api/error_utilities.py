from pydantic import BaseModel
from typing import Any

class VideoTranscriptError(Exception):
    """Raised when a video transcript cannot be loaded. Used for tools which require video transcripts."""
    def __init__(self, message, url):
        self.message = message
        self.url = url
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"

class InputValidationError(Exception):
    """Raised when an input validation error occurs."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class LoaderError(Exception):
    """Raised when a tool module's loader function encounters an error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ToolExecutorError(Exception):
    """Raised when a tool executor encounters an error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ErrorResponse(BaseModel):
    """Base model for error responses."""
    status: int
    message: Any
    
    model_config = {
        "arbitrary_types_allowed": True
    }