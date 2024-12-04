import os
import pytest
from app.features.notes_generator.core import executor
# from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import NotesGeneratorArgs

def test_executor_notes_valid():
    notes_generator_args = NotesGeneratorArgs(
             topic = "Machine Learning",
             nb_columns =  4,
             details = "information about Machine Learning",
             orientation = "portrait",
             givenfileslist = [
                {
                "file_url":"https://www.interactions.com/wp-content/uploads/2017/06/machine_learning_wp-5.pdf",
                "file_type":"pdf",
                "lang":"en"
                }
             ]
    )
    notes = executor(notes_generator_args)

    assert isinstance(notes, str), "full_path must be a string"
    assert os.path.exists(notes), f"full_path does not exist: {notes}"
    assert os.path.getsize(notes) > 0, "PDF file is empty"


def test_executor_notes_invalid():
    notes_generator_args = NotesGeneratorArgs(
             topic = "Machine Learning",
             nb_columns =  4,
             details = "information about Machine Learning",
             orientation = "portrait",
             givenfileslist = [
                {
                "file_url":"https://www.interaction.com/wp-content/uploads/2017/06/machine.pdf",
                "file_type":"pdf",
                "lang":"en"
                }
             ]
    )
    with pytest.raises(ValueError) as exc_info:
        notes = executor(notes_generator_args)

    assert isinstance(exc_info.value, ValueError)