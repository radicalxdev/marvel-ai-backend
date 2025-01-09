import os
import json
import subprocess
from pathlib import Path

def run_tests_for_tool(tool_id):
    """
    Runs pytest for a specific tool identified by its ID if it has a "tests_folder" attribute and specified "available_tests".

    Args:
        tool_id (str): ID of the tool to run tests for.

    Returns:
        None
    """
    # Path to the tools configuration JSON file
    config_path = Path(__file__).parent / "tools_config.json"

    # Load the configuration file
    with open(config_path, 'r') as config_file:
        tools_config = json.load(config_file)

    # Replace '-' with '_' in tool_id for internal use
    internal_tool_id = tool_id.replace('-', '_')

    # Find the tool by ID
    tool_info = tools_config.get(tool_id)
    if not tool_info:
        print(f"Tool with ID '{tool_id}' not found in configuration.")
        return

    # Check if the tool has a "tests_folder" and "available_tests"
    tests_folder = tool_info.get("tests_folder")
    available_tests = tool_info.get("available_tests", [])

    if tests_folder and available_tests:
        # Construct the absolute path to the tests folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tests_path = os.path.abspath(os.path.join(base_dir, '..', internal_tool_id, tests_folder))

        if os.path.exists(tests_path):
            print(f"Running tests for {tool_id} in {tests_path}...")
            for test_file in available_tests:
                test_file_path = os.path.join(tests_path, test_file)
                if os.path.exists(test_file_path):
                    print(f"Running {test_file}...")
                    try:
                        # Run pytest for the specific test file
                        subprocess.run(["pytest", test_file_path], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Tests in {test_file} failed with exit code {e.returncode}")
                else:
                    print(f"Test file {test_file} not found at {test_file_path}")
        else:
            print(f"Tests folder for {tool_id} not found at {tests_path}")
    else:
        print(f"Tool '{tool_id}' does not have a 'tests_folder' or 'available_tests' defined in the configuration.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_tests_util.py <tool_id>")
    else:
        # Get the tool ID from the command-line arguments
        tool_id = sys.argv[1]

        # Run the tests for the specified tool
        run_tests_for_tool(tool_id)
