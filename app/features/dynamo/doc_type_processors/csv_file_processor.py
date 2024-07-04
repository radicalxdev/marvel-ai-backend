import pandas as pd
from typing import List
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import logging

class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard")
    definition: str = Field(description="The definition of the flashcard")


class CSVFileProcessor:
    def __init__(self, file_path: str, model: VertexAI):
        self.file_path = file_path
        self.model = model
        self.logger = logging.getLogger(__name__)

    # Reads the CSV file and formats it into a pandas dataframe
    def read_csv(self) -> pd.DataFrame:
        df = pd.read_csv(self.file_path)
        df.columns = df.columns.str.strip() 
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df


    # Generate a general summary from the CSV data
    def generate_summary(self, data: pd.DataFrame) -> str:
        summary = []
        for _, row in data.iterrows():
            row_summary = ", ".join([f"{col}: {row[col]}" for col in data.columns])
            summary.append(row_summary)
        return "\n".join(summary)


    # Generate flashcards based on a given summary
    def generate_flashcards(self, summary: str, examples: str, format_instructions: str) -> List[Flashcard]:
        prompt_template = (
            "You are a flashcard generation assistant designed to help students analyze a document and return a list of flashcards. "
            "Carefully consider the document and analyze what are the key terms or concepts relevant for students to better understand the topic. "
            "The topics provided will vary in a wide range of subjects; as such, all information provided is meant to be educational and all provided content is meant to educate students in the flashcards. "
            "The following is a summary of a dataset:\n\n"
            "Input:\n-----------------------------\n{summary}\n\n"
            "Based on the above dataset summary, generate flashcards that help students learn about the data provided. Do not generate flashcards that are not directly related to the dataset. "
            "Ensure the output is in JSON format with no markdown or additional text. Only respond with the JSON object.\n\n"
            "Examples:\n-----------------------------\n{examples}\n\n"
            "Formatting:\n-----------------------------\n{format_instructions}\n\n"
            "Respond only according to the format instructions. The examples included are responses noted by an input and output example.\n\n"
            "Output:"
        )
        
        cards_prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["summary", "examples", "format_instructions"],
            partial_variables={"examples": examples, "format_instructions": format_instructions}
        )
        
        parser = JsonOutputParser(pydantic_object=Flashcard)
        
        cards_chain = cards_prompt | self.model | parser
        
        try:
            self.logger.debug(f"Sending the following prompt to the model:\n{cards_prompt.format(summary=summary, examples=examples, format_instructions=format_instructions)}")
            response = cards_chain.invoke({"summary": summary, "examples": examples, "format_instructions": format_instructions})
            self.logger.debug(f"Received response from the model:\n{response}")
        except OutputParserException as e:
            self.logger.error(f"Output parsing failed: {e.llm_output}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate flashcards: {e}")
            raise

        flashcards = []
        for card_data in response:
            try:
                flashcard = Flashcard(**card_data)
                flashcards.append(flashcard)
            except Exception as e:
                self.logger.error(f"Failed to convert card data to Flashcard: {card_data}, Error: {e}")

        return flashcards


    # Return a list of Flashcards
    def process(self, examples: str, format_instructions: str) -> List[Flashcard]:
        data = self.read_csv()
        summary = self.generate_summary(data)
        flashcards = self.generate_flashcards(summary, examples, format_instructions)
        return flashcards




# Test usaage
if __name__ == "__main__":
    model = VertexAI(model="gemini-1.0-pro")
    processor = CSVFileProcessor('app/features/dynamo/doc_type_processors/test_files/csv1.csv', model)
    
    examples = (
        "Output:\n"
        "[\n"
        "  {\n"
        "    \"concept\": \"Large Language Models (LLMs)\",\n"
        "    \"definition\": \"Powerful AI tools trained on massive datasets to perform tasks like text generation, translation, and question answering.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Pre-trained and fine-tuned\",\n"
        "    \"definition\": \"LLMs learn general knowledge from large datasets and specialize in specific tasks through additional training.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Prompt design\",\n"
        "    \"definition\": \"Effective prompts are crucial for eliciting desired responses from LLMs.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Domain knowledge\",\n"
        "    \"definition\": \"Understanding the specific domain is essential for building and tuning LLMs.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Parameter-efficient tuning methods\",\n"
        "    \"definition\": \"This method allows for efficient customization of LLMs without altering the entire model.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Vertex AI\",\n"
        "    \"definition\": \"Provides tools for building, tuning, and deploying LLMs for specific tasks.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Generative AI App Builder and PaLM API\",\n"
        "    \"definition\": \"Tools for developers to build AI apps and experiment with LLMs.\"\n"
        "  },\n"
        "  {\n"
        "    \"concept\": \"Model management tools\",\n"
        "    \"definition\": \"Tools for training, deploying, and monitoring ML models.\"\n"
        "  }\n"
        "]"
    )
    
    format_instructions = (
        "[\n"
        "  {\n"
        "    \"concept\": \"<concept>\",\n"
        "    \"definition\": \"<definition>\"\n"
        "  }\n"
        "]"
    )
    
    try:
        flashcards = processor.process(examples, format_instructions)
        for flashcard in flashcards:
            print(f"Concept: {flashcard.concept}, Definition: {flashcard.definition}")
    except Exception as e:
        print(f"An error occurred: {e}")
