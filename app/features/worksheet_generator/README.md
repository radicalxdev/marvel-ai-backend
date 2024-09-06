# Worksheet Question Generator

This project provides a framework for generating quiz and worksheet questions using a machine learning model, integrated with the LangChain framework. The system allows users to input topics, difficulty levels, and hints to generate customized questions. To ensure the accuracy, quality, and relevance of the generated content, it leverages various validation mechanisms, including cosine similarity scores, to minimize hallucinations and ensure the correctness of the questions and answers.

## Key Features

### 1. Dual-Prompt Setup for Optimal Performance
Through extensive fine-tuning and prompt engineering experiments, it was discovered that using two distinct prompts yields the best results. One prompt is designed for quiz question generation, and another is tailored for worksheet question creation. This dual-prompt approach optimizes question generation by better capturing the specific nuances of each question type, leading to higher-quality and more relevant outputs. 

### 2. Worksheet and Quiz Question Generation
The core functionality of this tool is to generate questions based on the provided topic, level, hint, and question type (quiz or worksheet). The `WorksheetBuilder` class is responsible for this generation process. By invoking machine learning models, configured through LangChain's VertexAI, the system can generate customized questions with high accuracy.

### 3. Parameters
- **Topic**: The subject matter for the questions.
- **Level**: The difficulty level of the questions (e.g., beginner, intermediate, advanced).
- **Hint**: A hint to guide the style or focus of the questions (e.g., "single sentence answer questions" or "multiple choice questions").
- **q_type**: Specifies whether to generate quiz questions or worksheet questions.

### 4. Question Validation
The generated questions undergo several layers of validation to ensure quality, relevance, and correctness.

#### a. Format Validation
For **quiz questions**, validation checks for essential components such as the question, multiple answer choices, the correct answer, and an explanation. For **worksheet questions**, it ensures the presence of the question, the correct answer, and an explanation.

#### b. Cosine Similarity Validation
To further ensure the relevance of the question-answer pair:
- The system uses a `SentenceTransformer` model to calculate cosine similarity scores between:
  - The question and its answer.
  - The question and its explanation.
- These scores help validate whether the generated answer and explanation are semantically aligned with the question.

### 5. Correctness and Avoiding Hallucinations
To avoid irrelevant or incorrect outputs (hallucinations) from the language model, the system implements the following approach:
- **Cosine Similarity Score**: The system computes similarity scores between the question-answer pair and the question-explanation pair.
- **Maximum Similarity Score**: The higher score between these two pairs is chosen as a measure of content relevance.
- **Validation Threshold**: Only questions where the cosine similarity score exceeds a pre-set threshold (typically 0.6) are deemed valid and added to the final set of generated questions.

This validation pipeline ensures that the generated questions are not only syntactically correct but also semantically aligned with the topic, minimizing the risk of irrelevant or nonsensical questions.

### 6. Logging and Error Handling
The system includes detailed logging and error handling mechanisms. Logs capture key stages such as question generation, validation, and any encountered errors. This makes debugging and system monitoring more efficient.

## How to Use

1. Instantiate the `WorksheetBuilder` class with the necessary parameters, including the topic, level, hint, and question type.
2. Use one of the two dedicated prompts based on your requirements:
   - For quiz generation, call the `create_questions()` method.
   - For worksheet generation, use the `create_worksheet_questions()` method.
3. The system will generate, validate, and return the questions as a list of dictionaries. Each dictionary contains a question, its answer, and an explanation.

## Example Usage
```python
executor([ToolFile(url="https://courses.edx.org/asset-v1:ColumbiaX+CSMM.101x+1T2017+type@asset+block@AI_edx_ml_5.1intro.pdf")],
         "machine learning", "Masters", "single sentence answer questions", 5, 5)
