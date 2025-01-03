from app.assistants.classroom_support.essay_grading_assistant.assistant import run_essay_grading_assistant
from app.services.assistant_registry import Message, UserInfo
from app.services.logger import setup_logger
from app.services.schemas import (
    ChatMessage
)

logger = setup_logger()

def executor(
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
        user_info: UserInfo,
        messages: list[Message]=None, 
        k=3
    ):
    
    logger.info(f"Generating response from Essay Grading Assistant")

    chat_context_list = [
        ChatMessage(
            role=message.role, 
            type=message.type, 
            text=message.payload.text
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
    
    grading_inputs = {
        "grade_level": grade_level,
        "point_scale": point_scale,
        "assignment_description": assignment_description,
        "rubric_objectives": rubric_objectives,
        "rubric_objectives_file_url": rubric_objectives_file_url,
        "rubric_objectives_file_type": rubric_objectives_file_type,
        "writing_to_review": writing_to_review,
        "writing_to_review_file_url": writing_to_review_file_url,
        "writing_to_review_file_type": writing_to_review_file_type,
        "lang": lang,
    }

    response = run_essay_grading_assistant(
        grading_inputs,
        user_query=chat_context_list[-1].text,
        chat_context=chat_context_string,
        user_info=user_info
    )

    logger.info(f"Response generated successfully for Essay Grading Assistant: {response}")

    return response