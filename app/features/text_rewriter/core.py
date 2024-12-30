import json  
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict
import logging
from dotenv import load_dotenv
import os

# Dynamically determine the path to the .env file relative to the current file
dotenv_path = os.path.join(os.path.dirname(__file__), "text_rewriter.env")

# Load environment variables from the .env file
load_dotenv(dotenv_path=dotenv_path)

# Load API key and project ID from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
project_id = os.getenv("PROJECT_ID")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")
if not project_id:
    raise ValueError("PROJECT_ID environment variable is not set.")

logger = logging.getLogger(__name__)

def create_text_rewriter_pipeline():
    """
    Initializes the LangChain pipeline for text rewriting with enforced JSON output.
    """
    # Load API key from environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    # Initialize the model with the API key
    gemini_model = GoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7,
        max_output_tokens=1024,
        api_key=api_key,  # Pass the API key
    )

    # Update the prompt template to enforce JSON response
    prompt_template = PromptTemplate(
        template=(
            "Task: {instructions}\n\n"
            "Text: {text}\n\n"
            "Respond with a JSON object containing only the key 'rewritten_text' and its value."
        ),
        input_variables=["instructions", "text"]
    )

    # Define the output parser
    output_parser = JsonOutputParser(pydantic_object=dict)

    # Combine the components into a pipeline
    return prompt_template | gemini_model | output_parser


def execute_text_rewriter(text: str, instructions: str) -> Dict[str, str]:
    """
    Executes the text rewriting logic.

    Args:
        text (str): The input text to rewrite.
        instructions (str): The instructions for rewriting.

    Returns:
        Dict[str, str]: The rewritten text.
    """
    logger.info("Starting text rewriting task.")
    try:
        # Initialize the pipeline
        pipeline = create_text_rewriter_pipeline()
        
        # Prepare inputs
        inputs = {"instructions": instructions, "text": text}
        
        # Invoke the pipeline and get results
        result = pipeline.invoke(inputs)

        # Log raw output
        logger.info(f"Raw model output: {result}")

        # If the result is already a dictionary, return it directly
        if isinstance(result, dict):
            return {"rewritten_text": result.get("rewritten_text", "No rewritten text found")}

        # Otherwise, attempt to parse as JSON
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON output: {result}")
            raise RuntimeError("Failed to rewrite text: Invalid JSON output.")

        # Return the parsed response
        return {"rewritten_text": parsed_result["rewritten_text"]}
    
    except Exception as e:
        logger.error(f"Error during text rewriting: {str(e)}")
        raise RuntimeError(f"Failed to rewrite text: {str(e)}")