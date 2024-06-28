### How to Run

To make a request a `url` of the file is needed. To identify specific items in the documents, the user can either specify a list using `specific_list`, or the user can identify a range by using `section_start` and `section_end`. The following examples will help to guide the usage of the new quizzify features.

The specification is further illustrated in the following table:

| Type | `specific_list` | `section_start` + `section_end`| Description|
| --- | --- | --- | --- |
| <center> YouTube </center> | <center> ✓ </center>| <center> ✗ </center> | <center> Timestamps </center> |
| <center> WebPage </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Pages </center> |
| <center> DOC </center> | <center> ✗ </center>| <center> ✗ </center> | <center> N/A </center> |
| <center> DOCX </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Pages </center> |
| <center> PPT </center> | <center> ✗ </center>| <center> ✗ </center> | <center> N/A </center> |
| <center> PPTX </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Slides </center> |
| <center> PDF </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Pages </center> |
| <center> CSV </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Rows & Columns </center> |
| <center> XLSX </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Rows & Columns </center> |
| <center> TXT </center> | <center> ✓ </center>| <center> ✓ </center> | <center> Pages </center> |

### Json Request Examples

#### Web Page
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://www.britannica.com/science/linear-algebra",
                        "file_type":"web_url",
                        "section_start":1,
                        "section_end":10
                    }
                ]
            }
        ]
    }
}
```

#### YouTube
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://www.youtube.com/watch?v=QKA4HNEw3aY",
                        "file_type":"youtube",
                        "section_start":1,
                        "section_end":20
                    }
                ]
            }
        ]
    }
}
```

#### CSV
```
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
                "value": "Math"
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
						"url": "https://firebasestorage.googleapis.com/v0/b/docxfile-1ed2d.appspot.com/o/tesla_stock_data.csv?alt=media&token=244ff9df-9779-468c-9da0-4cc17941afa5",  
						"filename": "certificate.csv",
                        "file_type": "csv",
                        "section_start": [1,1],
                        "section_end": [4,3]
                    }
                ]
            }
        ]
    }
}
```

#### Excel
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://www.cns.nyu.edu/~david/courses/compNeuro/linear-systems-tutorial.xlsx",
                        "file_type": "xlsx",
                        "section_start": [1,1],
                        "section_end": [4,3]
                    }
                ]
            }
        ]
    }
}
```

#### Text
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://github.com/jasongrout/linear-algebra/blob/master/linear-algebra-book-changes.txt",
                        "file_type":"txt",
                        "specific_list": [1,3,5,6,9]
                    }
                ]
            }
        ]
    }
}
```

#### PDF
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://web.stanford.edu/~boyd/vmls/vmls-slides.pdf",
                        "file_type": "pdf",
                        "specific_list": [3,2,5,7,8]
                    }
                ]
            }
        ]
    }
}
```

#### DOCX
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://www.hse.ru/data/2014/06/19/1309928966/Linear%20Algebra%20Year%202%20ENG.docx",
                        "file_type": "docx",
                        "section_start":1,
                        "section_end":15
                    }
                ]
            }
        ]
    }
}
```

#### DOC
###### Note that specific pages is not implemented for DOC since it's considered outdated by python-docx
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://www.engr.mun.ca/~ggeorge/2050/handout/C2a.doc",
                        "file_type": "doc"
                    }
                ]
            }
        ]
    }
}
```

#### PPT
###### Note that specific slides is not implemented for PPT since it's considered outdated by python-pptx
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://cbmm.mit.edu/sites/default/files/learning-hub/LinearAlgebra_2016updatedFromwiki.ppt",
                        "file_type": "ppt"
                    }
                ]
            }
        ]
    }
}
```

#### PPTX
```
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
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 1
            },
            {
                "name": "files",
                "value": [
                    {
                        "url": "https://personal.utdallas.edu/~nrr150130/cs7301/2021fa/lects/Lecture_9_LA_Review.pptx",
                        "file_type": "pptx",
                        "specific_list": [1,2,4,6,8,10]
                    }
                ]
            }
        ]
    }
}
```