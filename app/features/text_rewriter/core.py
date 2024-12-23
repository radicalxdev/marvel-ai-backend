from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import GooglePalm 

def executor(text: str, instructions: str) -> dict:
    """
    Main function to process inputs and generate rewritten text.
    """
    # Initialize LangChain components
    llm = GooglePalm(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = PromptTemplate(
        input_variables=["text", "instructions"],
        template="Rewrite the following text based on these instructions: {instructions}\n\n{text}"
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    # Run the chain
    rewritten_text = chain.run(text=text, instructions=instructions)
    return {"original_text": text, "rewritten_text": rewritten_text}