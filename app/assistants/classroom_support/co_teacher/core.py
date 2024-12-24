from app.assistants.classroom_support.co_teacher.assistant import run_co_teacher_assistant
from app.services.logger import setup_logger
from app.services.schemas import ChatMessage, Message

logger = setup_logger()

def executor(
        user_name: str,
        user_age: int,
        user_preference: str,
        messages: list[Message]=None, 
        k=3
    ):
    
    logger.info(f"Generating response from CoTeacher")

    chat_context_list = [
        ChatMessage(
            role=message["role"], 
            type=message["type"], 
            text=message["payload"]["text"]
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
    
    result, response = run_co_teacher_assistant(
        user_query=chat_context_list[-1].text,
        chat_context=chat_context_string,
        user_name=user_name,
        user_age=user_age,
        user_preference=user_preference
    )

    logger.info(f"Response generated successfully for CoTeacher: {response}")
    logger.info(f"Final result generated successfully for CoTeacher: {result}")

    return {
        "response": response,
        "result": result
    }