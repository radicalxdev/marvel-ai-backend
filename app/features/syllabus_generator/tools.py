from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict,Optional
from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from fastapi import HTTPException

logger = setup_logger(__name__)


class SyllabusRequestArgs(BaseModel):
    subject_topic: str
    grade_level: str
    subject: str
    course_description: str
    course_objectives: str
    required_materials: str
    grading_policy: str
    course_outline: str
    class_policies: str
    instructor_name: str
    instructor_title: str
    file_type: Optional[str] = None
    file_url: str
    important_dates: Optional[str] = None
    learning_outcomes: Optional[str] = None
    class_schedule: Optional[str] = None
    instructor_contact: Optional[str] = None
    additional_customizations: Optional[str] = None

    def to_dict(self) -> dict:
        return self.dict(exclude_unset=True)

class SyllabusGeneratorPipeline:
    def __init__(self, prompt=None, parser=None, model=None, verbose=False):
        default_config = {
            "prompt": (
                "Generate a syllabus based on the following details:\n"
                "Subject Topic: {subject_topic}\n"
                "Grade Level: {grade_level}\n"
                "Subject: {subject}\n"
                "Course Description: {course_description}\n"
                "Course Objectives: {course_objectives}\n"
                "Required Materials: {required_materials}\n"
                "Grading Policy: {grading_policy}\n"
                "Course Outline: {course_outline}\n"
                "Class Policies: {class_policies}\n"
                "Instructor Name: {instructor_name}\n"
                "Instructor Title: {instructor_title}\n"
                "File Type: {file_type}\n"
                "File URL: {file_url}\n"
                "Output in JSON format as per the SyllabusSchema."
            ),
            "parser": JsonOutputParser(pydantic_object=SyllabusSchema),
            "model": GoogleGenerativeAI(model="gemini-1.5-pro")
        }
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.verbose = verbose

    def compile(self):
        try:
            prompt = PromptTemplate(
                template=self.prompt,
                input_variables=[
                    "subject_topic",
                    "grade_level",
                    "subject",
                    "course_description",
                    "course_objectives",
                    "required_materials",
                    "grading_policy",
                    "course_outline",
                    "class_policies",
                    "instructor_name",
                    "instructor_title",
                    "file_type",
                    "file_url"
                ],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )

            chain = prompt | self.model | self.parser

            if self.verbose: logger.info("Chain compilation complete")

        except Exception as e:
            logger.error(f"Failed to compile LLM chain: {e}")
            raise HTTPException(status_code=500, detail="Failed to compile LLM chain")

        return chain

class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")

class InstructorInformation(BaseModel):
    name: str = Field(description="The instructor name")
    title: str = Field(description="The instructor title")
    description_title: str = Field(description="The description of the instructor title")

class CourseDescriptionObjectives(BaseModel):
    objectives: List[str] = Field(description="The course objectives")
    intended_learning_outcomes: List[str] = Field(description="The intended learning outcomes of the course")

class CourseContentItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course content")
    unit_time_value: int = Field(description="The unit of time value for the course content")
    topic: str = Field(description="The topic per unit of time for the course content")

class PoliciesProcedures(BaseModel):
    attendance_policy: str = Field(description="The attendance policy of the class")
    late_submission_policy: str = Field(description="The late submission policy of the class")
    academic_honesty: str = Field(description="The academic honesty policy of the class")

class AssessmentMethod(BaseModel):
    type_assessment: str = Field(description="The type of assessment")
    weight: int = Field(description="The weight of the assessment in the final grade")

class AssessmentGradingCriteria(BaseModel):
    assessment_methods: List[AssessmentMethod] = Field(description="The assessment methods")
    grading_scale: Dict[str, str] = Field(description="The grading scale")

class LearningResource(BaseModel):
    title: str = Field(description="The title of the learning resource")
    author: str = Field(description="The author of the learning resource")
    year: int = Field(description="The year of creation of the learning resource")

class CourseScheduleItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course schedule item")
    unit_time_value: int = Field(description="The unit of time value for the course schedule item")
    date: str = Field(description="The date for the course schedule item")
    topic: str = Field(description="The topic for the course schedule item")
    activity_desc: str = Field(description="The description of the activity for the course schedule item")

class SyllabusSchema(BaseModel):
    course_information: CourseInformation = Field(description="The course information")
    instructor_information: InstructorInformation = Field(description="The instructor information")
    course_description_objectives: CourseDescriptionObjectives = Field(description="The objectives of the course")
    course_content: List[CourseContentItem] = Field(description="The content of the course")
    policies_procedures: PoliciesProcedures = Field(description="The policies and procedures of the course")
    assessment_grading_criteria: AssessmentGradingCriteria = Field(description="The assessment and grading criteria of the course")
    learning_resources: List[LearningResource] = Field(description="The learning resources of the course")
    course_schedule: List[CourseScheduleItem] = Field(description="The course schedule")

def generate_syllabus(request_args: SyllabusRequestArgs, verbose=True) -> Dict:
    try:
        pipeline = SyllabusGeneratorPipeline(verbose=verbose)
        chain = pipeline.compile()
        output = chain.invoke(request_args.to_dict())
    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM")
    
    return output
