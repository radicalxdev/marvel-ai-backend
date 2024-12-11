from app.assistants.classroom_support.co_teacher.tools import compile_co_teacher
from app.services.logger import setup_logger
from app.services.schemas import ChatMessage, Message
logger = setup_logger()

def executor(
        action: str,
        messages: list[Message]=None, 
        k=10
    ):
    
    logger.info(f"Generating response from CoTeacher - Action: [{action}]")

    print(messages)

    chat_context = [
        ChatMessage(
            role=message["role"], 
            type=message["type"], 
            text=message["payload"]["text"]
        ) for message in messages[-k:]
    ]

    co_teacher = compile_co_teacher()
    user_query = messages[-1]["payload"]["text"]

    inputs = {
        "user_query": user_query,
        "action": action,
        "chat_history": chat_context
    }

    result = co_teacher.invoke(inputs)

    logger.info(f"Response generated successfully for CoTeacher - Action: [{action}]")

    return result["result"]