import pytest

from app.assistants.classroom_support.essay_grading_assistant.core import executor
from app.services.assistant_registry import Message, MessagePayload, MessageType, Role, UserInfo

base_attributes = {
    "user_info": UserInfo(
        user_name="Aaron",
        user_age=30,
        user_preference="Senior AI Engineer"
    )
}

"""
    "grade_level": None,
    "point_scale": None,
    "assignment_description": None,
    "rubric_objectives": None,
    "rubric_objectives_file_url": None,
    "rubric_objectives_file_type": None,
    "writing_to_review": None,
    "writing_to_review_file_url": None,
    "writing_to_review_file_type": None,
    "lang": None
"""

#=============================ESSAY GRADING REQUEST TESTS=============================
def test_executor_grading_valid_rubric_text_writing_to_review_pdf():
    result = executor(
        **base_attributes,
        messages = [
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Hi"
                )
            ),
            Message(
                role=Role.ai,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Hello Aaron, it's great to connect with you! As a Senior AI Engineer, you're likely juggling a lot of complex tasks. I'm here to help make your work a bit easier by assisting with essay grading. Just let me know how I can be of service today.\n"
                )
            ),
            Message(
                role=Role.system,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text={
                        "grade_level": "university",
                        "point_scale": 4,
                        "assignment_description": "",
                        "rubric_objectives": "Understanding Linear Regression Concept, Clear analysis, evidence and informative examples, Clarity on structure and grammar",
                        "rubric_objectives_file_url": "",
                        "rubric_objectives_file_type": "",
                        "writing_to_review": "",
                        "writing_to_review_file_url": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
                        "writing_to_review_file_type": "pdf",
                        "lang": "en"
                    }
                )
            )
        ]
    )
    assert isinstance(result, dict)

