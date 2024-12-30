from app.features.text_rewriter.core import execute_text_rewriter
import os
import json
from pydantic import BaseModel, create_model

def create_input_model(metadata: dict):
    """
    Dynamically creates a Pydantic model for input validation based on metadata.json.

    Args:
        metadata (dict): Metadata defining the inputs.

    Returns:
        BaseModel: A Pydantic model.
    """
    fields = {
        input_name: (str, ...) if input_spec["required"] else (str, None)
        for input_name, input_spec in metadata["inputs"].items()
    }
    return create_model(metadata["name"] + "InputModel", **fields)

def create_output_model(metadata: dict):
    """
    Dynamically creates a Pydantic model for output validation based on metadata.json.

    Args:
        metadata (dict): Metadata defining the outputs.

    Returns:
        BaseModel: A Pydantic model.
    """
    fields = {
        output_name: (str, ...)
        for output_name, output_spec in metadata["outputs"].items()
    }
    return create_model(metadata["name"] + "OutputModel", **fields)

# Load metadata.json
METADATA_FILE = os.path.join(os.path.dirname(__file__), "metadata.json")

def load_metadata():
    """
    Loads the metadata.json file for the text_rewriter tool.
    """
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

# Validate inputs dynamically
def validate_inputs(inputs: dict, metadata: dict):
    """
    Validates inputs against metadata.json.

    Args:
        inputs (dict): Input data to validate.
        metadata (dict): Metadata defining required inputs.

    Raises:
        ValueError: If validation fails.
    """
    for input_key, input_spec in metadata["inputs"].items():
        if input_spec["required"] and input_key not in inputs:
            raise ValueError(f"Missing required input: {input_key}")
        if input_key in inputs and not isinstance(inputs[input_key], str):
            raise ValueError(f"Invalid type for input '{input_key}'. Expected: {input_spec['type']}")

# Tool handler for text rewriting
def rewrite_tool_handler(inputs: dict):
    """
    Handles the text rewriting tool request.

    Args:
        inputs (dict): Inputs for the text_rewriter tool.

    Returns:
        dict: The rewritten text.
    """
    metadata = load_metadata()
    validate_inputs(inputs, metadata)  # Validate inputs dynamically
    return execute_text_rewriter(inputs["text"], inputs["instructions"])