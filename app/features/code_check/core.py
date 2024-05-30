from features.code_check.tools import get_feedback
# TODO: Implement the executor function's verbose param to downstream logic

def executor(solution: str, submission: str, verbose=False):
    feedback = get_feedback(solution, submission)
    
    return feedback



# from features.dynamo.tools import find_key_concepts, retrieve_youtube_documents

# # TODO: Implement the executor function's verbose param to downstream logic

# def executor(youtube_url: str, verbose=False):
#     yt_documents = retrieve_youtube_documents(youtube_url)
#     concepts = find_key_concepts(yt_documents)
    
#     return concepts