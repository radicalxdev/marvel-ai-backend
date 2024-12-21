import os
import pytest
from app.tools.notes_generator.core import executor


def test_executor_notes_valid():
    notes = executor(
                topic="Machine Learning",
                nb_columns=4,
                details="information about Machine Learning",
                orientation="portrait",
                file_urls="https://www.interactions.com/wp-content/uploads/2017/06/machine_learning_wp-5.pdf,https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
                file_types="pdf,pdf",
                langs="en,en"
                )
    assert isinstance(notes, dict)


def test_executor_notes_invalid():
    with pytest.raises(ValueError) as exc_info:
        nnotes = executor(
                topic="Machine Learning",
                nb_columns=4,
                details="information about Machine Learning",
                orientation="portrait",
                file_urls="https://www.interactions.com/wp-content/uploads/2017/06/machine.pdf",
                file_types="pdf,pdf",
                langs="en,en"
                )

    assert isinstance(exc_info.value, ValueError)