from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_community.document_loaders import UnstructuredAPIFileLoader
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()


load_dotenv()


class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard")
    definition: str = Field(description="The definition of the flashcard")

class docProcessor:

    # Initializes instances for the class level document, model, and logger
    def __init__(self, userDocument: str, model: VertexAI):
        self.document = userDocument
        self.model = model 
        self.api_key = os.getenv("UNSTRUCTURED_API_KEY")
        self.logger = logging.getLogger(__name__)
    
    # Uses Unstructured API File Loader to process the user provided word document
    def processDocument(self):
        with open(self.document, "rb") as file:
            self.logger.info(f"Loading document from {self.document}")
            loader = UnstructuredAPIFileLoader(self.document, api_key=self.api_key)
            docs = loader.load()
        return docs

    # Summarizes Document by joining everything into 1
    def summarizeDoc(self):
        allDocuments = self.processDocument()
        if not allDocuments:
            self.logger.error("No documents were loaded.")
            raise ValueError("Document processing failed, no content available.")
    
        self.logger.info(f"Loaded {len(allDocuments)} documents.")
    
        docSummary = []
        for doc in allDocuments:
            content = doc.page_content
            if content:
                docSummary.append(content)
            else:
                self.logger.warning(f"Empty content found in one of the documents.")
    
        if not docSummary:
            self.logger.error("Document summary is empty.")
            raise ValueError("Document summary generation failed.")
    
        return ("\n".join(docSummary))
    
    # Creates a singular flashcard prompt
    def createFlashcards(self, summary, examples, format_instructions):
        if not summary:
            self.logger.error("Summary is empty. Cannot generate flashcards.")
            raise ValueError("Summary is empty.")
        
        prompt_template = (
            "You are a flashcard generation assistant designed to help students analyze a document and return a list of flashcards. "
            "Carefully consider the document and analyze what are the key terms or concepts relevant for students to better understand the topic. "
            "The topics provided will vary in a wide range of subjects; as such, all information provided is meant to be educational and all provided content is meant to educate students in the flashcards. "
            "The following is a summary of a document:\n\n"
            "Input:\n-----------------------------\n{summary}\n\n"
            "Based on the above dataset summary, generate flashcards that help students learn about the data provided. Do not generate flashcards that are not directly related to the dataset. "
            "Ensure the output is in JSON format with no markdown or additional text. Only respond with the JSON object.\n\n"
            "Examples:\n-----------------------------\n{examples}\n\n"
            "Formatting:\n-----------------------------\n{format_instructions}\n\n"
            "Respond only according to the format instructions. The examples included are responses noted by an input and output example.\n\n"
            "Output:"
        )

        flashcardsPrompt = PromptTemplate(
            template=prompt_template,
            input_variables=["summary"],
            partial_variables={"examples": examples, "format_instructions": format_instructions}
        )

        parser = JsonOutputParser(pydantic_object=Flashcard)
        
        flashcardsChain = flashcardsPrompt | self.model | parser
        
        try:
            self.logger.debug(f"Sending the following prompt to the model:\n{flashcardsPrompt.format(summary=summary, examples=examples, format_instructions=format_instructions)}")
            modelResponse = flashcardsChain.invoke({"summary": summary, "examples": examples, "format_instructions": format_instructions})
            if not modelResponse:
                self.logger.error("Model response is empty.")
                raise ValueError("Model did not return any flashcards.")
        except OutputParserException as e:
            self.logger.error(f"Output parsing failed: {e.llm_output}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate flashcards: {e}")
            raise

        flashcards = []
        for card_data in modelResponse:
            try:
                flashcard = Flashcard(**card_data)
                flashcards.append(flashcard)
            except Exception as e:
                self.logger.error(f"Failed to convert card data to Flashcard: {card_data}, Error: {e}")

        return flashcards

    # Return a list of Flashcards
    def publishFlashcards(self, examples: str, format_instructions: str):
        documentSummary = self.summarizeDoc()
        flashcards = self.createFlashcards(documentSummary, examples, format_instructions)
        return flashcards
    
# if __name__ == "__main__":
#     model = VertexAI(model = "gemini-1.0-pro")

    

# FastAPI testing
@app.get("/")
def read_root():
    return {"message": "Doc Flashcard generator testing"}

@app.post("/process_doc_file")
async def createFlashcards(documentFile: UploadFile = File(...)):
    try:
        with open("uploaded_file.doc", "wb") as f:
            f.write(documentFile.file.read())

        model = VertexAI(model="gemini-1.0-pro")
        processor = docProcessor('uploaded_file.doc', model)

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

        flashcards = processor.publishFlashcards(examples, format_instructions)
        return JSONResponse(content=[flashcard.model_dump() for flashcard in flashcards])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
