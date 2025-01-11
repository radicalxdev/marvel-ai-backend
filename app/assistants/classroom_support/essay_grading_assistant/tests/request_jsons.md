# Request JSONs for manual endpoint testing

## Generate Grading and Feedback for a List of Essays

```json
{
   "assistant_inputs":{
      "assistant_group":"classroom_support",
      "assistant_name":"essay_grading_assistant",
      "user_info":{
         "user_name":"Aaron Sosa",
         "user_age":26,
         "user_preference":"Senior AI Engineer"
      },
      "messages":[
         {
            "role":"human",
            "type":"text",
            "timestamp":"string",
            "payload":{
               "text":"Hi"
            }
         },
         {
            "role":"ai",
            "type":"text",
            "timestamp":null,
            "payload":{
               "text":"Hello Aaron, it's great to connect with you! As a Senior AI Engineer, you're likely juggling a lot of complex tasks. I'm here to help make your work a bit easier by assisting with essay grading. Just let me know how I can be of service today.\n"
            }
         },
         {
            "role":"human",
            "type":"text",
            "timestamp":"string",
            "payload":{
               "text":{
                        "grade_level": "university",
                        "point_scale": 4,
                        "assignment_description": "Write an essay on Linear Regression",
                        "rubric_objectives": "Understanding Linear Regression Concept, Clear analysis, evidence and informative examples, Clarity on structure and grammar",
                        "rubric_objectives_file_url": "",
                        "rubric_objectives_file_type": "",
                        "writing_to_review_list": [
                            {
                                "writing_to_review": "",
                                "writing_to_review_file_url": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
                                "writing_to_review_file_type": "pdf"
                            },
                            {
                                "writing_to_review": "",
                                "writing_to_review_file_url": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link",
                                "writing_to_review_file_type": "gdoc"
                            },
                            {
                                "writing_to_review": "",
                                "writing_to_review_file_url": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml",
                                "writing_to_review_file_type": "xml"
                            }
                        ],
                        "lang": "en"
                    }
            }
         }
      ]
   }
}
```

## User Query to summarize previous output of Essay Grading Assistant

