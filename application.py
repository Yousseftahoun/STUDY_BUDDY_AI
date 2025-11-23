import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()


def main():
    st.set_page_config(page_title="Study buddy AI",page_icon="📚")

    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False

    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    st.title("📚 Study Buddy AI")


    st.sidebar.header("Quiz Settings")

    question_type = st.sidebar.selectbox(
        "Select Question Type",
        ["Multiple Choice", "Fill in the Blanks"],
        index=0
    )

    topic = st.sidebar.text_input("Enter Topic", placeholder="General Knowledge")

    difficulty = st.sidebar.selectbox(
        "Select Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    num_questions = st.sidebar.number_input(
        "Number of Questions",
        min_value=1,
        max_value=10,
        value=5,
    )


    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False

        generator = QuestionGenerator()
        succes = st.session_state.quiz_manager.generate_questions(
            generator,
            topic,
            question_type,
            difficulty,
            num_questions
        )
        st.session_state.quiz_generated = succes
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("Quiz Time!")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Answers"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()

    if st.session_state.quiz_submitted:
        st.header("Quiz Results")
        results_df = st.session_state.quiz_manager.get_results_dataframe()

        if not results_df.empty:

            correct_count = results_df['is_correct'].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100

            st.write(f"### You scored {correct_count} out of {total_questions}, Score: {score_percentage} ###")

            for _, result in results_df.iterrows():
                question_number = result['question_number']
                if result['is_correct']:
                    st.success(f"Question {question_number}: {result['question']} - Correct")
                else:
                    st.error(f"Question {question_number}: {result['question']} - Incorrect. Correct Answer: {result['correct_answer']}")
                    st.write(f"Your Answer: {result['user_answer']}")
                
                st.markdown("-----")
        
        if st.button("Save results"):
            saved_file = st.session_state.quiz_manager.save_to_csv()
            if saved_file:
                with open(saved_file, "rb") as f:
                    st.download_button(
                        label="Download Results as CSV",
                        data=f.read(),
                        file_name=os.path.basename(saved_file),
                        mime="text/csv"
                    )
            else:
                st.warning("No results to save.")

if __name__ == "__main__":
    main()
            

