from tools import *
import streamlit as st

if __name__ == "__main__":
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "kaidev-431918",
        "location": "us-central1"
    }

    if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
        st.session_state['question_bank'] = []
        st.session_state['display_quiz'] = False
        st.session_state['question_index'] = 0

        screen = st.empty()
        with screen.container():
            st.header("Quiz Builder")

            with st.form("Load Data to Chroma"):
                st.write("Select files for Ingestion, the topic for the quiz, and click Generate!")

                processor = DocumentProcessor()
                processor.ingest_documents()

                embed_client = EmbeddingClient(**embed_config)

                chroma_creator = ChromaCollectionCreator(processor, embed_client)

                topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)

                submitted = st.form_submit_button("Submit")

                if submitted:
                    chroma_creator.create_chroma_collection()

                    if len(processor.pages) > 0:
                        st.write(f"Generating {questions} questions for topic: {topic_input}")
                    
                    # Wait for the Chroma collection to be created before passing it to QuizGenerator
                    while chroma_creator.db is None:
                        st.write("Waiting for Chroma collection to be created...")
                    
                    generator = QuizGenerator(topic_input, questions, chroma_creator.db)
                    question_bank = generator.generate_quiz()
                    st.session_state['question_bank'] = question_bank
                    st.session_state['display_quiz'] = True
                    st.session_state['question_index'] = 0

    if st.session_state["display_quiz"]:
        with st.container():
            st.header("Generated Quiz Question: ")
            quiz_manager = QuizManager(st.session_state['question_bank'])

            with st.form("MCQ"):
                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])

                choices = []
                for choice in index_question['choices']:
                    key = choice['key']
                    value = choice['value']
                    choices.append(f"{key}) {value}")

                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio("Choose an answer", choices, index=None)
                answer_choice = st.form_submit_button("Submit")

                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
                    st.write(f"Explanation: {index_question['explanation']}")

            col1, col2 = st.columns(2)
            if not quiz_manager.is_first_question():
                with col1:
                    if st.button("Previous Question"):
                        quiz_manager.next_question_index(direction=-1)
                        st.experimental_rerun()

            if not quiz_manager.is_last_question():
                with col2:
                    if st.button("Next Question"):
                        quiz_manager.next_question_index(direction=1)
                        st.experimental_rerun()
            else:
                st.write("End of Quiz! Upload a new file to generate a new quiz.")
                if st.button("Start Over"):
                    st.session_state["question_bank"] = []
                    st.session_state["display_quiz"] = False
                    st.session_state["question_index"] = 0
                    st.experimental_rerun()

