from app.assistants.classroom_support.essay_grading_assistant.assistant import run_essay_grading_assistant
from app.services.assistant_registry import Message, UserInfo
from app.services.logger import setup_logger
from app.services.schemas import (
    ChatMessage
)

logger = setup_logger()
"""
Essay Grading Inputs:
    grade_level: str,
    point_scale: str,
    assignment_description: str,
    rubric_objectives: str,
    rubric_objectives_file_url: str,
    rubric_objectives_file_type: str,
    writing_to_review: str,
    writing_to_review_file_url: str,
    writing_to_review_file_type: str,
    lang: str,
"""

def executor(
        user_info: UserInfo,
        messages: list[Message]=None, 
        k=3
    ):
    
    logger.info(f"Generating response from Essay Grading Assistant")

    chat_context_list = [
        ChatMessage(
            role=message.role, 
            type=message.type, 
            text=(
                # Symbolic prompt to represent the arguments dictionary for Essay Grading Pipeline. Its only purpose is to maintain comprehensibility of the context string.
                "Generate essay grading with these arguments: " + str(message.payload.text)
                if isinstance(message.payload.text, dict) and message.role.value == "system"
                else message.payload.text
            )
        ) for message in messages[-k:]
    ]

    chat_context_string = "\n\n".join(
        map(
            lambda message: (
                f"Role: {message.role}\n"
                f"Type: {message.type}\n"
                f"Text: {message.text}"
            ),
            chat_context_list
        )
    )

    response = run_essay_grading_assistant(
        user_query=messages[-1].payload.text,
        chat_context=chat_context_string,
        user_info=user_info
    )

    logger.info(f"Response generated successfully for Essay Grading Assistant: {response}")

    return response