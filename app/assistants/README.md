# Assistants Framework Overview

This repository hosts the implementation of a modular architecture for a variety of educational assistants designed to enhance teaching and learning experiences. The assistants are categorized into three main groups:

| **Curriculum Tools** | **Classroom Support** | **Communication & Tech Integration** |
|-----------------------|-----------------------|--------------------------------------|
| Coming Soon          | **CoTeacher**         | Coming Soon                          |

## Implemented Assistants

### CoTeacher
CoTeacher belongs to the **Classroom Support** category and is designed to assist educators with tasks like translation, summarization, rewriting, question generation, and custom prompt-based interactions. The assistant supports multilingual capabilities and personalization based on user preferences.

## Features and Payloads
Below are the JSON payloads for the implemented actions of CoTeacher.

### CoTeacher - Translate
**Request:**
```json
{
   "assistant_inputs": {
      "assistant_group": "classroom_support",
      "assistant_name": "co_teacher",
      "inputs": [
         {
            "name": "action",
            "value": "translate"
         },
         {
            "name": "messages",
            "value": [
               {
                  "role": "human",
                  "type": "text",
                  "timestamp": "string",
                  "payload": {
                     "text": "Please, translate 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on vast amounts of text data to understand and generate human-like language. These models leverage deep learning techniques, particularly transformer architectures, to process and generate text across a wide range of contexts and tasks. LLMs are capable of performing diverse functions, including language translation, summarization, content creation, and even complex problem-solving. Their capabilities continue to expand as they are fine-tune for specific applications, making them invaluable tools in industries such as healthcare, education, customer support, and software development.' from English to Spanish."
                  }
               }
            ]
         }
      ]
   }
}
```

**Response:**
```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": "Los modelos lingüísticos grandes (LLM) son sistemas avanzados de inteligencia artificial entrenados con grandes cantidades de datos de texto para comprender y generar lenguaje similar al humano. Estos modelos aprovechan técnicas de aprendizaje profundo, particularmente arquitecturas de transformadores, para procesar y generar texto en una amplia gama de contextos y tareas. Los LLM son capaces de realizar diversas funciones, incluyendo traducción de idiomas, resumen, creación de contenido e incluso resolución de problemas complejos. Sus capacidades continúan expandiéndose a medida que se ajustan finamente para aplicaciones específicas, lo que los convierte en herramientas invaluables en industrias como la salud, la educación, la atención al cliente y el desarrollo de software."
      }
    }
  ]
}
```

### CoTeacher - Summarize
**Request:**
```json
{
   "assistant_inputs": {
      "assistant_group": "classroom_support",
      "assistant_name": "co_teacher",
      "inputs": [
         {
            "name": "action",
            "value": "summarize"
         },
         {
            "name": "messages",
            "value": [
               {
                  "role": "human",
                  "type": "text",
                  "timestamp": "string",
                  "payload": {
                     "text": "Please, summarize 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on vast amounts of text data to understand and generate human-like language. These models leverage deep learning techniques, particularly transformer architectures, to process and generate text across a wide range of contexts and tasks. LLMs are capable of performing diverse functions, including language translation, summarization, content creation, and even complex problem-solving. Their capabilities continue to expand as they are fine-tune for specific applications, making them invaluable tools in industries such as healthcare, education, customer support, and software development.'"
                  }
               }
            ]
         }
      ]
   }
}
```

**Response:**
```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": "LLMs are advanced AI systems trained on massive text datasets to understand and generate human-like text using deep learning (transformer architectures). They perform diverse functions (translation, summarization, content creation, problem-solving) and are valuable tools across many industries."
      }
    }
  ]
}
```

### CoTeacher - Rewrite
**Request:**
```json
{
   "assistant_inputs": {
      "assistant_group": "classroom_support",
      "assistant_name": "co_teacher",
      "inputs": [
         {
            "name": "action",
            "value": "rewrite"
         },
         {
            "name": "messages",
            "value": [
               {
                  "role": "human",
                  "type": "text",
                  "timestamp": "string",
                  "payload": {
                     "text": "Please, rewrite so like llms are these things that do like ai stuff and they like talk and write but not really like people but kinda, and they like use data or something, idk, like lots of data, and then they like learn, but not really learn like humans, just like, you know, math or whatever, and then they make stuff like words and answers, and ppl say they’re smart but they’re just like programs, and yeah, they’re everywhere now and ppl use them for like, idk, work or chatting or whatever."
                  }
               }
            ]
         }
      ]
   }
}
```

**Response:**
```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": "Large language models (LLMs) are AI systems that process and generate human-like text. They aren't sentient, but they mimic human communication by using vast amounts of data to identify patterns and relationships. This allows them to \"learn\" in a statistical sense, not through conscious understanding like humans. They then use this learned information to create text, translate languages, and answer questions. While their capabilities are impressive, they remain sophisticated programs, not truly intelligent beings. LLMs are increasingly prevalent, assisting with various tasks from professional work to casual conversations."
      }
    }
  ]
}
```

### CoTeacher - Question Generation
**Request:**
```json
{
   "assistant_inputs": {
      "assistant_group": "classroom_support",
      "assistant_name": "co_teacher",
      "inputs": [
         {
            "name": "action",
            "value": "question_generation"
         },
         {
            "name": "messages",
            "value": [
               {
                  "role": "human",
                  "type": "text",
                  "timestamp": "string",
                  "payload": {
                     "text": "Please, create questions for Linear Algebra."
                  }
               }
            ]
         }
      ]
   }
}
```

**Response:**
```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": {
          "multiple_choice_questions": [
            {
              "question": "Which of the following is NOT a property of vector addition?",
              "choices": [
                {
                  "key": "A",
                  "value": "Commutative Property: u + v = v + u"
                },
                {
                  "key": "B",
                  "value": "Associative Property: (u + v) + w = u + (v + w)"
                },
                {
                  "key": "C",
                  "value": "Distributive Property: c(u + v) = cu + cv"
                },
                {
                  "key": "D",
                  "value": "Identity Property: u + 0 = u"
                },
                {
                  "key": "E",
                  "value": "Inverse Property: u + (-u) = 0"
                }
              ],
              "answer": "C",
              "explanation": "The distributive property applies to scalar multiplication, not vector addition. The distributive property of scalar multiplication over vector addition is c(u + v) = cu + cv."
            }
          ]
        }
      }
    }
  ]
}
```

### CoTeacher - Custom Prompt
**Request:**
```json
{
   "assistant_inputs": {
      "assistant_group": "classroom_support",
      "assistant_name": "co_teacher",
      "inputs": [
         {
            "name": "action",
            "value": "custom"
         },
         {
            "name": "messages",
            "value": [
               {
                  "role": "human",
                  "type": "text",
                  "timestamp": "string",
                  "payload": {
                     "text": "Save this prompt: 'Please, create questions for Linear Algebra.'"
                  }
               }
            ]
         }
      ]
   }
}
```

**Response:**
```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": "Okay, I've saved the prompt."
      }
    }
  ]
}
```

### CoTeacher - Default
**Request:**
```json
{
   "assistant_inputs": {
      "assistant_group": "classroom_support",
      "assistant_name": "co_teacher",
      "inputs": [
         {
            "name": "action",
            "value": "default"
         },
         {
            "name": "messages",
            "value": [
               {
                  "role": "human",
                  "type": "text",
                  "timestamp": "string",
                  "payload": {
                     "text": "Generate tips for differentiated instruction."
                  }
               }
            ]
         }
      ]
   }
}
```

**Response:**
```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": "Here are some tips for differentiated instruction..."
      }
    }
  ]
}
```