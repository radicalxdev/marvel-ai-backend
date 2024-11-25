# How to test the features:

## Table of Contents

1. [**AVAILABLE DOCUMENT LOADERS FOR DIFFERENT FILE TYPES**](#available-document-loaders-for-different-file-types)

2. [**PAYLOADS FOR TESTING**](#payloads-for-testing)
   - [**Epic 7.1 - Multiple Choice Quiz Generator**](#epic-71---multiple-choice-quiz-generator)
     - [PDF](#pdf-1)
     - [Structured Data (EXCEL)](#structured-data-excel)
     - [Youtube Videos](#youtube-videos)
     - [Google Drive (GDocs)](#google-drive-gdocs)
     - [Google Drive (GPDF)](#google-drive-gpdf)
     - [Images](#images-1)
   - [**Epic 7.2 - Flashcards Generator**](#epic-72---flashcards-generator)
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

## Epic 7.1 - Multiple Choice Quiz Generator:
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

## Epic 7.2 - Flashcards Generator:
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
                "name": "subject",
                "value": "Linear Regression"
            },
            {
                "name": "course_description",
                "value": "This course introduces Linear Regression concepts, focusing on mathematical foundations and practical applications."
            },
            {
                "name": "objectives",
                "value": "Understand regression theory, perform analysis on datasets, and interpret statistical results."
            },
            {
                "name": "required_materials",
                "value": "Laptop, statistical software (e.g., R, Python), and course textbook."
            },
            {
                "name": "grading_policy",
                "value": "Projects contribute 40%, exams contribute 60%."
            },
            {
                "name": "policies_expectations",
                "value": "Students must submit assignments on time and actively participate in discussions."
            },
            {
                "name": "course_outline",
                "value": "Week 1: Introduction to Linear Regression\nWeek 2: Least Squares Method\nWeek 3: Hypothesis Testing\nWeek 4: Multivariate Regression\nWeek 5: Diagnostics and Residual Analysis\nWeek 6: Regularization Techniques\nWeek 7: Model Validation\nWeek 8: Capstone Project."
            },
            {
                "name": "additional_notes",
                "value": "This course is intensive and requires prior knowledge of basic statistics."
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
                "name": "subject",
                "value": "Software Engineering"
            },
            {
                "name": "course_description",
                "value": "This course covers the principles and practices of software engineering, including requirements analysis, system design, development, testing, and maintenance."
            },
            {
                "name": "objectives",
                "value": "Understand software development life cycles, design scalable systems, and apply testing methodologies to ensure quality software."
            },
            {
                "name": "required_materials",
                "value": "Computer with IDE installed, course textbook on software engineering, and internet access for research."
            },
            {
                "name": "grading_policy",
                "value": "Projects contribute 50%, exams contribute 40%, and participation contributes 10%."
            },
            {
                "name": "policies_expectations",
                "value": "Active participation is required. Assignments must be submitted on time. Collaboration is encouraged, but plagiarism is strictly prohibited."
            },
            {
                "name": "course_outline",
                "value": "Week 1: Introduction to Software Engineering\nWeek 2: Requirements Engineering\nWeek 3: System Design and Architecture\nWeek 4: Implementation and Coding Standards\nWeek 5: Testing and Debugging Techniques\nWeek 6: Agile and DevOps Practices\nWeek 7: Software Maintenance\nWeek 8: Capstone Project."
            },
            {
                "name": "additional_notes",
                "value": "This course requires prior knowledge of basic programming concepts."
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
                "name": "subject",
                "value": "Machine Learning"
            },
            {
                "name": "course_description",
                "value": "This course introduces the fundamental concepts and techniques of machine learning, including supervised and unsupervised learning, model evaluation, and practical applications using modern tools."
            },
            {
                "name": "objectives",
                "value": "Understand the theoretical foundations of machine learning algorithms, apply them to real-world datasets, and evaluate model performance effectively."
            },
            {
                "name": "required_materials",
                "value": "Computer with Python installed, Jupyter Notebook, and a stable internet connection for accessing datasets and libraries."
            },
            {
                "name": "grading_policy",
                "value": "Projects contribute 50%, exams contribute 40%, and participation contributes 10%."
            },
            {
                "name": "policies_expectations",
                "value": "Students are expected to complete weekly assignments, participate in discussions, and adhere to academic honesty policies."
            },
            {
                "name": "course_outline",
                "value": "Week 1: Introduction to Machine Learning\nWeek 2: Linear Regression and Classification\nWeek 3: Decision Trees and Random Forests\nWeek 4: Support Vector Machines\nWeek 5: Neural Networks\nWeek 6: Unsupervised Learning and Clustering\nWeek 7: Model Evaluation and Optimization\nWeek 8: Capstone Project."
            },
            {
                "name": "additional_notes",
                "value": "Familiarity with basic statistics and programming is recommended."
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
                "name": "subject",
                "value": "LLMs"
            },
            {
                "name": "course_description",
                "value": "This course delves into the foundations, architectures, and applications of Large Language Models (LLMs). Students will explore key topics including transformer models, pretraining techniques, fine-tuning strategies, and practical use cases in natural language processing (NLP)."
            },
            {
                "name": "objectives",
                "value": "Understand the theory and architecture of LLMs, implement fine-tuning for specific tasks, and critically evaluate their performance and limitations."
            },
            {
                "name": "required_materials",
                "value": "Laptop with Python installed, access to popular libraries like TensorFlow or PyTorch, and a stable internet connection for experimenting with APIs like OpenAI or Hugging Face."
            },
            {
                "name": "grading_policy",
                "value": "Projects contribute 50%, exams contribute 40%, and participation contributes 10%."
            },
            {
                "name": "policies_expectations",
                "value": "Students must actively engage in discussions, complete weekly assignments, and ensure academic honesty throughout the course."
            },
            {
                "name": "course_outline",
                "value": "Week 1: Introduction to LLMs and Transformers\nWeek 2: Pretraining and Fine-Tuning\nWeek 3: Applications of LLMs in NLP\nWeek 4: Ethical Implications and Bias in LLMs\nWeek 5: Advanced Architectures (e.g., GPT, BERT)\nWeek 6: Scaling LLMs and Distributed Computing\nWeek 7: Evaluation Metrics for LLMs\nWeek 8: Capstone Project: Building and Deploying an LLM."
            },
            {
                "name": "additional_notes",
                "value": "Familiarity with basic machine learning concepts and programming is recommended."
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
                "name": "subject",
                "value": "AWS Architectures"
            },
            {
                "name": "course_description",
                "value": "This course provides an in-depth understanding of AWS architectures and best practices for designing scalable, secure, and cost-effective solutions on the Amazon Web Services (AWS) cloud platform. Students will explore topics like compute, storage, databases, and networking within AWS."
            },
            {
                "name": "objectives",
                "value": "Learn to design scalable and resilient AWS architectures, implement best practices for security and cost management, and deploy AWS solutions for real-world applications."
            },
            {
                "name": "required_materials",
                "value": "Laptop with internet access, AWS free-tier account, and course-provided materials."
            },
            {
                "name": "grading_policy",
                "value": "Projects contribute 60%, exams contribute 30%, and participation contributes 10%."
            },
            {
                "name": "policies_expectations",
                "value": "Students must complete weekly labs and assignments, actively participate in discussions, and comply with AWS cloud usage policies."
            },
            {
                "name": "course_outline",
                "value": "Week 1: Introduction to AWS Cloud Computing\nWeek 2: Compute Services and EC2\nWeek 3: Storage Solutions (S3, EBS, Glacier)\nWeek 4: Networking and Content Delivery\nWeek 5: Databases and AWS RDS\nWeek 6: Security Best Practices\nWeek 7: Monitoring and Optimization\nWeek 8: Capstone Project: Building a Scalable AWS Architecture."
            },
            {
                "name": "additional_notes",
                "value": "Prior knowledge of basic cloud computing concepts is recommended."
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