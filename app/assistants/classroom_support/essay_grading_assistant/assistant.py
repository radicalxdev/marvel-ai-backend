import chromadb.api
import chromadb.api.client
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from app.utils.document_loaders import get_docs
from app.services.assistant_registry import UserInfo
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from concurrent.futures import ThreadPoolExecutor

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_chroma import Chroma
import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai

from app.tools.rubric_generator.core import executor as rubric_generator_executor
from app.tools.rubric_generator.tools import RubricOutput
from app.tools.rubric_generator.tools import RubricCriteria as RubricCriterion  # Naming vexation. Please dont mind it too much
from app.tools.writing_feedback_generator.core import executor as feedback_generator_executor
from app.tools.writing_feedback_generator.tools import WritingFeedback

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

logger = setup_logger()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()

system_message = read_text_file('prompt/essay_grading_assistant_context.txt')
model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp',
                              system_instruction=system_message,
                              )
langchain_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

#==============================================MODEL DEFINITIONS==============================================
# Essay Grading Input
class WritingToReviewItem(BaseModel):
    writing_to_review: str
    writing_to_review_file_url: str
    writing_to_review_file_type: str

class EssayGradingGeneratorArgs(BaseModel):
    grade_level: str
    point_scale: int
    assignment_description: str
    rubric_objectives: str
    rubric_objectives_file_url: str
    rubric_objectives_file_type: str
    writing_to_review_list: List[WritingToReviewItem]
    lang: str

# Essay Grading Pipeline Output
class CriterionGrading(BaseModel):
    criterion: RubricCriterion = Field(..., description="The rubric criterion being evaluated, including its descriptions and each description's corresponding points.")
    grade: int  = Field(..., description="The grade assigned for this criterion. It should be how many points out of the point scale")
    reasoning: str = Field(..., description="Explanation of why this grade was assigned to this criterion.")

class GradingOutput(BaseModel):
    criteria_grading: List[CriterionGrading] = Field(..., description="The list of assigned grade and explaination for said grade for each rubric criterion.")
    total_grade: str

# Essay Grading Final Output
class EssayGradingOutput(BaseModel):
    writing_to_review_item: WritingToReviewItem
    criteria_grading: List[CriterionGrading]
    feedback: WritingFeedback
    total_grade: str

# List of Essay Grading Final Output for batch output of essays
class EssayGradingResult(BaseModel):
    rubric: RubricOutput
    essay_grading_output_list: List[EssayGradingOutput]

#==============================================GENERATOR PIPELINES==============================================
#-------------------------------------------GENERATE GRADING-------------------------------------------
class EssayGradingGeneratorPipelineArgs(BaseModel):
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"]
    point_scale: int
    assignment_description: str
    rubric_criteria: List[RubricCriterion]
    writing_to_review: str
    writing_to_review_file_url: str
    writing_to_review_file_type: str
    lang: str

