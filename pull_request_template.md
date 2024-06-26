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
- Purpose: To be able to upload Youtube videos and extract the transcript to get the information from the video.
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

[Examples] (https://docs.google.com/document/d/12EsMTSSsa--GmEPsp59r9PldBfG0FYcZmohKXRUartw/edit)

## How to Test

Use the Swagger UI to manually input the JSON request to the /submit-tool endpoint.
Sample JSON requests for each of these loaders are as follows:

### For Docx: 
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

### For pptx:
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

### For CSV:

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
### For Webpage:

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

### For YouTube:

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
                "value": "stoic philosophy"
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
### For PDF:

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






