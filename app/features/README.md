# How to test the features:

## Table of Contents

1. [**AVAILABLE DOCUMENT LOADERS FOR DIFFERENT FILE TYPES**](#available-document-loaders-for-different-file-types)

2. [**PAYLOADS FOR TESTING**](#payloads-for-testing)
   - [**Epic 7.1 - Quizzify**](#epic-71---quizzify)
     - [PDF](#pdf-1)
     - [Structured Data (EXCEL)](#structured-data-excel)
     - [Youtube Videos](#youtube-videos)
     - [Google Drive (GDocs)](#google-drive-gdocs)
     - [Google Drive (GPDF)](#google-drive-gpdf)
     - [Images](#images-1)
   - [**Epic 7.2 - Dynamo**](#epic-72---dynamo)
     - [PDF](#pdf-2)
     - [Structured Data (XML)](#structured-data-xml)
     - [Youtube Videos](#youtube-videos-1)
     - [Google Drive (GDocs)](#google-drive-gdocs-1)
     - [Images](#images-2)
   - [**Epic 7.3 - Worksheet Generator**](#epic-73---worksheet-generator)
     - [PDF](#pdf-3)
     - [Structured Data (XML)](#structured-data-xml-1)
     - [Youtube Videos](#youtube-videos-2)
     - [Google Drive (GDocs)](#google-drive-gdocs-2)
     - [Images](#images-3)
   - [**Epic 7.7 - Syllabus Generator**](#epic-77---syllabus-generator)
     - [PDF](#pdf-4)
     - [Structured Data (XML)](#structured-data-xml-2)
     - [Youtube Videos](#youtube-videos-3)
     - [Google Drive (GDocs)](#google-drive-gdocs-3)
     - [Images](#images-4)


## AVAILABLE DOCUMENT LOADERS FOR DIFFERENT FILE TYPES:
| File Type | Description | Function |
|-----------|-------------|----------|
| PDF       | Portable Document Format | `load_pdf_documents` |
| CSV       | Comma-Separated Values | `load_csv_documents` |
| TXT       | Plain Text | `load_txt_documents` |
| MD        | Markdown | `load_md_documents` |
| URL       | Web URL | `load_url_documents` |
| Youtube URL       | Youtube URL | `summarize_transcript_youtube_url` |
| PPTX      | PowerPoint Presentation | `load_pptx_documents` |
| DOCX      | Word Document | `load_docx_documents` |
| XLS       | Excel Spreadsheet | `load_xls_documents` |
| XLSX      | Excel Spreadsheet | `load_xlsx_documents` |
| XML       | XML Document | `load_xml_documents` |
| Google Docs | Documents from Google Drive | `load_gdocs_documents` |
| Google Sheets | Spreadsheets from Google Drive | `load_gsheets_documents` |
| Google Slides | Presentations from Google Drive | `load_gslides_documents` |
| Google PDFs | PDFs from Google Drive | `load_gpdf_documents` |
| Images | PNG, JPG, JPEG | `generate_concepts_from_img` |

## PAYLOADS FOR TESTING:

## Epic 7.1 - Quizzify:
### PDF:
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
            "value": "Linear Algebra"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
         },
         {
            "name": "file_type",
            "value": "pdf"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```


### Structured Data (EXCEL):
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
            "value": "Countries"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://github.com/AaronSosaRamos/mission-flights/raw/main/files-for-test/Free_Test_Data_1MB_XLSX.xlsx"
         },
         {
            "name": "file_type",
            "value": "xlsx"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Youtube Videos:
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
            "value": "Machine Learning"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
         },
         {
            "name": "file_type",
            "value": "youtube_url"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Google Drive (GDocs):
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
            "value": "OpenAI"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
         },
         {
            "name": "file_type",
            "value": "gdoc"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Google Drive (GPDF):
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
            "value": "OpenAI"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://drive.google.com/file/d/1JIZxgX4aLUUl5bHy5SE8OK7Eg9tT1ZkA/view?usp=drive_link"
         },
         {
            "name": "file_type",
            "value": "gpdf"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Images:
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
            "value": "AWS Architecture"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://miro.medium.com/v2/resize:fit:1200/1*DGp9FSicaRJOs8IWFPxKag.png"
         },
         {
            "name": "file_type",
            "value": "img"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

## Epic 7.2 - Dynamo:
### PDF:
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
      },
      {
        "name": "file_type",
        "value": "pdf"
      }
    ]
  }
}
```

### Structured Data (XML):
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
      },
      {
        "name": "file_type",
        "value": "xml"
      }
    ]
  }
}
```

### Youtube Videos:
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
      },
      {
        "name": "file_type",
        "value": "youtube_url"
      }
    ]
  }
}
```

### Google Drive (GDocs):
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
      },
      {
        "name": "file_type",
        "value": "gdoc"
      }
    ]
  }
}
```

### Images:
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://docs.aws.amazon.com/images/solutions/latest/workload-discovery-on-aws/images/workload-discovery-arch-diagram.png"
      },
      {
        "name": "file_type",
        "value": "img"
      }
    ]
  }
}
```

## Epic 7.3 - Worksheet Generator:
### PDF:
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 2,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "topic",
            "value": "Machine Learning"
         },
         {
            "name": "file_url",
            "value": "https://www.interactions.com/wp-content/uploads/2017/06/machine_learning_wp-5.pdf"
         },
         {
            "name": "file_type",
            "value": "pdf"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Structured Data (XML):
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 2,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "topic",
            "value": "Books"
         },
         {
            "name": "file_url",
            "value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
         },
         {
            "name": "file_type",
            "value": "xml"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Youtube Videos:
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 2,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "topic",
            "value": "Machine Learning"
         },
         {
            "name": "file_url",
            "value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
         },
         {
            "name": "file_type",
            "value": "youtube_url"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Google Drive (GDocs):
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 2,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "topic",
            "value": "OpenAI"
         },
         {
            "name": "file_url",
            "value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
         },
         {
            "name": "file_type",
            "value": "gdoc"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Images:
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 2,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "topic",
            "value": "AWS Architecture"
         },
         {
            "name": "file_url",
            "value": "https://docs.aws.amazon.com/images/solutions/latest/workload-discovery-on-aws/images/workload-discovery-arch-diagram.png"
         },
         {
            "name": "file_type",
            "value": "img"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

## Epic 7.7 - Syllabus Generator:
### PDF:
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 6,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "course",
            "value": "Linear Regression"
         },
         {
            "name": "instructor_name",
            "value": "Wilfredo Sosa"
         },
         {
            "name": "instructor_title",
            "value": "Master in Artificial Intelligence"
         },
         {
            "name": "unit_time",
            "value": "week"
         },
         {
            "name": "unit_time_value",
            "value": 8
         },
         {
            "name": "start_date",
            "value": "July, 4th, 2024"
         },
         {
            "name": "assessment_methods",
            "value": "project and exams"
         },
         {
            "name": "grading_scale",
            "value": "In percentages (100%)"
         },
         {
            "name": "file_url",
            "value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
         },
         {
            "name": "file_type",
            "value": "pdf"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Structured Data (XML):
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 6,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "course",
            "value": "Software Engineering"
         },
         {
            "name": "instructor_name",
            "value": "Wilfredo Sosa"
         },
         {
            "name": "instructor_title",
            "value": "Master in Artificial Intelligence"
         },
         {
            "name": "unit_time",
            "value": "week"
         },
         {
            "name": "unit_time_value",
            "value": 8
         },
         {
            "name": "start_date",
            "value": "July, 4th, 2024"
         },
         {
            "name": "assessment_methods",
            "value": "project and exams"
         },
         {
            "name": "grading_scale",
            "value": "In percentages (100%)"
         },
         {
            "name": "file_url",
            "value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
         },
         {
            "name": "file_type",
            "value": "xml"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Youtube Videos:
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 6,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "course",
            "value": "Machine Learning"
         },
         {
            "name": "instructor_name",
            "value": "Wilfredo Sosa"
         },
         {
            "name": "instructor_title",
            "value": "Master in Artificial Intelligence"
         },
         {
            "name": "unit_time",
            "value": "week"
         },
         {
            "name": "unit_time_value",
            "value": 8
         },
         {
            "name": "start_date",
            "value": "July, 4th, 2024"
         },
         {
            "name": "assessment_methods",
            "value": "project and exams"
         },
         {
            "name": "grading_scale",
            "value": "In percentages (100%)"
         },
         {
            "name": "file_url",
            "value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
         },
         {
            "name": "file_type",
            "value": "youtube_url"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Google Drive (GDocs):
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 6,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "course",
            "value": "LLMs"
         },
         {
            "name": "instructor_name",
            "value": "Wilfredo Sosa"
         },
         {
            "name": "instructor_title",
            "value": "Master in Artificial Intelligence"
         },
         {
            "name": "unit_time",
            "value": "week"
         },
         {
            "name": "unit_time_value",
            "value": 8
         },
         {
            "name": "start_date",
            "value": "July, 4th, 2024"
         },
         {
            "name": "assessment_methods",
            "value": "project and exams"
         },
         {
            "name": "grading_scale",
            "value": "In percentages (100%)"
         },
         {
            "name": "file_url",
            "value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
         },
         {
            "name": "file_type",
            "value": "gdoc"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```

### Images:
```json
{
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "chat",
   "tool_data": {
      "tool_id": 6,
      "inputs": [
         {
            "name": "grade_level",
            "value": "College"
         },
         {
            "name": "course",
            "value": "AWS Architectures"
         },
         {
            "name": "instructor_name",
            "value": "Wilfredo Sosa"
         },
         {
            "name": "instructor_title",
            "value": "Master in Artificial Intelligence"
         },
         {
            "name": "unit_time",
            "value": "week"
         },
         {
            "name": "unit_time_value",
            "value": 8
         },
         {
            "name": "start_date",
            "value": "July, 4th, 2024"
         },
         {
            "name": "assessment_methods",
            "value": "project and exams"
         },
         {
            "name": "grading_scale",
            "value": "In percentages (100%)"
         },
         {
            "name": "file_url",
            "value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2023/02/13/adverse_1-1024x546.png"
         },
         {
            "name": "file_type",
            "value": "img"
         },
         {
            "name": "lang",
            "value": "en"
         }
      ]
   }
}
```