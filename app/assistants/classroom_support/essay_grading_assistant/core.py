from app.assistants.classroom_support.essay_grading_assistant.assistant import run_essay_grading_assistant, EssayGradingGeneratorArgs
from app.services.assistant_registry import Message, UserInfo
from app.services.logger import setup_logger
from app.services.schemas import (
    ChatMessage
)

logger = setup_logger()

def executor(
        user_info: UserInfo,
        messages: list[Message]=None,
        k=3
    ):

    logger.info(f"Generating response from Essay Grading Assistant")

    user_query = messages[-1].payload.text

    if isinstance(user_query, dict) and messages[-1].role.value == "human":
        user_query = EssayGradingGeneratorArgs.model_validate(user_query)
    else:
        user_query = str(user_query)

    chat_context_list = [
        ChatMessage(
            role=message.role,
            type=message.type,
            text=(
                "Generate essay grading with these arguments: " + str(message.payload.text) # Purely symbolic prompt to represent the arguments dictionary for Essay Grading Pipeline. Its only purpose is to maintain comprehensibility of the context string.
                # if payload contain the correct arguments for Essay Grading Pipeline and role is human, append symbolic prompt
                if isinstance(message.payload.text, dict) and message.role.value == "human"
                # Else, payload is the request/response of either human or ai and should be converted to string
                else str(message.payload.text)
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
        user_query=user_query,
        chat_context=chat_context_string,
        user_info=user_info
    )

    logger.info(f"Response generated successfully for Essay Grading Assistant: {response}")

    return response