import logging
from app.features.text_rewriter.tools import (
    load_metadata,
    create_input_schema,
    create_output_schema,
    rewrite_tool_handler,
    get_few_shot_examples
)
from typing import Dict

logger = logging.getLogger(__name__)

def execute_text_rewriter(text: str, instructions: str) -> Dict[str, str]:
    """
    Executes the text rewriting logic using the few-shot approach and tool handlers.

    Args:
        text (str): The input text to rewrite.
        instructions (str): The instructions for rewriting.

    Returns:
        Dict[str, str]: The rewritten text.
    """
    logger.info("Starting text rewriting task.")
    try:
        # Load metadata dynamically and create Pydantic schemas
        metadata = load_metadata()

        # Create input and output schemas dynamically
        InputModel = create_input_schema(metadata)
        OutputModel = create_output_schema(metadata)

        # Get few-shot examples
        few_shot_examples = get_few_shot_examples()

        # Prepare inputs for the rewrite tool handler
        inputs = {
            "text": text,
            "instructions": instructions,
        }

        # Call the rewrite tool handler with the inputs
        result = rewrite_tool_handler(inputs, few_shot_examples)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")