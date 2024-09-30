from app.services.logger import setup_logger
from app.features.connect_with_them.tools import validate_input, CWTRecommendationGenerator

#Setting up logging
logger = setup_logger()

def executor(grade: str, subject: str, students_description: str):
    try:
        # Validate the input
        if not validate_input(subject, students_description):
            raise ValueError("Input validation failed. Please provide a valid subject and student description.")

        # Log the input for debugging purposes
        logger.debug(f"Grade: {grade}, Subject: {subject}, Students: {students_description}")

        # Call Vertex AI to generate recommendations based on the validated input
        personalized_recommendations = CWTRecommendationGenerator(grade, subject, students_description)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return personalized_recommendations
