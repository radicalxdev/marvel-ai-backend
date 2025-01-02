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

def create_text_rewriter_pipeline(few_shot_examples: str):
    """
    Initializes the LangChain pipeline for text rewriting with enforced JSON output and a few-shot learning approach.
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

    # Update the prompt template to include examples
    prompt_template = PromptTemplate(
        template=(
            "{few_shot_examples}\n"
            "Task: {instructions}\n\n"
            "Text: {text}\n\n"
            "Respond with a JSON object containing only the key 'rewritten_text' and its value."
        ),
        input_variables=["instructions", "text", "few_shot_examples"]
    )

    # Define the output parser
    output_parser = JsonOutputParser(pydantic_object=dict)

    # Combine the components into a pipeline
    return prompt_template | gemini_model | output_parser


def execute_text_rewriter(text: str, instructions: str) -> Dict[str, str]:
    """
    Executes the text rewriting logic using the few-shot approach.

    Args:
        text (str): The input text to rewrite.
        instructions (str): The instructions for rewriting.

    Returns:
        Dict[str, str]: The rewritten text.
    """
    logger.info("Starting text rewriting task.")
    try:
        # Few-shot examples that demonstrate how text rewriting should work
        few_shot_examples = (
            "Example 1: \n"
            "Text: 'The causes of the American Civil War were complex, including economic differences, the issue of slavery, and the election of Abraham Lincoln.'\n"
            "Instructions: 'Rewrite the text in simpler terms.'\n"
            "Rewritten Text: 'The American Civil War happened because of many reasons, such as different economies in the North and South, slavery, and the election of Abraham Lincoln.'\n\n"

            "Example 2: \n"
            "Text: 'Photosynthesis is the process by which plants use sunlight to synthesize foods from carbon dioxide and water.'\n"
            "Instructions: 'Summarize the key points of the text.'\n"
            "Rewritten Text: 'Photosynthesis is how plants make food from sunlight, carbon dioxide, and water.'\n\n"

            "Example 3: \n"
            "Text: 'In the history of mathematics, there are several key figures such as Euclid, Isaac Newton, and Carl Friedrich Gauss, who contributed to the foundations of geometry and calculus.'\n"
            "Instructions: 'Make the text shorter and focus on the key points.'\n"
            "Rewritten Text: 'Important mathematicians like Euclid, Newton, and Gauss helped develop geometry and calculus.'\n\n"

            "Example 4: \n"
            "Text: 'The mitochondria are often called the powerhouses of the cell because they generate most of the cell's energy.'\n"
            "Instructions: 'Explain the concept in simple terms.'\n"
            "Rewritten Text: 'Mitochondria are the parts of cells that produce energy.'\n\n"

            "Example 5: \n"
            "Text: 'A balanced diet is crucial for maintaining health, and it should include a variety of foods such as vegetables, fruits, proteins, and carbohydrates.'\n"
            "Instructions: 'Rewrite the text in a more concise manner.'\n"
            "Rewritten Text: 'A healthy diet includes a mix of vegetables, fruits, proteins, and carbs.'\n\n"
        )


        # Initialize the pipeline, passing in the few-shot examples
        pipeline = create_text_rewriter_pipeline(few_shot_examples)
        
        # Prepare inputs
        inputs = {
            "instructions": instructions,
            "text": text,
            "few_shot_examples": few_shot_examples
        }
        
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