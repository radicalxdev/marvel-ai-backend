# Pull Request - Added Functionality to Kai Loaders

## Summary
Created new loaders to handle docx, pptx, csv, txt, youtube links, and web links
Created Unit tests to test these new loaders and to test multiple loaders at once

## Changes
Renamed BytesFilePDFLoader to PDFLoader for consitency with the other loaders
Made a class for each loader
- PDFLoader
- DOCXLoader
- PPTXLoader
- CSVLoader
- TXTLoader
- YouTubeLoader
- WebPageLoader
Routed to these loaders using URLLoader for seamless integration

## Testing
The loaders were tested with manual testing and unit tests using pytest
- Manual testing covered mutltiple questions and multiple files for each loader
- Used offensive testing practices to identify any issues with the loaders and how to use the API
- Unit tests were made for each loader, and tests that the loader can generate a Document from a URL
- Another unit test was created to test if it could generate a Document from multiple files

## Results
Created a series of new loaders that add functionality to Kai
Screenshots of this working are here: https://docs.google.com/document/d/15Vqf3E2PuZtapccfHPSYOCcIGJbXaYGUr3e3AZ9DfHs/edit?usp=sharing

## How to Test
Open up the API using whatever method works best for you, type dev into the api key and use these sample JSON requests to test each loader

PDF:
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
                "value": "Convolutional Neural Network"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://firebasestorage.googleapis.com/v0/b/nano-knights-9b750.appspot.com/o/CNN.pdf?alt=media&token=d608d447-8e2a-44b8-8c89-c303fd25cd20",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}

DOCX:
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
                "value": "Agile Development"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://firebasestorage.googleapis.com/v0/b/nano-knights-9b750.appspot.com/o/Documentation_Strategies_on_Agile_Software_Develop.docx?alt=media&token=bd93539b-bcc2-45b0-8ef3-a1d751393d69",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}

PPTX:
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
                "value": "Refactoring"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://firebasestorage.googleapis.com/v0/b/nano-knights-9b750.appspot.com/o/Refactoring-Part%201.pptx?alt=media&token=7017f116-af19-400f-9c09-880bba4b5314",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}

CSV:
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
                "value": "Customers"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://firebasestorage.googleapis.com/v0/b/nano-knights-9b750.appspot.com/o/customers-100.csv?alt=media&token=eb8cda0a-e829-4e9b-8dbb-5afe9461faa3",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}

TXT:
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
                "value": "Agile Development"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://firebasestorage.googleapis.com/v0/b/nano-knights-9b750.appspot.com/o/Agile%20development.txt?alt=media&token=1057e62a-6f5d-4cd3-943d-d36aa142558a",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}

YouTube:
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
                "value": "Docker"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://youtu.be/RqTEHSBrYFw?si=CRFjjQw7HUmSJFCQ",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}

Webpage:
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
                "value": "Data parallelism"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "filePath": "",
                        "url": "https://en.wikipedia.org/wiki/Data_parallelism",
                        "filename": ""
                    }
                ]
            }
        ]
    }
}