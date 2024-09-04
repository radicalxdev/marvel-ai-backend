# Worksheet Question Generator

This project provides a framework for generating quiz and worksheet questions using a machine learning model, integrated with the LangChain framework. The system allows users to input topics, difficulty levels, and hints to generate customized questions. Additionally, it includes mechanisms to validate and ensure the quality of the generated questions by leveraging cosine similarity scores to avoid hallucinations and ensure the correctness and completeness of the questions and answers.

## Key Features

### 1. Worksheet and Quiz Question Generation
The core functionality of this tool is to generate questions based on the provided topic, level, hint, and type of question (quiz or worksheet). The `WorksheetBuilder` class is responsible for this generation process. The questions are created by invoking a machine learning model, which is configured via LangChain's VertexAI.

### 2. Parameters
- **Topic**: The subject matter for the questions.
- **Level**: The difficulty level of the questions (e.g., beginner, intermediate, advanced).
- **Hint**: A hint provided to guide the type of questions being generated (e.g., "single sentence answer questions", "multiple choice questions").
- **q_type**: Specifies whether to generate quiz questions or worksheet questions.

### 3. Question Validation
The generated questions undergo a rigorous validation process to ensure their quality and relevance.

#### a. Format Validation
For quiz questions, the generated output is validated to check for the presence of essential components such as the question, choices, the correct answer, and an explanation. For worksheet questions, the validation checks for the presence of the question, the correct answer, and an explanation.

#### b. Cosine Similarity Validation
To ensure that the questions and their corresponding answers are both relevant and accurate, the system uses a `SentenceTransformer` model to calculate cosine similarity scores between:
- The question and its answer.
- The question and its explanation.

The similarity scores help in verifying that the generated answer and explanation are indeed relevant to the question posed.

### 4. Ensuring Correctness and Avoiding Hallucinations
To avoid potential hallucinations (irrelevant or incorrect outputs from the model), the system employs the following approach:
- **Cosine Similarity Score**: The system computes cosine similarity scores between the question-answer pair and the question-explanation pair.
- **Maximum Similarity Score**: Out of the two computed cosine similarity scores, the higher score is selected to represent the relevance of the generated content.
- **Validation Threshold**: Only those questions where the maximum cosine similarity score exceeds a threshold (typically set at 0.6) are considered valid and are added to the final set of generated questions.

This approach ensures that the generated questions are not only syntactically correct but also semantically relevant to the topic, thus minimizing the risk of hallucination by the underlying language model.

## Logging and Error Handling
The system is equipped with detailed logging and error handling mechanisms. Logs are generated at each significant step of the process, including during question generation, validation, and any encountered errors. This helps in debugging and ensuring the robustness of the system.

## How to Use
1. Instantiate the `WorksheetBuilder` class with the necessary parameters, including the topic, level, hint, and question type.
2. Call the `create_questions()` method to generate quiz questions or the `create_worksheet_questions()` method to generate worksheet questions.
3. The generated questions will be validated and returned as a list of dictionaries, with each dictionary containing a question, its answer, and an explanation.

## Example
```python
executor([ToolFile(url="https://courses.edx.org/asset-v1:ColumbiaX+CSMM.101x+1T2017+type@asset+block@AI_edx_ml_5.1intro.pdf")],
         "machine learning","Masters","single sentence answer questions",5, 5)