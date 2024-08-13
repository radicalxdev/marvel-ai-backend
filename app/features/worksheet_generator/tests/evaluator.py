import re
from sentence_transformers import SentenceTransformer, util
import numpy as np
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# import nltk
from bert_score import score


class AnswerEvaluator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def preprocess_answer(self, answer):
        answer = answer.lower()
        answer = re.sub(r'[^\w\s]', '', answer)
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(answer)
        filtered_answer = ' '.join([word for word in word_tokens if word not in stop_words])
        return filtered_answer

    def exact_match(self, given_answer, ground_truth):
        return self.preprocess_answer(given_answer) == self.preprocess_answer(ground_truth)

    def get_sentence_embeddings(self, text):
        return self.model.encode(text, convert_to_tensor=True)

    def semantic_similarity(self, given_answer, ground_truth):
        given_answer_emb = self.get_sentence_embeddings(self.preprocess_answer(given_answer))
        ground_truth_emb = self.get_sentence_embeddings(self.preprocess_answer(ground_truth))
        similarity = util.pytorch_cos_sim(given_answer_emb, ground_truth_emb).item()
        return similarity

    def evaluate_answer(self, given_answer, ground_truth, threshold=0.7):
        # Exact match
        if self.exact_match(given_answer, ground_truth):
            return 1.0, "Exact Match"

        # Semantic similarity
        similarity = self.semantic_similarity(given_answer, ground_truth)
        if similarity >= threshold:
            return similarity, "Semantic Match"

        return similarity, "No Match"

    def calc_bert_score(self, generated_questions, context):
        P, R, F1 = score(generated_questions, [context] * len(generated_questions), lang='en', verbose=True)

        print("Precision:", P)
        print("Recall:", R)
        print("F1 Score:", F1)
        return P, R, F1


if __name__ == "__main__":
    # Download stopwords if not already downloaded
    # nltk.download('punkt')
    # nltk.download('stopwords')
    evaluator = AnswerEvaluator()
    context = "Paris is the capital city of France. Harper Lee wrote the novel 'To Kill a Mockingbird'."
    generated_questions = [
        "What is the capital city of France?",
        "Who is the author of 'To Kill a Mockingbird'?"
    ]

    P, R, F1 = evaluator.calc_bert_score(generated_questions, context)
    print(f"P: {P}, R: {R}, F1: {F1}")