```json
{
   "assistant_inputs":{
      "assistant_group":"classroom_support",
      "assistant_name":"essay_grading_assistant",
      "user_info":{
         "user_name":"Aaron Sosa",
         "user_age":26,
         "user_preference":"Senior AI Engineer"
      },
      "messages":[
         {
            "role":"human",
            "type":"text",
            "timestamp":"string",
            "payload":{
               "text":{
                        "grade_level": "university",
                        "point_scale": 4,
                        "assignment_description": "Write an essay on Linear Regression",
                        "rubric_objectives": "Understanding Linear Regression Concept, Clear analysis, evidence and informative examples, Clarity on structure and grammar",
                        "rubric_objectives_file_url": "",
                        "rubric_objectives_file_type": "",
                        "writing_to_review_list": [
                            {
                                "writing_to_review": "",
                                "writing_to_review_file_url": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
                                "writing_to_review_file_type": "pdf"
                            },
                            {
                                "writing_to_review": "",
                                "writing_to_review_file_url": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link",
                                "writing_to_review_file_type": "gdoc"
                            },
                            {
                                "writing_to_review": "",
                                "writing_to_review_file_url": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml",
                                "writing_to_review_file_type": "xml"
                            }
                        ],
                        "lang": "en"
                    }
            }
         },
         {
            "role":"ai",
            "type":"text",
            "timestamp":null,
            "payload":{
               "text":{
                                        "rubric": {
                                            "title": "Linear Regression Essay Rubric",
                                            "grade_level": "university",
                                            "criterias": [
                                                {
                                                    "criteria": "Understanding of Linear Regression",
                                                    "criteria_description": [
                                                        {
                                                            "points": "Excellent (4 points)",
                                                            "description": [
                                                                "Demonstrates a comprehensive understanding of linear regression, including its assumptions, limitations, and applications.  Accurately explains the concept of correlation and regression, and distinguishes between them.  Provides insightful examples and demonstrates a nuanced understanding of the model's strengths and weaknesses."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Good (3 points)",
                                                            "description": [
                                                                "Shows a good understanding of linear regression, but may lack depth in certain areas.  Explains the core concepts reasonably well, with some minor inaccuracies or omissions. Provides relevant examples, but may not fully explore the nuances of the model."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Fair (2 points)",
                                                            "description": [
                                                                "Displays a basic understanding of linear regression, but with significant gaps in knowledge.  Explanation of concepts is superficial and may contain several inaccuracies.  Examples provided are limited and lack depth."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Poor (1 point)",
                                                            "description": [
                                                                "Demonstrates a limited or inaccurate understanding of linear regression.  Fails to adequately explain key concepts and provides few or irrelevant examples.  Shows a lack of grasp of the fundamental principles."
                                                            ]
                                                        }
                                                    ]
                                                },
                                                {
                                                    "criteria": "Analysis, Evidence, and Examples",
                                                    "criteria_description": [
                                                        {
                                                            "points": "Excellent (4 points)",
                                                            "description": [
                                                                "Provides a clear, insightful, and well-supported analysis of linear regression.  Uses strong and relevant evidence to support claims.  Examples are well-chosen, illustrative, and effectively integrated into the analysis.  Demonstrates critical thinking and a sophisticated understanding of the subject matter."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Good (3 points)",
                                                            "description": [
                                                                "Offers a good analysis of linear regression, but may lack depth or sophistication in some areas.  Evidence is generally relevant, but could be stronger in certain instances.  Examples are appropriate but may not be as insightful or well-integrated as in a higher-scoring response."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Fair (2 points)",
                                                            "description": [
                                                                "Analysis is superficial and lacks depth.  Evidence is weak or insufficient to support claims.  Examples are limited or poorly chosen.  The analysis demonstrates a basic understanding but lacks critical evaluation."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Poor (1 point)",
                                                            "description": [
                                                                "Analysis is weak, inaccurate, or largely absent.  Evidence is missing or irrelevant.  Examples are inappropriate or missing entirely.  Demonstrates a significant lack of understanding of how to analyze linear regression."
                                                            ]
                                                        }
                                                    ]
                                                },
                                                {
                                                    "criteria": "Clarity, Structure, and Grammar",
                                                    "criteria_description": [
                                                        {
                                                            "points": "Excellent (4 points)",
                                                            "description": [
                                                                "Essay is exceptionally clear, well-structured, and well-written.  The writing is concise, engaging, and free of grammatical errors and stylistic flaws.  The organization is logical and enhances the overall clarity of the essay."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Good (3 points)",
                                                            "description": [
                                                                "Essay is generally clear and well-structured, with minor flaws in organization or style.  There may be a few grammatical errors or stylistic inconsistencies, but they do not significantly impede understanding."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Fair (2 points)",
                                                            "description": [
                                                                "Essay is somewhat unclear and/or poorly structured.  There are several grammatical errors and stylistic flaws that affect readability and comprehension.  Organization is weak and detracts from the overall clarity."
                                                            ]
                                                        },
                                                        {
                                                            "points": "Poor (1 point)",
                                                            "description": [
                                                                "Essay is unclear, poorly organized, and contains numerous grammatical errors and stylistic flaws that severely impede understanding.  The writing is difficult to follow and lacks coherence."
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ],
                                            "feedback": "This rubric aligns well with the learning objectives by assessing understanding of linear regression, analytical skills, and writing proficiency.  The four-point scale allows for nuanced evaluation of student work, promoting fair and balanced grading.  Each criterion is clearly defined, and the descriptions for each point level provide specific examples of student performance, ensuring transparency and consistency in grading."
                                        },
                                        "essay_grading_output_list": [
                                            {
                                                "criteria_grading": [
                                                    {
                                                        "criterion": {
                                                            "criteria": "Understanding of Linear Regression",
                                                            "criteria_description": [
                                                                {
                                                                    "points": "Excellent (4 points)",
                                                                    "description": [
                                                                        "Demonstrates a comprehensive understanding of linear regression, including its assumptions, limitations, and applications.  Accurately explains the concept of correlation and regression, and distinguishes between them.  Provides insightful examples and demonstrates a nuanced understanding of the model's strengths and weaknesses."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Good (3 points)",
                                                                    "description": [
                                                                        "Shows a good understanding of linear regression, but may lack depth in certain areas.  Explains the core concepts reasonably well, with some minor inaccuracies or omissions. Provides relevant examples, but may not fully explore the nuances of the model."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Fair (2 points)",
                                                                    "description": [
                                                                        "Displays a basic understanding of linear regression, but with significant gaps in knowledge.  Explanation of concepts is superficial and may contain several inaccuracies.  Examples provided are limited and lack depth."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Poor (1 point)",
                                                                    "description": [
                                                                        "Demonstrates a limited or inaccurate understanding of linear regression.  Fails to adequately explain key concepts and provides few or irrelevant examples.  Shows a lack of grasp of the fundamental principles."
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        "grade": 4,
                                                        "reasoning": "The provided text demonstrates a comprehensive understanding of linear regression. It accurately explains the core concepts, including the relationship between explanatory and dependent variables, the use of scatterplots to assess relationships, the meaning of the correlation coefficient, and the equation of a linear regression line. The text also delves into important considerations such as the method of least squares, the impact of outliers, the presence of lurking variables, and the dangers of extrapolation. The explanation is clear, concise, and covers all the key aspects of linear regression, indicating a nuanced understanding of the model's strengths and weaknesses."
                                                    },
                                                    {
                                                        "criterion": {
                                                            "criteria": "Analysis, Evidence, and Examples",
                                                            "criteria_description": [
                                                                {
                                                                    "points": "Excellent (4 points)",
                                                                    "description": [
                                                                        "Provides a clear, insightful, and well-supported analysis of linear regression.  Uses strong and relevant evidence to support claims.  Examples are well-chosen, illustrative, and effectively integrated into the analysis.  Demonstrates critical thinking and a sophisticated understanding of the subject matter."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Good (3 points)",
                                                                    "description": [
                                                                        "Offers a good analysis of linear regression, but may lack depth or sophistication in some areas.  Evidence is generally relevant, but could be stronger in certain instances.  Examples are appropriate but may not be as insightful or well-integrated as in a higher-scoring response."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Fair (2 points)",
                                                                    "description": [
                                                                        "Analysis is superficial and lacks depth.  Evidence is weak or insufficient to support claims.  Examples are limited or poorly chosen.  The analysis demonstrates a basic understanding but lacks critical evaluation."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Poor (1 point)",
                                                                    "description": [
                                                                        "Analysis is weak, inaccurate, or largely absent.  Evidence is missing or irrelevant.  Examples are inappropriate or missing entirely.  Demonstrates a significant lack of understanding of how to analyze linear regression."
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        "grade": 2,
                                                        "reasoning": "The analysis provided is superficial and lacks depth. While the essay touches on key concepts like explanatory and dependent variables, correlation coefficients, and the least-squares method, it doesn't delve into the nuances of these concepts. The essay mentions outliers and lurking variables but doesn't provide a strong analysis of their impact on linear regression. The examples are limited and not well-integrated into the analysis. The essay demonstrates a basic understanding of linear regression but lacks critical evaluation and insightful analysis."
                                                    },
                                                    {
                                                        "criterion": {
                                                            "criteria": "Clarity, Structure, and Grammar",
                                                            "criteria_description": [
                                                                {
                                                                    "points": "Excellent (4 points)",
                                                                    "description": [
                                                                        "Essay is exceptionally clear, well-structured, and well-written.  The writing is concise, engaging, and free of grammatical errors and stylistic flaws.  The organization is logical and enhances the overall clarity of the essay."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Good (3 points)",
                                                                    "description": [
                                                                        "Essay is generally clear and well-structured, with minor flaws in organization or style.  There may be a few grammatical errors or stylistic inconsistencies, but they do not significantly impede understanding."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Fair (2 points)",
                                                                    "description": [
                                                                        "Essay is somewhat unclear and/or poorly structured.  There are several grammatical errors and stylistic flaws that affect readability and comprehension.  Organization is weak and detracts from the overall clarity."
                                                                    ]
                                                                },
                                                                {
                                                                    "points": "Poor (1 point)",
                                                                    "description": [
                                                                        "Essay is unclear, poorly organized, and contains numerous grammatical errors and stylistic flaws that severely impede understanding.  The writing is difficult to follow and lacks coherence."
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        "grade": 3,
                                                        "reasoning": "The provided text is generally clear and well-structured, presenting information about linear regression, lurking variables, and extrapolation in a logical manner. There are no significant grammatical errors that impede understanding. However, the text is not exceptionally engaging or concise, and it lacks a strong introduction or conclusion that would elevate it to the 'Excellent' category. The organization is good, but it could be improved with more explicit transitions between topics. While the writing is functional, it doesn't demonstrate the stylistic polish expected for a top score."
                                                    }
                                                ],
                                                "feedback": {
                                                    "title": "Feedback on Your Writing: Write an essay on Linear Regression",
                                                    "areas_of_strength": {
                                                        "title": "Areas of Strength",
                                                        "points": [
                                                            "Solid Understanding of Core Concepts: The essay demonstrates a strong grasp of fundamental linear regression concepts, including the relationship between variables, scatterplots, correlation coefficients, and the regression equation.  The grader specifically praised the comprehensive explanation of these elements, indicating a clear understanding of the topic.",
                                                            "Logical Structure and Clarity: The essay presents the information in a logical and organized manner, making it easy to follow the writer's train of thought. The grader noted the clarity and structure as positive aspects, suggesting that the essay effectively communicates its points.",
                                                            "Correct Grammar and Readability: The writing is free of major grammatical errors, ensuring that the content is easily understandable. The grader highlighted the clarity of the writing, which is crucial for effective communication in an academic setting.",
                                                            "Inclusion of Key Considerations: The essay goes beyond the basics by addressing important aspects of linear regression such as the least squares method, outliers, lurking variables, and extrapolation.  This demonstrates a broader understanding of the topic and its practical implications."
                                                        ]
                                                    },
                                                    "areas_for_growth": {
                                                        "title": "Areas for Growth",
                                                        "points": [
                                                            "**Content Depth:** While the essay demonstrates a good foundational understanding of linear regression, it needs more depth.  The essay mentions important concepts like outliers, lurking variables, and extrapolation, but it doesn't explore their impact on the model in sufficient detail. For example, instead of just mentioning outliers, discuss how they can skew the regression line and how to address them (e.g., robust regression techniques).  Similarly, provide a more in-depth analysis of how lurking variables can lead to spurious correlations and how to control for them (e.g., multiple regression). Expand on the dangers of extrapolation with concrete examples and explain why predictions outside the range of observed data are unreliable.",
                                                            "**Clarity and Examples:** The essay would benefit from clearer and more illustrative examples. The current examples are quite general. Instead of just mentioning 'weights of individuals to their heights,' provide a specific, hypothetical dataset and demonstrate how a linear regression model would be applied. This would make the concepts more tangible and easier to understand.  When discussing lurking variables, provide a more compelling example than 'political or economic cycles.'  A more concrete example with hypothetical or real-world data would significantly strengthen the argument.  Similarly, when discussing extrapolation, a concrete example showing the absurdity of extrapolating far beyond the observed data range would be beneficial.",
                                                            "**Logical Argumentation and Structure:** While the structure is generally logical, the essay lacks a strong introduction and conclusion. The introduction should clearly state the purpose of the essay and provide a brief overview of linear regression. The conclusion should summarize the key points discussed and offer some final insights.  Additionally, stronger transitions between paragraphs would improve the flow and coherence of the essay.  For instance, when transitioning from discussing the basic concepts to the limitations of linear regression, use a transition phrase to signal the shift in focus.  This would make the essay's argumentation more persuasive and easier to follow."
                                                        ]
                                                    },
                                                    "general_feedback": {
                                                        "title": "Writing Mechanics Feedback",
                                                        "points": [
                                                            "While the essay demonstrates a good understanding of linear regression concepts, the writing could be significantly improved.",
                                                            "The essay lacks a strong introduction and conclusion.  Start with a clear thesis statement outlining the purpose of the essay and end with a summary of key points and takeaways.",
                                                            "The text is organized logically, but transitions between paragraphs could be smoother. Use transition words and phrases (e.g., 'Furthermore,' 'However,' 'In addition') to connect ideas and improve flow.",
                                                            "The writing is functional but lacks engagement. Consider using more active voice and stronger verbs to make the writing more dynamic and interesting.",
                                                            "Although grammatically correct, the writing could be more concise. Avoid redundant phrases and ensure every sentence adds value to the overall explanation.",
                                                            "While examples are present, they are not fully developed.  Provide more detailed examples and explain how they illustrate the concepts being discussed.",
                                                            "The essay could benefit from more formal academic language. Avoid informal language or colloquialisms."
                                                        ]
                                                    }
                                                },
                                                "total_grade": "9 / 12"
                                            }
                                        ]
                                    }
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
   }
}
```
