from fastapi import APIRouter, HTTPException
from .core import executor
from .tools import TextRewriterInput, TextRewriterOutput

router = APIRouter()

@router.post("/rewrite", response_model=TextRewriterOutput)
def rewrite_text(input: TextRewriterInput):
    """
    API endpoint to rewrite text based on user instructions.
    """
    try:
        result = executor(input.text, input.instructions)
        return TextRewriterOutput(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))