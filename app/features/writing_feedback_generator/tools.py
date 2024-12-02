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

class FeedbackSection(BaseModel):
    title: str
    points: List[str]

class WritingFeedback(BaseModel):
    title: str
    areas_of_strength: FeedbackSection
    areas_for_growth: FeedbackSection
    general_feedback: FeedbackSection

class WritingFeedbackGeneratorPipeline:
    def __init__(self, args=None, verbose=False):
        self.verbose = verbose
        self.args = args
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.vectorstore_class = Chroma
        self.parsers = {
            "areas_of_strength": JsonOutputParser(pydantic_object=FeedbackSection),
            "areas_for_growth": JsonOutputParser(pydantic_object=FeedbackSection),
            "general_feedback": JsonOutputParser(pydantic_object=FeedbackSection),
        }
        self.vectorstore = None
        self.retriever = None

    def compile_vectorstore(self, documents: List[Document]):
        if self.verbose:
            logger.info("Creating vectorstore from documents...")
        self.vectorstore = self.vectorstore_class.from_documents(documents, GoogleGenerativeAIEmbeddings(model="models/embedding-001"))
        self.retriever = self.vectorstore.as_retriever()
        if self.verbose:
            logger.info("Vectorstore and retriever created successfully.")

    def compile_pipeline(self):
        prompts = {
            "areas_of_strength": PromptTemplate(
                template=(
                    "Analyze the provided writing and generate feedback under 'Areas of Strength'. "
                    "Focus on what the writer has done well, including structure, clarity, and topic presentation. "
                    "Assignment Description: {assignment_description}. Grade Level: {grade_level}. "
                    "Use the provided Writing to Review: {writing_to_review} and Criteria: {criteria}. If any of them is empty, use the context {context}. "
                    "Respond in this JSON format: \n{format_instructions}"
                ),
                input_variables=["writing_to_review", "assignment_description", "grade_level", "criteria", "context"],
                partial_variables={"format_instructions": self.parsers["areas_of_strength"].get_format_instructions()},
            ),
            "areas_for_growth": PromptTemplate(
                template=(
                    "Analyze the provided writing and generate feedback under 'Areas for Growth'. "
                    "Identify areas where the writer could improve, focusing on content depth, clarity, and logical argumentation. "
                    "Assignment Description: {assignment_description}. Grade Level: {grade_level}. "
                    "Use the provided Writing to Review: {writing_to_review} and Criteria: {criteria}. If any of them is empty, use the context {context}. "
                    "Respond in this JSON format: \n{format_instructions}"
                ),
                input_variables=["writing_to_review", "assignment_description", "grade_level", "criteria", "context"],
                partial_variables={"format_instructions": self.parsers["areas_for_growth"].get_format_instructions()},
            ),
            "general_feedback": PromptTemplate(
                template=(
                    "Analyze the provided writing and generate general feedback on 'Writing Mechanics'. "
                    "This includes grammar, sentence structure, and overall readability. "
                    "Assignment Description: {assignment_description}. Grade Level: {grade_level}. "
                    "Use the provided Writing to Review: {writing_to_review} and Criteria: {criteria}. If any of them is empty, use the context {context}. "
                    "Respond in this JSON format: \n{format_instructions}"
                ),
                input_variables=["writing_to_review", "assignment_description", "grade_level", "criteria", "context"],
                partial_variables={"format_instructions": self.parsers["general_feedback"].get_format_instructions()},
            ),
        }

        chains = {
            key: prompt | self.model | self.parsers[key]
            for key, prompt in prompts.items()
        }
        return RunnableParallel(branches=chains)

    def generate_context(self, query: str) -> str:
        return self.retriever.invoke(query)

    def generate_feedback(self, documents: Optional[List[Document]] = None):
        if documents:
            self.compile_vectorstore(documents)
            context = self.generate_context("Provide context for evaluating this writing assignment.")
        else:
            context = ""

        pipeline = self.compile_pipeline()
        inputs = {
            "writing_to_review": self.args.writing_to_review,
            "assignment_description": self.args.assignment_description,
            "grade_level": self.args.grade_level,
            "criteria": self.args.criteria,
            "context": context,
        }

        try:
            results = pipeline.invoke(inputs)
            feedback = WritingFeedback(
                title=f"Feedback on Your Writing: {self.args.assignment_description}",
                areas_of_strength=results["branches"]["areas_of_strength"],
                areas_for_growth=results["branches"]["areas_for_growth"],
                general_feedback=results["branches"]["general_feedback"],
            )
            if self.verbose:
                logger.info("Feedback successfully generated.")
            return feedback
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            raise ValueError("Failed to generate feedback.")