#=============================NON ESSAY GRADING REQUEST TESTS=============================
def test_executor_summarize_valid():
    result = executor(
        **base_attributes,
        messages = [
            Message(
                role=Role.system,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Generate essay grading with these arguments: {'grade_level': 'university', 'point_scale': 4, 'assignment_description': '', 'rubric_objectives': 'Understanding Linear Regression Concept, Clear analysis, evidence and informative examples, Clarity on structure and grammar', 'rubric_objectives_file_url': '', 'rubric_objectives_file_type': '', 'writing_to_review': '', 'writing_to_review_file_url': 'https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd', 'writing_to_review_file_type': 'pdf', 'lang': 'en'}"
                )
            ),
            Message(
                role=Role.ai,
                type=MessageType.text,
                timestamp=None,
                payload=MessagePayload(
                    text="""
                        {
                        "criteria_grading": [
                            {
                                "criterion": {
                                    "criteria": "Understanding of Linear Regression Concepts",
                                    "criteria_description": [
                                        {
                                            "points": "Excellent (4 points)",
                                            "description": [
                                                "Demonstrates a comprehensive understanding of linear regression concepts, including assumptions, limitations, and interpretations. Accurately explains the relationship between variables and provides insightful interpretations of model outputs."
                                            ]
                                        },
                                        {
                                            "points": "Good (3 points)",
                                            "description": [
                                                "Shows a good understanding of linear regression concepts.  May have minor inaccuracies in explaining relationships or interpreting model outputs.  Demonstrates understanding of key concepts but may lack depth in certain areas."
                                            ]
                                        },
                                        {
                                            "points": "Fair (2 points)",
                                            "description": [
                                                "Displays a basic understanding of linear regression concepts but shows significant gaps in knowledge.  Explanations of relationships and interpretations of model outputs are superficial or contain several inaccuracies."
                                            ]
                                        },
                                        {
                                            "points": "Poor (1 point)",
                                            "description": [
                                                "Demonstrates a limited or inaccurate understanding of linear regression concepts.  Unable to adequately explain relationships between variables or interpret model outputs.  Significant misconceptions are present."
                                            ]
                                        }
                                    ]
                                },
                                "grade": 3,
                                "reasoning": "The writing demonstrates a good understanding of linear regression concepts by explaining that it models the relationship between two variables using a linear equation, identifying explanatory and dependent variables, and mentioning the importance of determining a relationship before fitting the model. It also correctly notes that correlation does not equal causation and suggests using a scatterplot to check the strength of a relationship. The writing also touches on lurking variables and the dangers of extrapolation, showing a broader understanding of the limitations. However, while it touches on key concepts, it lacks depth in areas like specific assumptions of linear regression (linearity, independence, homoscedasticity, normality of residuals) and detailed interpretation of model outputs (like R-squared, p-values, coefficients). Therefore, it does not fully meet the criteria for 'Excellent' but exceeds 'Fair' and is rated as 'Good'."
                            },
                            {
                                "criterion": {
                                    "criteria": "Analysis, Evidence, and Examples",
                                    "criteria_description": [
                                        {
                                            "points": "Excellent (4 points)",
                                            "description": [
                                                "Analysis is thorough, insightful, and supported by strong evidence and relevant, informative examples.  Clearly demonstrates critical thinking and a deep understanding of the data."
                                            ]
                                        },
                                        {
                                            "points": "Good (3 points)",
                                            "description": [
                                                "Analysis is generally sound and well-supported by evidence.  Examples are relevant but may lack depth or sophistication.  Shows a good understanding of the data but could be more insightful."
                                            ]
                                        },
                                        {
                                            "points": "Fair (2 points)",
                                            "description": [
                                                "Analysis is superficial and lacks sufficient evidence or relevant examples.  Conclusions are weakly supported or may be inaccurate.  Shows limited understanding of the data."
                                            ]
                                        },
                                        {
                                            "points": "Poor (1 point)",
                                            "description": [
                                                "Analysis is missing, flawed, or unsupported by evidence.  Examples are irrelevant or absent.  Demonstrates a lack of understanding of the data and analytical skills."
                                            ]
                                        }
                                    ]
                                },
                                "grade": 3,
                                "reasoning": "The analysis is generally sound, explaining the purpose of linear regression and the importance of identifying a relationship between variables before modeling. The examples given, such as relating weights to heights and mentioning the use of scatterplots, are relevant. However, the analysis could be more insightful. The text does not delve into the nuances of how these examples relate to the data or explore the limitations of linear regression, such as lurking variables or extrapolation, which are mentioned later in the document but not explicitly connected to the initial analysis. While the text demonstrates a good understanding, it doesn't reach the depth and critical thinking required for an excellent rating."
                            },
                            {
                                "criterion": {
                                    "criteria": "Clarity, Structure, and Grammar",
                                    "criteria_description": [
                                        {
                                            "points": "Excellent (4 points)",
                                            "description": [
                                                "Writing is exceptionally clear, concise, and well-organized.  Grammar and mechanics are flawless.  The analysis is easy to follow and understand."
                                            ]
                                        },
                                        {
                                            "points": "Good (3 points)",
                                            "description": [
                                                "Writing is clear and well-organized.  Minor grammatical errors or stylistic issues may be present but do not impede understanding."
                                            ]
                                        },
                                        {
                                            "points": "Fair (2 points)",
                                            "description": [
                                                "Writing is understandable but lacks clarity or organization in places.  Several grammatical errors or stylistic issues affect readability."
                                            ]
                                        },
                                        {
                                            "points": "Poor (1 point)",
                                            "description": [
                                                "Writing is unclear, disorganized, and contains numerous grammatical errors that significantly impair understanding."
                                            ]
                                        }
                                    ]
                                },
                                "grade": 4,
                                "reasoning": "The writing is exceptionally clear, concise, and well-organized. Grammar and mechanics are flawless. The analysis is easy to follow and understand. The text provides a clear and logical explanation of linear regression, lurking variables, and extrapolation. The structure is coherent, with each topic presented in a way that builds understanding. There are no grammatical errors or stylistic issues that impede understanding."
                            }
                        ],
                        "feedback": {
                            "title": "Feedback on Your Writing: ",
                            "areas_of_strength": {
                                "title": "Areas of Strength",
                                "points": [
                                    "**Clear and Concise Explanation:** The writing provides a clear and concise explanation of the fundamental concepts of linear regression, making it easy for the reader to grasp the core ideas.",
                                    "**Well-Organized Structure:** The text follows a logical structure, starting with the basic definition of linear regression and progressing to more nuanced concepts like correlation vs. causation and the importance of checking for relationships. This organization enhances readability and understanding.",
                                    "**Effective Use of Examples:**  The use of examples, such as relating weight to height and mentioning SAT scores and college grades, helps to illustrate the concepts and make them more relatable.",
                                    "**Strong Grammar and Mechanics:** The writing is free of grammatical errors and stylistic issues, which contributes to clarity and professionalism.",
                                    "**Highlights Key Considerations:** The writing appropriately emphasizes the importance of determining a relationship between variables before fitting a model and cautions against assuming correlation implies causation."
                                ]
                            },
                            "areas_for_growth": {
                                "title": "Areas for Growth",
                                "points": [
                                    "**Content Depth:** While the writing demonstrates a good foundational understanding of linear regression, it needs more depth.  Specifically, it should elaborate on the assumptions underlying linear regression.  These include linearity (the relationship between variables is linear), independence (observations are independent of each other), homoscedasticity (constant variance of errors), and normality of residuals (errors are normally distributed).  Explaining these assumptions and their importance in ensuring the validity of the model would strengthen the writing significantly.  Additionally, the writing should delve deeper into the interpretation of model outputs.  While it mentions correlation and scatterplots, it omits important metrics like R-squared (which measures the goodness of fit), p-values (which assess the statistical significance of the coefficients), and the interpretation of the regression coefficients themselves.  Including these would demonstrate a more comprehensive understanding.",
                                    "**Clarity and Logical Argumentation:** The writing could improve the connection between concepts. For example, while lurking variables and extrapolation are mentioned, they are presented somewhat in isolation. The writing would benefit from explicitly linking these concepts back to the initial discussion of linear regression, illustrating how these factors can influence the interpretation and reliability of the model.  Provide clearer examples of how lurking variables might affect the relationship between the independent and dependent variables and demonstrate how extrapolation beyond the observed data range can lead to unreliable predictions.  Stronger examples would bolster the logical flow and clarity of the argument.",
                                    "**Data Analysis and Application:**  Although the provided writing doesn't include any specific datasets, a university-level discussion of linear regression should demonstrate the application of these concepts to data.  Future iterations should include examples of how linear regression is used to analyze data, interpret results, and draw conclusions.  This could involve discussing specific case studies or hypothetical scenarios, showcasing how the choice of variables, interpretation of model outputs, and consideration of limitations play out in practice."
                                ]
                            },
                            "general_feedback": {
                                "title": "Writing Mechanics Feedback",
                                "points": [
                                    "The writing demonstrates excellent clarity, conciseness, and organization.",
                                    "Grammar and mechanics are flawless, contributing to the overall readability.",
                                    "Sentences are well-structured and easy to follow.",
                                    "The logical flow of ideas enhances comprehension."
                                ]
                            }
                        },
                        "total_grade": "10 / 12"
                    }
                    """
                )
            ),
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Please, summarize the essay grading and feedback."
                )
            )
        ]
    )
    assert isinstance(result, str)

