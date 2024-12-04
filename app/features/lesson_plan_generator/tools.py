from pydantic import BaseModel
from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger

logger = setup_logger(__name__)

class LessonPlanGeneratorPipeline:
    def __init__(self, args=None, verbose=False):
        self.verbose = verbose
        self.args = args
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore_class = Chroma
        self.parsers = {
            "title": JsonOutputParser(pydantic_object=Title),
            "objective": JsonOutputParser(pydantic_object=Objective),
            "assessment": JsonOutputParser(pydantic_object=Assessment),
            "key_points": JsonOutputParser(pydantic_object=KeyPoints),
            "opening": JsonOutputParser(pydantic_object=Section),
            "introduction_to_new_material": JsonOutputParser(pydantic_object=Section),
            "guided_practice": JsonOutputParser(pydantic_object=Section),
            "independent_practice": JsonOutputParser(pydantic_object=IndependentPractice),
            "closing": JsonOutputParser(pydantic_object=Section),
            "extension_activity": JsonOutputParser(pydantic_object=ExtensionActivity),
            "homework": JsonOutputParser(pydantic_object=Homework),
            "standards_addressed": JsonOutputParser(pydantic_object=StandardsAddressed),
        }
        self.vectorstore = None
        self.retriever = None

    def compile_vectorstore(self, documents: List[Document]):
        if self.verbose:
            logger.info("Creating vectorstore from documents...")
        self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
        self.retriever = self.vectorstore.as_retriever()
        if self.verbose:
            logger.info("Vectorstore and retriever created successfully.")

    def compile_pipeline(self):
        prompts = {
            "title": PromptTemplate(
                template="Generate a detailed title for {topic} (Grade Level: {grade_level}). You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic", "grade_level"],
                partial_variables={"format_instructions": self.parsers["title"].get_format_instructions()},
            ),
            "objective": PromptTemplate(
                template="Provide an objective for {topic} (Grade Level: {grade_level}). You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic", "grade_level"],
                partial_variables={"format_instructions": self.parsers["objective"].get_format_instructions()},
            ),
            "assessment": PromptTemplate(
                template="Suggest an assessment for {topic}. Context: {context}, Objectives: {objectives}, Customization: {additional_customization}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic", "context", "objectives", "additional_customization"],
                partial_variables={"format_instructions": self.parsers["assessment"].get_format_instructions()},
            ),
            "key_points": PromptTemplate(
                template="List key points for {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["key_points"].get_format_instructions()},
            ),
            "opening": PromptTemplate(
                template="Describe an opening activity for {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["opening"].get_format_instructions()},
            ),
            "introduction_to_new_material": PromptTemplate(
                template="Outline the introduction to new material for {topic}. Context: {context}, Objectives: {objectives}, Comments: {additional_customization}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic", "context", "objectives", "additional_customization"],
                partial_variables={"format_instructions": self.parsers["introduction_to_new_material"].get_format_instructions()},
            ),
            "guided_practice": PromptTemplate(
                template="Describe guided practice for {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["guided_practice"].get_format_instructions()},
            ),
            "independent_practice": PromptTemplate(
                template="Provide an independent practice task for {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["independent_practice"].get_format_instructions()},
            ),
            "closing": PromptTemplate(
                template="Describe a conclusion for {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["closing"].get_format_instructions()},
            ),
            "extension_activity": PromptTemplate(
                template="Suggest an extension activity for {topic}. Context: {context}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic", "context"],
                partial_variables={"format_instructions": self.parsers["extension_activity"].get_format_instructions()},
            ),
            "homework": PromptTemplate(
                template="Provide homework for {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["homework"].get_format_instructions()},
            ),
            "standards_addressed": PromptTemplate(
                template="List standards addressed by teaching {topic}. You must respond as a JSON in this format: \n{format_instructions}",
                input_variables=["topic"],
                partial_variables={"format_instructions": self.parsers["standards_addressed"].get_format_instructions()},
            ),
        }
        chains = {key: prompt | self.model | self.parsers[key] for key, prompt in prompts.items()}
        return RunnableParallel(branches=chains)

    def generate_context(self, query: str) -> str:
        return self.retriever.invoke(query)

    def generate_lesson_plan(self, documents: Optional[List[Document]]):

        if documents: 
            self.compile_vectorstore(documents)

        pipeline = self.compile_pipeline()

        if documents:
            context_queries = {
                "general": "Provide general context for the topic.",
                "specific": "Provide specific details for creating an educational lesson plan.",
            }
            context = {
                query_name: self.generate_context(query)
                for query_name, query in context_queries.items()
            }

        inputs = {
            "topic": self.args.topic,
            "grade_level": self.args.grade_level,
            "context": context["general"] if documents else '',
            "objectives": self.args.objectives,
            "additional_customization": self.args.additional_customization,
        }
        results = pipeline.invoke(inputs)
        lesson_plan = {
            "title": results["branches"]["title"]["title"],
            "objective": results["branches"]["objective"]["objective"],
            "assessment": results["branches"]["assessment"]["assessment"],
            "key_points": results["branches"]["key_points"]["key_points"],
            "opening": results["branches"]["opening"],
            "introduction_to_new_material": results["branches"]["introduction_to_new_material"],
            "guided_practice": results["branches"]["guided_practice"],
            "independent_practice": results["branches"]["independent_practice"],
            "closing": results["branches"]["closing"],
            "extension_activity": results["branches"]["extension_activity"],
            "homework": results["branches"]["homework"],
            "standards_addressed": results["branches"]["standards_addressed"],
        }
        if self.verbose:
            logger.info("Lesson Plan successfully generated.")
        return lesson_plan

class Title(BaseModel):
    title: str

class Objective(BaseModel):
    objective: str

class Assessment(BaseModel):
    assessment: str

class KeyPoint(BaseModel):
    title: str
    description: str

class Section(BaseModel):
    title: str
    content: List[str]

class IndependentPractice(BaseModel):
    description: str
    tasks: List[str]

class ExtensionActivity(BaseModel):
    description: str
    additional_instructions: Optional[str]

class Homework(BaseModel):
    description: str
    submission_instructions: Optional[str]

class Standard(BaseModel):
    name: str
    description: str

class KeyPoints(BaseModel):
    key_points: List[KeyPoint]

class StandardsAddressed(BaseModel):
    standards_addressed: List[Standard]

class LessonPlan(BaseModel):
    title: Title
    objective: Objective
    assessment: Assessment
    key_points: KeyPoints
    opening: Section
    introduction_to_new_material: Section
    guided_practice: Section
    independent_practice: IndependentPractice
    closing: Section
    extension_activity: ExtensionActivity
    homework: Homework
    standards_addressed: StandardsAddressed