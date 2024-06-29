# Pull Request - Upgrading Kai Loaders

## Summary

- In this pull request, we have created new loaders for the kai quizzify project that will allow for handling of docx, pptx, and csv apart from pdf.
- Created additional loader classes for extracting Web Content and Youtube Transcript.
- Performed unit and integration testing to validate them in the whole quizzify system

## Changes

- Included more imports for handling various document types, loading from different sources, and using additional functionality from LangChain.
- New helper functions were added for extracting text from DOCX and PPTX files.
- Additional class “WebPageLoader”  was added for loading contents from web pages 
- Additional class “YouTubeLoader” was added for loading transcripts, and timestamps from YouTube.
- Updates were made to the BytesFileLoader, LocalFileLoader, and UploadFileLoader classes for handling different file types including PDFs, DOC/DOCX, PPT/PPTX, and  CSV. Each file type is handled specifically to extract text content properly.
- The URLLoader class has been updated to enhance its capability to load and handle different types of files from URLs. The class can now differentiate between different types of URLs and handle YouTube links and web pages separately, using the YouTubeLoader and WebPageLoader classes, respectively. The class also includes detailed error handling and logging to track the status and issues encountered while loading files.
- Created new classes for each loaders to test locally in kai-ai-backend/app/features/quizzify/tests
- Updated requirements.txt with python-docx, pandas, python-pptx, and beautifulsoup4 for handling the new file types.
- Added missing error_utilities.py

## Unit Testing & Results

### For DOCXLoader unit testing:
- Type of Testing: Manual testing (basic functional testing)
- Purpose: To validate that the docxLoader class correctly loads DOCXfiles and converts them into Document objects.
- Methodology: This involves running the code with a specific input to verify that it behaves as expected. Executed the load method of the DOCXLoader class with a sample docx file and verified the output.
- Results: The DOCXLoader successfully loaded the sample docx file. The output was a list of Document objects with the correct content and metadata.

### For WebPageLoader unit testing:
- Type of Testing: Manual testing (basic functional testing)
- Purpose: To be able to upload website urls into quizzify to get information from necessary websites.
- Methodology: This involves running the code with a specific input to verify that it behaves as expected. Executed the load method of the WebPageLoader.py class with a sample web based url and verified that content such as headings, paragraphs, lists and tables were able to upload from the url.
- Results: The WebBaseLoader class was able to run given a web url. Was able to transform the information into a document object with the correct content and metadata.

### For YoutubeLoader unit testing:
- Type of Testing: Manual testing (basic functional testing)
- Purpose: To be able to upload Youtube videos and extract the transcript within user specidied time stamps to get the information from the video.
- Methodology: This involves creating plain text content from the transcript and then creating a Document object with page content and metadata. Executed the load method of the YoutubeLoader.py class with a sample Youtube video.
- Results: The YoutubeLoader class was able to run given a video. Was able to transform the transcript into a document object with the correct content and metadata.

#### In terms of unit testing, the same testing type, purpose, methodology and results were used for csv, doc, pptx, and pdf, as seen above for docx.

## Integration Testing & Results

### Type of testing: Adhoc Testing with FastAPI Swagger UI
- Methodology
Used the Swagger UI to manually input the JSON request to the /submit-tool endpoint
Monitored the responses and system behavior, checking for correctness and performance.
Resolved any bugs or issues identified during integration testing.
- Purpose
To verify the stability and performance of the new loaders in the complete Quizzify system.
- Results
The integration test confirmed that the content extracted by the all these loaders is correctly utilized by the entire quizzify system and generated multiple choice question


## Notes
These features are intended to expand the scope of Kai so that it can intake documents from various different file types aside from .pdf.
Added detailed error handling in file loaders to provide informative error messages. Ensured that unsupported file types are correctly identified and handled.
In the future, the ability to generate quizzes for specific sections of various document types will be added. This includes generating quizzes from specific pages of PDF files, specific paragraphs from web pages and DOCX files, specific slides from PPTX presentations, specific rows or columns from CSV files, and specific timestamps from YouTube videos. The updated code supports extracting specific contents from each of them for such implication.
Additionally, grading of quizzes in Quizzify and personalized responses can be implemented to further improve upon Kai’s assisting skills.