def test_executor_summarize_invalid():
    with pytest.raises(TypeError) as exc_info:
        executor(
            messages=[
                {
                    "role":"system",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                    "text":"Generate essay grading with these arguments: {'grade_level': 'university', 'point_scale': 4, 'assignment_description': '', 'rubric_objectives': 'Understanding Linear Regression Concept, Clear analysis, evidence and informative examples, Clarity on structure and grammar', 'rubric_objectives_file_url': '', 'rubric_objectives_file_type': '', 'writing_to_review': '', 'writing_to_review_file_url': 'https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd', 'writing_to_review_file_type': 'pdf', 'lang': 'en'}"
                    }
                },
                {
                    "role":"ai",
                    "type":"text",
                    "timestamp":None,
                    "payload":{
                    "text":"""{'criteria_grading': [{'criterion': {'criteria': 'Understanding of Linear Regression Concepts', 'criteria_description': [{'points': 'Excellent (4 points)', 'description': ['Demonstrates a comprehensive understanding of linear regression concepts, including assumptions, limitations, and interpretations. Accurately explains the relationship between variables and provides insightful interpretations of model outputs.']}, {'points': 'Good (3 points)', 'description': ['Shows a good understanding of linear regression concepts.  May have minor inaccuracies in explaining relationships or interpreting model outputs.  Demonstrates understanding of key concepts but may lack depth in certain areas.']}, {'points': 'Fair (2 points)', 'description': ['Displays a basic understanding of linear regression concepts but shows significant gaps in knowledge.  Explanations of relationships and interpretations of model outputs are superficial or contain several inaccuracies.']}, {'points': 'Poor (1 point)', 'description': ['Demonstrates a limited or inaccurate understanding of linear regression concepts.  Unable to adequately explain relationships between variables or interpret model outputs.  Significant misconceptions are present.']}]}, 'grade': 3, 'reasoning': "The writing demonstrates a good understanding of linear regression concepts by explaining that it models the relationship between two variables using a linear equation, identifying explanatory and dependent variables, and mentioning the importance of determining a relationship before fitting the model. It also correctly notes that correlation does not equal causation and suggests using a scatterplot to check the strength of a relationship. The writing also touches on lurking variables and the dangers of extrapolation, showing a broader understanding of the limitations. However, while it touches on key concepts, it lacks depth in areas like specific assumptions of linear regression (linearity, independence, homoscedasticity, normality of residuals) and detailed interpretation of model outputs (like R-squared, p-values, coefficients). Therefore, it does not fully meet the criteria for 'Excellent' but exceeds 'Fair' and is rated as 'Good'."}, {'criterion': {'criteria': 'Analysis, Evidence, and Examples', 'criteria_description': [{'points': 'Excellent (4 points)', 'description': ['Analysis is thorough, insightful, and supported by strong evidence and relevant, informative examples.  Clearly demonstrates critical thinking and a deep understanding of the data.']}, {'points': 'Good (3 points)', 'description': ['Analysis is generally sound and well-supported by evidence.  Examples are relevant but may lack depth or sophistication.  Shows a good understanding of the data but could be more insightful.']}, {'points': 'Fair (2 points)', 'description': ['Analysis is superficial and lacks sufficient evidence or relevant examples.  Conclusions are weakly supported or may be inaccurate.  Shows limited understanding of the data.']}, {'points': 'Poor (1 point)', 'description': ['Analysis is missing, flawed, or unsupported by evidence.  Examples are irrelevant or absent.  Demonstrates a lack of understanding of the data and analytical skills.']}]}, 'grade': 3, 'reasoning': "The analysis is generally sound, explaining the purpose of linear regression and the importance of identifying a relationship between variables before modeling. The examples given, such as relating weights to heights and mentioning the use of scatterplots, are relevant. However, the analysis could be more insightful. The text does not delve into the nuances of how these examples relate to the data or explore the limitations of linear regression, such as lurking variables or extrapolation, which are mentioned later in the document but not explicitly connected to the initial analysis. While the text demonstrates a good understanding, it doesn't reach the depth and critical thinking required for an excellent rating."}, {'criterion': {'criteria': 'Clarity, Structure, and Grammar', 'criteria_description': [{'points': 'Excellent (4 points)', 'description': ['Writing is exceptionally clear, concise, and well-organized.  Grammar and mechanics are flawless.  The analysis is easy to follow and understand.']}, {'points': 'Good (3 points)', 'description': ['Writing is clear and well-organized.  Minor grammatical errors or stylistic issues may be present but do not impede understanding.']}, {'points': 'Fair (2 points)', 'description': ['Writing is understandable but lacks clarity or organization in places.  Several grammatical errors or stylistic issues affect readability.']}, {'points': 'Poor (1 point)', 'description': ['Writing is unclear, disorganized, and contains numerous grammatical errors that significantly impair understanding.']}]}, 'grade': 4, 'reasoning': 'The writing is exceptionally clear, concise, and well-organized. Grammar and mechanics are flawless. The analysis is easy to follow and understand. The text provides a clear and logical explanation of linear regression, lurking variables, and extrapolation. The structure is coherent, with each topic presented in a way that builds understanding. There are no grammatical errors or stylistic issues that impede understanding.'}], 'feedback': {'title': 'Feedback on Your Writing: ', 'areas_of_strength': {'title': 'Areas of Strength', 'points': ['**Clear and Concise Explanation:** The writing provides a clear and concise explanation of the fundamental concepts of linear regression, making it easy for the reader to grasp the core ideas.', '**Well-Organized Structure:** The text follows a logical structure, starting with the basic definition of linear regression and progressing to more nuanced concepts like correlation vs. causation and the importance of checking for relationships. This organization enhances readability and understanding.', '**Effective Use of Examples:**  The use of examples, such as relating weight to height and mentioning SAT scores and college grades, helps to illustrate the concepts and make them more relatable.', '**Strong Grammar and Mechanics:** The writing is free of grammatical errors and stylistic issues, which contributes to clarity and professionalism.', '**Highlights Key Considerations:** The writing appropriately emphasizes the importance of determining a relationship between variables before fitting a model and cautions against assuming correlation implies causation.']}, 'areas_for_growth': {'title': 'Areas for Growth', 'points': ['**Content Depth:** While the writing demonstrates a good foundational understanding of linear regression, it needs more depth.  Specifically, it should elaborate on the assumptions underlying linear regression.  These include linearity (the relationship between variables is linear), independence (observations are independent of each other), homoscedasticity (constant variance of errors), and normality of residuals (errors are normally distributed).  Explaining these assumptions and their importance in ensuring the validity of the model would strengthen the writing significantly.  Additionally, the writing should delve deeper into the interpretation of model outputs.  While it mentions correlation and scatterplots, it omits important metrics like R-squared (which measures the goodness of fit), p-values (which assess the statistical significance of the coefficients), and the interpretation of the regression coefficients themselves.  Including these would demonstrate a more comprehensive understanding.', '**Clarity and Logical Argumentation:** The writing could improve the connection between concepts. For example, while lurking variables and extrapolation are mentioned, they are presented somewhat in isolation. The writing would benefit from explicitly linking these concepts back to the initial discussion of linear regression, illustrating how these factors can influence the interpretation and reliability of the model.  Provide clearer examples of how lurking variables might affect the relationship between the independent and dependent variables and demonstrate how extrapolation beyond the observed data range can lead to unreliable predictions.  Stronger examples would bolster the logical flow and clarity of the argument.', "**Data Analysis and Application:**  Although the provided writing doesn't include any specific datasets, a university-level discussion of linear regression should demonstrate the application of these concepts to data.  Future iterations should include examples of how linear regression is used to analyze data, interpret results, and draw conclusions.  This could involve discussing specific case studies or hypothetical scenarios, showcasing how the choice of variables, interpretation of model outputs, and consideration of limitations play out in practice."]}, 'general_feedback': {'title': 'Writing Mechanics Feedback', 'points': ['The writing demonstrates excellent clarity, conciseness, and organization.', 'Grammar and mechanics are flawless, contributing to the overall readability.', 'Sentences are well-structured and easy to follow.', 'The logical flow of ideas enhances comprehension.']}}, 'total_grade': '10 / 12'}"""
                    }
                },
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                    "text":"Please, summarize the essay grading and feedback."
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, TypeError)