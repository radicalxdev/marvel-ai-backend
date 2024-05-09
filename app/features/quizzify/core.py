from fastapi import UploadFile
from typing import List


def executor(upload_files: List[UploadFile], topic: str):
    from features.quizzify.tools import UploadPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    ## Load and Split multiple PDF files into list of document chunks
    total_loaded_files = []
    
    for file in upload_files:
        reader = UploadPDFLoader(file)
        documents = reader.load()
        total_loaded_files.append(documents)
    
    print(f"Read {len(total_loaded_files)} documents")
    print(f"Type of single doc: {type(total_loaded_files[0][0])}")
    print(f"Length of loaded file: {len(total_loaded_files[0])}")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    
    total_chunks = []
    
    for file in total_loaded_files:
        chunks = text_splitter.split_documents(file)
        total_chunks.extend(chunks)
        print(f"Split into {len(chunks)} chunks")
    
    print(f"Total chunks: {len(total_chunks)}")
    
    ## Instantiate Chroma model (in-memory) from document chunks
    from langchain_chroma import Chroma
    from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough, RunnableParallel
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.pydantic_v1 import BaseModel, Field
    
    embedding = VertexAIEmbeddings(model="textembedding-gecko")
    
    db = Chroma.from_documents(total_chunks, embedding)
    
    template = """
            You are a subject matter expert on the topic: 
            {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object:
            {format_instructions}
            
            Context: 
            {context}
            """
    class QuestionChoice(BaseModel):
        key: str = Field(description="A unique identifier for the choice")
        value: str = Field(description="The text content of the choice")
    class QuizQuestion(BaseModel):
        question: str = Field(description="The question text")
        choices: List[QuestionChoice] = Field(description="A list of choices")
        answer: str = Field(description="The correct answer")
        explanation: str = Field(description="An explanation of why the answer is correct")
    
    parser = JsonOutputParser(pydantic_model=QuizQuestion)
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["topic"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    retriever = db.as_retriever()
    
    runner = RunnableParallel(
        {"context": retriever, "topic": RunnablePassthrough()}
    )
    
    model = VertexAI(model="gemini-1.0-pro")
    
    chain = runner | prompt | model | parser
    
    response = chain.invoke(topic)
    
    return {"message": "success", "data": response}
