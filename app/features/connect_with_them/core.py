from services.logger import setup_logger
from tools import Agent_executor
from prompt.Prompts import Prompt_query

logger = setup_logger()

def executor(grade:str ,subject:str ,description:str ) -> str:
    try:
        if not(grade and subject) :
            raise ValueError("Grade and subject are required")

        user_input = Prompt_query(grade,subject,description)
        result = Agent_executor.invoke({'input':user_input})
        return result['output']

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

# later we setup the endpoint