class EssayGradingGeneratorPipeline:
    def __init__(self, args=None, verbose=False):
        self.verbose = verbose
        self.args = args
        self.model = langchain_model
        self.vectorstore_class = Chroma
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
        # Remove criterion field from chain's result format. This is to prevent the chain from altering the rubric criterion's actual content.
        class GradingOutput(BaseModel):
            grade: int  = Field(..., description="The grade assigned for the specified criterion. It should be how many points out of the point scale")
            reasoning: str = Field(..., description="Explanation of why this grade was assigned to this criterion.")

        base_prompt = PromptTemplate(
            template_format='f-string',
            template=(
                "System Message: {system_message}"
                "Analyze the provided writing and evaluate it based on the rubric criterion '{criterion}'."
                "Assign grading and reasoning behind the grading using the descriptions for each point section: {criterion_description}. "
                "Use the provided Writing to Review: {writing_to_review}. If it is empty, use the context {context}."
                "Assignment Description: {assignment_description}. Grade Level: {grade_level}. Point Scale: {point_scale}"
                "YOU MUST RESPONSE IN THIS LANGUAGE: {lang}"
                "Respond in this JSON format: \n{format_instructions}"
            ),
            input_variables=["assignment_description", "grade_level", "point_scale", "criterion", "criterion_description", "writing_to_review", "lang", "context"],
            partial_variables={"system_message": system_message,
                               "format_instructions": JsonOutputParser(pydantic_object=GradingOutput).get_format_instructions()}
        )

        chains = {}

        for criterion in self.args.rubric_criteria:
            criterion_description_str = "\n".join([
                f"{desc.points} points: " + " ".join(desc.description)
                for desc in criterion.criteria_description
            ])

            if (self.vectorstore):
                context = self.generate_context(f"Provide context for grading this assignment using this criterion: {criterion}")
                chromadb.api.client.SharedSystemClient.clear_system_cache()
            else:
                context = ""

            prompt = PromptTemplate(
                template=base_prompt.template,
                input_variables=base_prompt.input_variables,
                partial_variables={
                    **base_prompt.partial_variables,
                    "criterion": criterion.criteria,
                    "criterion_description": criterion_description_str,
                    "context": context
                }
            )

            chain = prompt | self.model | JsonOutputParser(pydantic_object=GradingOutput)

            chains[criterion.criteria] = chain
        
        return RunnableParallel(branches=chains)

    def generate_context(self, query: str) -> str:
        return self.retriever.invoke(query)

    def essay_grading_generator(self, documents: Optional[List[Document]] = None):
        if documents:
            self.compile_vectorstore(documents)
        
        pipeline = self.compile_pipeline()
        inputs = {
            "grade_level": self.args.grade_level,
            "point_scale": self.args.point_scale,
            "assignment_description": self.args.assignment_description,
            "rubric_criteria": self.args.rubric_criteria,
            "writing_to_review":  self.args.writing_to_review,
            "lang": self.args.lang
        }

        try:
            results = pipeline.invoke(inputs)
            grading_output = GradingOutput(
                criteria_grading=[
                    CriterionGrading(
                        criterion=criterion,
                        grade=results["branches"][criterion.criteria]["grade"],
                        reasoning=results["branches"][criterion.criteria]["reasoning"]
                    )
                    for criterion in self.args.rubric_criteria
                ],
                # Total grade: total of assigned grade / total of maximum grade for each criteria (i.e point scale * # of criteria)
                total_grade = f"{sum(results["branches"][criterion.criteria]["grade"] for criterion in self.args.rubric_criteria)} / {self.args.point_scale * len(self.args.rubric_criteria)}"
            )

            if self.verbose:
                logger.info("(Grade Essay Pipeline) Grading successfully generated.")
            return grading_output

        except Exception as e:
            logger.error(f"(Grade Essay Pipeline) Error in generating grading: {e}")
            raise ValueError("(Grade Essay Pipeline) Failed to generate grade.")

