import pytest

from app.assistants.classroom_support.co_teacher.core import executor

def test_executor_translate_valid():
    result = executor(
        action="translate",
        messages=[
            {
                "role":"human",
                "type":"text",
                "timestamp":"string",
                "payload":{
                    "text":"""Please, translate 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on vast amounts 
                    of text data to understand and generate human-like language. These models leverage deep learning techniques, particularly transformer 
                    architectures, to process and generate text across a wide range of contexts and tasks. LLMs are capable of performing diverse functions, 
                    including language translation, summarization, content creation, and even complex problem-solving. Their capabilities continue to expand as 
                    they are fine-tune for specific applications, making them invaluable tools in industries such as healthcare, education, customer support, 
                    and software development.' from English to Spanish."""
                }
            }
        ]
    )
    assert isinstance(result, str)

def test_executor_translate_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            action="translate123",
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                        "text":"""Please, translate 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on vast amounts 
                        of text data to understand and generate human-like language. These models leverage deep learning techniques, particularly transformer 
                        architectures, to process and generate text across a wide range of contexts and tasks. LLMs are capable of performing diverse functions, 
                        including language translation, summarization, content creation, and even complex problem-solving. Their capabilities continue to expand as 
                        they are fine-tune for specific applications, making them invaluable tools in industries such as healthcare, education, customer support, 
                        and software development.' from English to Spanish."""
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, ValueError)

def test_executor_summarize_valid():
    result = executor(
        action="summarize",
        messages=[
            {
                "role":"human",
                "type":"text",
                "timestamp":"string",
                "payload":{
                    "text":"""Please, summarize 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on vast amounts 
                    of text data to understand and generate human-like language. These models leverage deep learning techniques, particularly transformer 
                    architectures, to process and generate text across a wide range of contexts and tasks. LLMs are capable of performing diverse functions, 
                    including language translation, summarization, content creation, and even complex problem-solving. Their capabilities continue to expand 
                    as they are fine-tune for specific applications, making them invaluable tools in industries such as healthcare, education, customer 
                    support, and software development."""
                }
            }
        ]
    )
    assert isinstance(result, str)

def test_executor_summarize_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            action="summarize123",
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                        "text":"""Please, summarize 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on vast amounts 
                        of text data to understand and generate human-like language. These models leverage deep learning techniques, particularly transformer 
                        architectures, to process and generate text across a wide range of contexts and tasks. LLMs are capable of performing diverse functions, 
                        including language translation, summarization, content creation, and even complex problem-solving. Their capabilities continue to expand 
                        as they are fine-tune for specific applications, making them invaluable tools in industries such as healthcare, education, customer 
                        support, and software development."""
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, ValueError)

def test_executor_rewrite_valid():
    result = executor(
        action="rewrite",
        messages=[
            {
                "role":"human",
                "type":"text",
                "timestamp":"string",
                "payload":{
                    "text":"""Please, rewrite so like llms are these things that do like ai stuff and they like talk and write but not really like people 
                    but kinda, and they like use data or something, idk, like lots of data, and then they like learn, but not really learn like humans, 
                    just like, you know, math or whatever, and then they make stuff like words and answers, and ppl say they’re smart but they’re just 
                    like programs, and yeah, they’re everywhere now and ppl use them for like, idk, work or chatting or whatever"""
                }
            }
        ]
    )
    assert isinstance(result, str)

def test_executor_rewrite_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            action="rewrite123",
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                        "text":"""Please, rewrite so like llms are these things that do like ai stuff and they like talk and write but not really like people 
                        but kinda, and they like use data or something, idk, like lots of data, and then they like learn, but not really learn like humans, 
                        just like, you know, math or whatever, and then they make stuff like words and answers, and ppl say they’re smart but they’re just 
                        like programs, and yeah, they’re everywhere now and ppl use them for like, idk, work or chatting or whatever"""
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, ValueError)

def test_executor_question_generation_valid():
    result = executor(
        action="question_generation",
        messages=[
            {
                "role":"human",
                "type":"text",
                "timestamp":"string",
                "payload":{
                    "text":"Please, create questions for Linear Algebra"
                }
            }
        ]
    )
    assert isinstance(result, dict)

def test_executor_question_generation_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            action="question_generation123",
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                        "text":"Please, create questions for Linear Algebra"
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, ValueError)

def test_executor_custom_prompt_valid():
    result = executor(
        action="custom",
        messages=[
            {
                "role":"human",
                "type":"text",
                "timestamp":"string",
                "payload":{
                    "text":"Save this prompt: 'Please, create questions for Linear Algebra'"
                }
            }
        ]
    )
    assert isinstance(result, str)

def test_executor_custom_prompt_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            action="custom123",
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                        "text":"Save this prompt: 'Please, create questions for Linear Algebra'"
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, ValueError)
