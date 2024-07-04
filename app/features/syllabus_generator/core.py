from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusRequestArgs
from app.features.syllabus_generator.tools import SyllabusGeneratorPipeline

logger = setup_logger()

def executor(grade_level: str, 
            course: str, 
            instructor_name: str, 
            instructor_title: str, 
            unit_time: str, 
            unit_time_value: int, 
            start_date: str, 
            assessment_methods: str, 
            grading_scale: str,
            verbose:bool = True):
    
    request_args = SyllabusRequestArgs(
                            grade_level,
                            course,
                            instructor_name,
                            instructor_title,
                            unit_time,
                            unit_time_value,
                            start_date,
                            assessment_methods,
                            grading_scale)
    
    pipeline = SyllabusGeneratorPipeline(verbose=verbose)
    chain = pipeline.compile()
    output = chain.invoke(request_args.to_dict())
    return output