## Overview

### Implemented Features

Implemented support for more file types for the quizzify feature. Feature now supports all of the following file types: "xlsx", "pdf", "pptx", "csv", "docx","jpeg",'jpg',"png", "ppt", "html", youtube links, and google drive links.

### Some sample json files for FastAPI testing

1. xlsx testing json
    ``` javascript
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
                    "value": "Benchmark Data for Wastewater Treatment"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://waterdams.nawihub.org/files/14/Benchmark%20data_v1.xlsx"
                        }
                    ]
                }
            ]
        }
    }
    ```

2. pdf testing json
    ``` javascript
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
                    "value": "Artificial Neural Network"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://www.ijser.org/researchpaper/A-Review-paper-on-Artificial-Neural-Network--A-Prediction-Technique.pdf"
                        }
                    ]
                }
            ]
        }
    }   
    ```

3. pptx testing json
    ``` javascript
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
                    "value": "Benchmark Data for Wastewater Treatment"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://waterdams.nawihub.org/files/14/Benchmark%20data%20slides_v1.pptx"
                        }
                    ]
                }
            ]
        }
    }
    ```

4. csv testing json
    ``` javascript
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
                    "value": "Relative Gas Change"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://pasteur.epa.gov/uploads/10.23719/1528686/documents/RelativeChangefromv1.1.1-2016to1.2-2019inSEFsbygas.csv"
                        }
                    ]
                }
            ]
        }
    }
    ```

5. docx testing json
    ``` javascript
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
                    "value": "Machine Learning"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://www.dovepress.com/get_supplementary_file.php?f=285742.docx"
                        }
                    ]
                }
            ]
        }
    }
    ```


6. html testing json
    ```javascript
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
                    "value": "Abstract Data Types"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://opendsa-server.cs.vt.edu/OpenDSA/Books/Everything/html/ADT.html"
                        }
                    ]
                }
            ]
        }
    }
    ```

7. google drive testing json
    ```javascript
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
                    "value": "Machine Learning"
                },
                {
                    "name": "num_questions",
                    "value": 3
                },
                {
                    "name": "files",
                    "value": [
                        {
                            "url": "https://docs.google.com/document/d/1xRHHgWWNsR08L_QP94XBA2HrihU4j1kB/edit?usp=sharing&ouid=116273819621699075725&rtpof=true&sd=true"
                        }
                    ]
                }
            ]
        }
    }
    ```