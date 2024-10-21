import os
import pytest
from app.features.rubric_generator.core import executor
# from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import RubricGeneratorArgs

def test_executor_rubric_valid():
    rubric_generator_args = RubricGeneratorArgs(
             standard = "To make an ensemble Machine Learning model",
             point_scale = 4,
             grade_level = "college",
             file_type = "pdf",
             lang = "en",
             file_url = "https://raw.githubusercontent.com/asleem/uploaded_files/main/assignment_build_LM.pdf"
    )

    rubric = executor(rubric_generator_args)

    assert isinstance(rubric, str), "full_path must be a string"
    assert os.path.exists(rubric), f"full_path does not exist: {rubric}"
    assert os.path.getsize(rubric) > 0, "PDF file is empty"


    

def test_executor_rubric_invalid():
    rubric_generator_args = RubricGeneratorArgs(
             standard = "To make an ensemble Machine Learning model",
             point_scale = 4,
             grade_level = "college",
             file_type = "pdf",
             lang = "en",
             file_url = "https://raw.githubusercontent.com/asleem/uploaded_files/main/assignment_build.pdf"
    )

    with pytest.raises(ValueError) as exc_info:
        rubric = executor(rubric_generator_args)

    assert isinstance(exc_info.value, ValueError)