## Screenshots

https://docs.google.com/document/d/12EsMTSSsa--GmEPsp59r9PldBfG0FYcZmohKXRUartw/edit

## How to Test

Use the Swagger UI to manually input the JSON request to the /submit-tool endpoint.
Sample JSON requests for each of these loaders are as follows:

### For Docx: 
- Sample Request:
```json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "macrosystems ecology"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "uploads/ac7c6ef5-51c4-4a24-b7e4-043e3f6f9fbd-certificate.docx",
                        "url": "https://firebasestorage.googleapis.com/v0/b/fahira-quizzify.appspot.com/o/student_handout_23sep22.docx?alt=media&embedded=true",
                        "filename": "certificate.docx"
                    }
                ]
            }
        ]
    }
}
```
- Sample Response:
```json
{
  "data": [
    {
      "question": "What is the focus of macrosystems ecology?",
      "choices": [
        {
          "key": "A",
          "value": "The study of ecological dynamics across multiple scales"
        },
        {
          "key": "B",
          "value": "The study of ecosystems at the global level"
        },
        {
          "key": "C",
          "value": "The study of the interactions between humans and ecosystems"
        },
        {
          "key": "D",
          "value": "The study of the effects of climate change on ecosystems"
        }
      ],
      "answer": "A",
      "explanation": "Macrosystems ecology focuses on understanding ecological dynamics at multiple interacting spatial and temporal scales."
    }
  ]
}
```

### For PPTx:
- Sample Request:
```json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "AI"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "uploads/ac7c6ef5-51c4-4a24-b7e4-043e3f6f9fbd-certificate.pptx",
                        "url": "https://firebasestorage.googleapis.com/v0/b/fahira-quizzify.appspot.com/o/TLC AI in the Classroom.pptx?alt=media&embedded=true",
                        "filename": "certificate.pptx"
                    }
                ]
            }
        ]
    }
}
```
- Sample Response:
```json
{
  "data": [
    {
      "question": "Which of the following is NOT a capability of Generative AI?",
      "choices": [
        {
          "key": "A",
          "value": "Creating text, images, or code from scratch"
        },
        {
          "key": "B",
          "value": "Summarizing and analyzing articles"
        },
        {
          "key": "C",
          "value": "Translating languages"
        },
        {
          "key": "D",
          "value": "Providing answers to factual questions"
        }
      ],
      "answer": "D",
      "explanation": "Generative AI is capable of creating new content, but it is not able to provide answers to factual questions."
    }
  ]
}
```
### For CSV:
- Sample Request:
```Json

{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "Customer"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "uploads/ac7c6ef5-51c4-4a24-b7e4-043e3f6f9fbd-certificate.csv",
                        "url": "https://firebasestorage.googleapis.com/v0/b/fahira-quizzify.appspot.com/o/customers-100.csv?alt=media&embedded=true",
                        "filename": "certificate.csv"
                    }
                ]
            }
        ]
    }
}
``` 

- Sample Response:
```json
{
  "data": [
    {
      "question": "Which customer has the first name 'Sherry'?",
      "choices": [
        {
          "key": "A",
          "value": "Sheryl"
        },
        {
          "key": "B",
          "value": "Sherry"
        },
        {
          "key": "C",
          "value": "Kiara"
        },
        {
          "key": "D",
          "value": "Colleen"
        }
      ],
      "answer": "B",
      "explanation": "The customer with the first name 'Sherry' is listed in row 93 with the customer ID '54B5B5Fe9F1B6C5'."
    }
  ]
}
```
### For Webpage:
- Sample Request:
```Json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "describe dog"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "dummy",
                        "url": "https://www.toppr.com/guides/essays/essay-on-dog/",
                        "filename": "dummy"
                    }
                ]
            }
        ]
    }
}

```

