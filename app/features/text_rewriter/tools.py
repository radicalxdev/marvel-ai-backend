from pydantic import BaseModel, create_model
import os
import json
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# Load environment variables
def load_api_credentials():
    """
    Load the credentials for Google API from environment variables.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), "text_rewriter.env")
    load_dotenv(dotenv_path=dotenv_path)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    project_id = os.getenv("PROJECT_ID")
    
    if not api_key or not project_id:
        raise ValueError("API key or project ID is missing in environment variables.")

    return api_key, project_id

def create_input_schema(metadata: dict):
    """
    Dynamically creates a Pydantic model for input validation based on metadata.json.

    Args:
        metadata (dict): Metadata defining the inputs.

    Returns:
        BaseModel: A Pydantic schema for input validation.
    """
    fields = {
        input_name: (str, ...) if input_spec["required"] else (str, None)
        for input_name, input_spec in metadata["inputs"].items()
    }
    return create_model(metadata["name"] + "InputSchema", **fields)

def create_output_schema(metadata: dict):
    """
    Dynamically creates a Pydantic model for output validation based on metadata.json.

    Args:
        metadata (dict): Metadata defining the outputs.

    Returns:
        BaseModel: A Pydantic schema for output validation.
    """
    fields = {
        output_name: (str, ...)
        for output_name, output_spec in metadata["outputs"].items()
    }
    return create_model(metadata["name"] + "OutputSchema", **fields)

def get_few_shot_examples() -> str:
    """
    Returns a string containing a set of few-shot examples for text rewriting tasks.
    """
    return (
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

def rewrite_tool_handler(inputs: dict, few_shot_examples: str):
    """
    Handles the text rewriting tool request by validating inputs and executing the model.

    Args:
        inputs (dict): The input data for text rewriting.
        few_shot_examples (str): The few-shot examples to guide the task.

    Returns:
        dict: The rewritten text.
    """
    try:
        metadata = load_metadata()  # Load the metadata
        validate_inputs(inputs, metadata)  # Validate inputs

        # Initialize the model and pipeline
        api_key, project_id = load_api_credentials()
        model = GoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_output_tokens=1024,
            api_key=api_key
        )

        prompt_template = PromptTemplate(
            template=(
                "{few_shot_examples}\n"
                "Task: {instructions}\n\n"
                "Text: {text}\n\n"
                "Respond with a JSON object containing only the key 'rewritten_text' and its value."
            ),
            input_variables=["instructions", "text", "few_shot_examples"]
        )

        output_parser = JsonOutputParser(pydantic_object=dict)

        # Combine components into the pipeline
        pipeline = prompt_template | model | output_parser

        # Prepare input for the model
        inputs["few_shot_examples"] = few_shot_examples

        # Execute the pipeline and return the result
        result = pipeline.invoke(inputs)
        
        return {"rewritten_text": result.get("rewritten_text", "No rewritten text found")}

    except Exception as e:
        raise ValueError(f"Error in rewrite_tool_handler: {str(e)}")

def load_metadata():
    """
    Loads metadata from the metadata.json file.

    Returns:
        dict: The metadata for the text rewriter tool.
    """
    METADATA_FILE = os.path.join(os.path.dirname(__file__), "metadata.json")
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

def validate_inputs(inputs: dict, metadata: dict):
    """
    Validates the inputs using the provided metadata.

    Args:
        inputs (dict): The input data to validate.
        metadata (dict): The metadata that defines the valid inputs.

    Raises:
        ValueError: If validation fails.
    """
    for input_key, input_spec in metadata["inputs"].items():
        if input_spec["required"] and input_key not in inputs:
            raise ValueError(f"Missing required input: {input_key}")
        if input_key in inputs and not isinstance(inputs[input_key], str):
            raise ValueError(f"Invalid type for input '{input_key}'. Expected: {input_spec['type']}")