def generate_grading(grade_level: str,
                    point_scale: int,
                    assignment_description: str,
                    writing_to_review: str,
                    writing_to_review_file_url: str,
                    writing_to_review_file_type: str,
                    lang: str,
                    rubric_criteria: List[RubricCriterion]):
    try:
        if (writing_to_review_file_type):
            logger.info(f"Generating Writing To Review docs. from {writing_to_review_file_url}")
        
        docs = None

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None
        
        docs = fetch_docs(writing_to_review_file_url, writing_to_review_file_type)

        essay_grading_generator_args = EssayGradingGeneratorPipelineArgs(
            grade_level=grade_level,
            point_scale=point_scale,
            assignment_description=assignment_description,
            rubric_criteria=rubric_criteria,
            writing_to_review=writing_to_review,
            writing_to_review_file_url=writing_to_review_file_url,
            writing_to_review_file_type=writing_to_review_file_type,
            lang=lang
        )

        grading_output = EssayGradingGeneratorPipeline(args=essay_grading_generator_args).essay_grading_generator(docs)

        logger.info(f"(Essay Grading Assistant) (Generate Grading) Essay Grading generated successfully.")

    except LoaderError as e:
        error_message = e
        logger.error(f"(Essay Grading Assistant) (Generate Grading) Error in Essay Grade Genarator Pipeline: {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"(Essay Grading Assistant) (Generate Grading) Error during running Essay Grading Generator: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return grading_output

#-------------------------------------------GENERATE RUBRIC-------------------------------------------
def generate_rubric(grade_level: str,
                    point_scale: int,
                    objectives: str,
                    assignment_description: str,
                    objectives_file_url: str,
                    objectives_file_type: str,
                    #assignment_description_file_url: str,
                    #assignment_description_file_type: str,
                    lang: str):
    try:
        rubric_output = rubric_generator_executor(grade_level=grade_level,
                                                point_scale=point_scale,
                                                objectives=objectives,
                                                assignment_description=assignment_description,
                                                objectives_file_url=objectives_file_url,
                                                objectives_file_type=objectives_file_type,
                                                assignment_description_file_url="",
                                                assignment_description_file_type="",
                                                lang=lang)
    except LoaderError as e:
        error_message = e
        logger.error(f"(Essay Grading Assistant) (Generate Rubric) Error in Rubric Genarator Pipeline: {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"(Essay Grading Assistant) (Generate Rubric) Error during running Rubric Generator: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return rubric_output

#-------------------------------------------GENERATE FEEDBACK-------------------------------------------
def generate_feedback(grade_level: str,
                    assignment_description: str,
                    #criteria: str,
                    writing_to_review: str,
                    #criteria_file_url: str,
                    #criteria_file_type: str,
                    writing_to_review_file_url: str,
                    writing_to_review_file_type: str,
                    lang: str,
                    grading_output: GradingOutput):
    #Convert Grading Output to String for feedback_generator_executor's criteria parameter
    grading_output_dict = grading_output.model_dump()

    grading_output_string = f"Total Grade: {grading_output_dict['total_grade']}\n\n"
    for criterion_grading in grading_output_dict['criteria_grading']:
        criterion = criterion_grading['criterion']
        grading_output_string += f"Criterion: {criterion['criteria']}\n"
        for description in criterion['criteria_description']:
            grading_output_string += f"Points: {description['points']}, Descriptions: {', '.join(description['description'])}\n"
        grading_output_string += f"Grade: {criterion_grading['grade']}\n"
        grading_output_string += f"Reasoning: {criterion_grading['reasoning']}\n\n"
        
    grading_output_string+= f"Use these criteria and their corresponding assigned grades and reasoning behind said grades as basis for your feedbacks.\n"
    
    try:
        generated_feedback = feedback_generator_executor(grade_level=grade_level,
                                                        assignment_description=assignment_description,
                                                        criteria=grading_output_string,
                                                        writing_to_review=writing_to_review,
                                                        criteria_file_url="",
                                                        criteria_file_type="",
                                                        writing_to_review_file_url=writing_to_review_file_url,
                                                        writing_to_review_file_type=writing_to_review_file_type,
                                                        lang=lang)

    except LoaderError as e:
        error_message = e
        logger.error(f"(Essay Grading Assistant) (Generate Feedback) Error in Writing Feedback Generator Pipeline: {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"(Essay Grading Assistant) (Generate Feedback) Error during running Writing Feedback Generator: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return generated_feedback

#==============================================RESPONSE FOR ESSAY GRADING==============================================
def generate_grading_and_feedback(grade_level: str,
                                    point_scale: str,
                                    assignment_description: str,
                                    writing_to_review_item: WritingToReviewItem,
                                    lang: str,
                                    rubric_criteria: List[RubricCriterion]):

    grading = generate_grading(grade_level=grade_level,
                                point_scale=point_scale,
                                assignment_description=assignment_description,
                                writing_to_review=writing_to_review_item["writing_to_review"],
                                writing_to_review_file_url=writing_to_review_item["writing_to_review_file_url"],
                                writing_to_review_file_type=writing_to_review_item["writing_to_review_file_type"],
                                lang=lang,
                                rubric_criteria=rubric_criteria)
    
    feedback = generate_feedback(grade_level=grade_level,
                                assignment_description=assignment_description,
                                writing_to_review=writing_to_review_item["writing_to_review"],
                                writing_to_review_file_url=writing_to_review_item["writing_to_review_file_url"],
                                writing_to_review_file_type=writing_to_review_item["writing_to_review_file_type"],
                                lang=lang,
                                grading_output=grading)
    
    return EssayGradingOutput(
                writing_to_review_item=writing_to_review_item,
                criteria_grading=grading.criteria_grading,
                feedback=feedback,
                total_grade=grading.total_grade,
            )


def run_essay_grading_assistant_essay_grading(grade_level: str,
                                            point_scale: str,
                                            assignment_description: str,
                                            rubric_objectives: str,
                                            rubric_objectives_file_url: str,
                                            rubric_objectives_file_type: str,
                                            writing_to_review_list: List[WritingToReviewItem],
                                            #writing_to_review_file_url: str,
                                            #writing_to_review_file_type: str,
                                            lang: str,):
    rubric_output = generate_rubric(grade_level=grade_level,
                                    point_scale=point_scale,
                                    objectives=rubric_objectives,
                                    assignment_description=assignment_description,
                                    objectives_file_url=rubric_objectives_file_url,
                                    objectives_file_type=rubric_objectives_file_type,
                                    lang=lang)
    rubric_criteria = rubric_output["criterias"]

    essay_grading_list: List[EssayGradingOutput] = []

    batch_size = 10
    def chunk_list(data_list, chunk_size):
        for i in range(0, len(data_list), chunk_size):
            yield data_list[i:i + chunk_size]

    for batch in chunk_list(writing_to_review_list, batch_size):
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [
                executor.submit(
                    generate_grading_and_feedback,
                    grade_level,
                    point_scale,
                    assignment_description,
                    writing_to_review_item,
                    lang,
                    rubric_criteria
                )
                for writing_to_review_item in batch
            ]

            for future in futures:
                try:
                    result = future.result()
                    essay_grading_list.append(result)
                except Exception as e:
                    error_message = f"(Essay Grading Assistant) (Batch Generate Grading and Feedback) Error batch processing of writing_to_review_item: {e}"
                    logger.error(error_message)
                    raise ValueError(error_message)

    return EssayGradingResult(
                rubric=rubric_output,
                essay_grading_output_list=essay_grading_list).model_dump()

#==============================================RESPONSE FOR BASIC QUERY==============================================
def run_essay_grading_assistant_basic_query(user_query: str, chat_context: str, user_info: UserInfo):
    chat = model.start_chat()

    user_name = user_info.user_name
    user_age = user_info.user_age
    user_preference = user_info.user_preference

    response = chat.send_message(f"""
                                User query: {user_query}\n
                                Personalize the response for {user_name} (Age: {user_age}) with preference: {user_preference}.\n
                                You can use the chat context if further information is needed: {chat_context}\n
                                """)

    return response.text

#==============================================ENTRY POINT FOR ESSAY GRADING ASSISTANT==============================================
def run_essay_grading_assistant(
                    user_query: str,
                    chat_context: str,
                    user_info: UserInfo):
    # If provided args for essay grading generation
    if isinstance(user_query, EssayGradingGeneratorArgs):
        return run_essay_grading_assistant_essay_grading(**user_query.model_dump())
    # else, only generate result for user query
    return run_essay_grading_assistant_basic_query(user_query=user_query, chat_context=chat_context, user_info=user_info)