- Sample Response:
```json
{
  "data": [
    {
      "question": "Which of the following is a characteristic of dogs?",
      "choices": [
        {
          "key": "A",
          "value": "They have sharp claws."
        },
        {
          "key": "B",
          "value": "They are known for their loyalty."
        },
        {
          "key": "C",
          "value": "They primarily eat plants."
        },
        {
          "key": "D",
          "value": "They have poor hearing."
        }
      ],
      "answer": "B",
      "explanation": "Dogs are known for their loyalty and companionship, which is why they are often referred to as 'man's best friend.'"
    }
  ]
}
```

### For YouTube:
- Sample Request:
```Json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "Negative thoughts"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": " ",
                        "url": "https://youtu.be/8yRvb07tP0M?si=-Ku4TcwBbbMhLr0K",
                        "filename": " "
                    }
                ]
            }
        ]
    }
}
```
- Sample Response:
```json
{
  "data": [
    {
      "question": "What is one of the key principles of Stoicism?",
      "choices": [
        {
          "key": "A",
          "value": "That our actions are the only things we can control."
        },
        {
          "key": "B",
          "value": "That our thoughts shape our reality."
        },
        {
          "key": "C",
          "value": "That we should live in accordance with nature."
        },
        {
          "key": "D",
          "value": "That we should seek pleasure and avoid pain."
        }
      ],
      "answer": "B",
      "explanation": "One of the core principles of Stoicism is the idea that our thoughts shape our reality. This is because our thoughts create our perceptions of the world, which in turn influence our emotions and actions."
    }
  ]
}

```
### For PDF:
- Sample Request:
```Json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "Claims"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "uploads/ac7c6ef5-51c4-4a24-b7e4-043e3f6f9fbd-certificate.pdf",
                        "url": "https://firebasestorage.googleapis.com/v0/b/fahira-quizzify.appspot.com/o/Annual-Claims-Report-FY2022.pdf?alt=media&token=ee07d2f9-1a1c-4682-ac82-b8337b516e7e",
                        "filename": "certificate.pdf"
                    }
                ]
            }
        ]
    }
}
```
- Sample Response:
```json
{
  "data": [
    {
      "question": "What type of claims include claims by private individuals seeking refunds for alleged overpayments and unjust fines?",
      "choices": [
        {
          "key": "A",
          "value": "Affirmative claims"
        },
        {
          "key": "B",
          "value": "Contract claims"
        },
        {
          "key": "C",
          "value": "Refund claims"
        },
        {
          "key": "D",
          "value": "Special education claims"
        }
      ],
      "answer": "C",
      "explanation": "Refund claims include claims by private individuals seeking refunds for alleged overpayments and unjust fines."
    }
  ]
}
```
### For Multiple File Types:
- Sample Request:
```Json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 0,
        "inputs": [
            {
                "name": "topic",
                "value": "What are dogs good for?"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "uploads/ac7c6ef5-51c4-4a24-b7e4-043e3f6f9fbd-certificate.pdf",
                        "url": "https://firebasestorage.googleapis.com/v0/b/fahira-quizzify.appspot.com/o/Annual-Claims-Report-FY2022.pdf?alt=media&token=ee07d2f9-1a1c-4682-ac82-b8337b516e7e",
                        "filename": "certificate.pdf"
                    },
                    {
                        "filePath": " ",
                        "url": "https://youtu.be/8yRvb07tP0M?si=-Ku4TcwBbbMhLr0K",
                        "filename": " "
                    },
                    {
                        "filePath": "dummy",
                        "url": "https://www.toppr.com/guides/essays/essay-on-dog/",
                        "filename": "dummy"
                    }
                ]
            }
        ]
    }
}
```
- Sample Response:
```Json
{
  "data": [
    {
      "question": "What is one of the benefits of having dogs?",
      "choices": [
        {
          "key": "A",
          "value": "They can help reduce stress"
        },
        {
          "key": "B",
          "value": "They can help you get exercise"
        },
        {
          "key": "C",
          "value": "They can help you meet new people"
        },
        {
          "key": "D",
          "value": "All of the above"
        }
      ],
      "answer": "D",
      "explanation": "All of the listed choices are benefits of having dogs."
    }
  ]
}
```
