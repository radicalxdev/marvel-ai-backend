import vertexai
import json
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI

#logger = setup_logger(__name__)

class CWTRecommendationGenerator:
    def __init__(self, grade: str, subject: str, students_description: str):
        """
        Initializes the RecommendationGenerator with the necessary inputs.
        
        :param grade: The grade level taught by the teacher.
        :param subject: The subject or topic taught by the teacher.
        :param students_description: A description of the students, including interests, location, cultural/social factors.
        """
        self.grade = grade
        self.subject = subject
        self.students_description = students_description
        self.llm = None
        self.prompt_template = """
        You are an AI model helping a teacher improve classroom engagement by generating detailed and creative project ideas. You are provided with the following information:
        Grade level taught by the teacher: {grade}
        Subject taught by the teacher: {subject}
        A description of their students, including key details such as age group, interests, location, and any relevant cultural or social factors: {students_description}

        Generate "exactly 3 detailed and creative personalized recommendations" for engaging students based on the grade, subject taught, and the description of the students. The project should be practical and reflect their interests and background (e.g., involving data analysis, local projects, or gamified learning).
        The output MUST be structured as valid JSON. Each recommendation must include:
        1. A "title" for the recommendation. The title must ONLY have the title of the project. Do NOT include terms like "Project 1".
        2. A detailed "project overview" describing in a paragraph about the activity or project in detail, including how students will engage with the material.
        3. A "rationale" explaining in a paragraph why this project will engage the students. Tie it back to their interests, culture, or social background, and explain how the project will make the material more engaging and relevant to their lives.

        The output MUST be structured as valid JSON, with the following format:
        {{
            "title": "<title>",
            "overview": "<description of the recommendation>",
            "rationale": "<explanation as to why the recommendation is relevant>"
        }}
        """

    def init_llm(self):
        """
        Initializes the VertexAI LLM model with the appropriate parameters.
        """
        self.llm = VertexAI(
            model="gemini-pro",
            temperature=0.2,  # Lower temperature for more structured output
            max_output_tokens=1024
        )

    def generate_recommendations(self):
        """
        Generates the personalized recommendations using LangChain and Vertex AI.
        """
        # Initialize the LLM if not already initialized
        if not self.llm:
            self.init_llm()

        # Create the LangChain prompt template
        prompt = PromptTemplate(
            input_variables=["grade", "subject", "students_description"],
            template=self.prompt_template
        )

        # Set up the sequence using RunnableSequence
        chain = prompt | self.llm

        # Run the sequence with user-provided inputs using invoke
        recommendations = chain.invoke({
            "grade": self.grade,
            "subject": self.subject,
            "students_description": self.students_description
        })

        return recommendations

# Validate the user input
def validate_input(subject: str, students_description: str) -> bool:
    """
    Validate that the input includes a teaching subject and a student description.
    """
    return bool(subject and students_description)

"""
# Main program logic
if __name__ == "__main__":
    # Gather user input
    print("Welcome to 'Connect With Them' - Personalized Student Engagement!")

    grade = "University"
    subject = "I teach Big Data Analytics"
    students_description = "They are from NYU, mostly from New York with a few international students. They are Gen Z and love memes. They also love music."

    # Project ID and location for Vertex AI initialization
    project_id = "gemini-quizify-431202"
    location = "us-central1"

    # Initialize the Vertex AI project with the given project ID and location
    vertexai.init(project=project_id, location=location)
    
    # Validate input
    if not validate_input(subject, students_description):
        print("Error: Please provide both a teaching subject and a description of your students.")
    else:
        print("\nGenerating personalized recommendations for classroom engagement...\n")
        
        # Create a recommendation generator instance
        generator = CWTRecommendationGenerator(grade, subject, students_description)
        
        # Generate recommendations
        recommendations = generator.generate_recommendations()

        # Print recommendations
        print("Here are your personalized recommendations:\n")
        print(recommendations)

        # Write recommendations to a file
        with open('recommendations_output.json', 'w') as outfile:
            json.dump(recommendations, outfile, indent=4)

        print("Recommendations have been saved to 'recommendations_output.json'.")
        """
