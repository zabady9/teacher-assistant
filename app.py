import streamlit as st
import google.generativeai as genai
from functions import *
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

def main():
    st.title("Smart Teacher Assistant")
    st.write("Choose a tool to assist with your teaching tasks!")

    option = st.sidebar.selectbox(
        "What do you need?",
        ["Generate Lesson Plan", "Create Test Questions", "Help Students"]
    )

    if option == "Generate Lesson Plan":
        st.subheader("Generate a Realistic Lesson Plan")
        subject = st.text_input("Enter the subject (e.g., Mathematics)", value="Mathematics")
        topic = st.text_input("Enter the topic or main focus of the lesson (e.g., addition)", value="addition")
        grade = st.selectbox(
            "Grade Level",
            ["Kindergarten", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"],
            index=0
        )
        level = st.selectbox("Student Proficiency Level", ["Beginner", "Intermediate", "Advanced"], index=0)
        duration = st.number_input("Lesson Duration (in minutes)", min_value=30, max_value=120, value=45)
        
        if st.button("Generate Plan"):
            prompt = f"Create a realistic lesson plan in English for teaching {subject}, focusing on {topic}, " \
                     f"to {grade} grade students at a {level} level in a {duration}-minute class. The plan must include:\n" \
                     f"- **Learning Objectives**: What students will master related to {topic} based on their level.\n" \
                     f"- **Introduction ({duration//6} minutes)**: An interactive activity linking {topic} to prior knowledge.\n" \
                     f"- **Teaching and Application ({2*duration//3} minutes)**: Explanation of {topic} with examples and a level-appropriate hands-on activity.\n" \
                     f"- **Conclusion and Assessment ({duration//6} minutes)**: A question or task to assess understanding of {topic}.\n" \
                     f"Focus on making the plan practical, curriculum-aligned, and suitable for the given time."
            with st.spinner("Generating..."):
                plan = query_llm(model,prompt)
            st.subheader(f"Lesson Plan: {subject} - {topic} for {grade} Grade ({level})")
            st.markdown(plan)

    elif option == "Create Test Questions":
        st.subheader("Create Test Questions with Answers")
        topic = st.text_input("Enter the topic (e.g., Science)")
        uploaded_file = st.file_uploader("Upload a PDF with material (optional)", type="pdf")
        mcq_count = st.number_input("Number of Multiple Choice Questions (MCQ)", min_value=0, max_value=20, value=1)
        written_count = st.number_input("Number of Written Questions", min_value=0, max_value=20, value=0)
        tf_count = st.number_input("Number of True/False Questions", min_value=0, max_value=20, value=0)
        
        total_questions = mcq_count + written_count + tf_count
        
        if total_questions == 0:
            st.warning("Please select at least one question!")
        elif st.button("Generate Questions"):
            prompt_parts = []
            if mcq_count > 0:
                prompt_parts.append(f"exactly {mcq_count} multiple choice questions (MCQ) with 4 options each")
            if written_count > 0:
                prompt_parts.append(f"exactly {written_count} open-ended written questions")
            if tf_count > 0:
                prompt_parts.append(f"exactly {tf_count} true or false questions")
            
            base_prompt = f"Create test questions in English as follows: {', '.join(prompt_parts)}. " \
                          f"Do NOT include answers immediately after each question. " \
                          f"Instead, provide all correct answers in a separate 'Answer Key' section at the end. " \
                          f"For MCQs, list the correct option (e.g., 'c'); for written questions, provide a concise answer; " \
                          f"for true/false, state 'True' or 'False'. Format questions under clear section headers: " \
                          f"'Multiple Choice Questions (MCQ)', 'Open-Ended Written Questions', and 'True or False Questions'."
            
            if uploaded_file:
                material_text = extract_text_from_pdf(uploaded_file)
                prompt = f"Based on the following material: '{material_text[:2000]}' (truncated for brevity), " \
                         f"create test questions about {topic}. {base_prompt}"
            else:
                prompt = f"Create test questions about {topic}. {base_prompt}"
            
            with st.spinner("Generating..."):
                questions_and_answers = query_llm(model,prompt)
            
            st.subheader("Questions:")
            if "Answer Key" in questions_and_answers:
                questions_only = questions_and_answers.split("Answer Key")[0].strip()
                st.write(questions_only)
            else:
                questions_only = questions_and_answers
                st.write(questions_only)
            
            pdf_buffer = create_questions_pdf(topic, questions_only)
            st.download_button(
                label="Download Questions as PDF",
                data=pdf_buffer,
                file_name=f"{topic}_questions.pdf",
                mime="application/pdf"
            )
            
            if "Answer Key" in questions_and_answers:
                st.subheader("Answer Key:")
                st.write(questions_and_answers.split("Answer Key")[1].strip())

    elif option == "Help Students":
        student_question = st.text_area("Enter the student's question")
        if st.button("Answer"):
            prompt = f"Answer the following question in a simple way in English: {student_question}"
            with st.spinner("Generating..."):
                answer = query_llm(model,prompt)
            st.subheader("Answer:")
            st.write(answer)

if __name__ == "__main__":
    main()
