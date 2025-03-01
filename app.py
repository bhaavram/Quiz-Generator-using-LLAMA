import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import pandas as pd
from create_zip import create_zip
from convert_df_to_qti import convert_df_to_qti
from generate_mc_questions import generate_mc_questions

def extract_text_from_pdf(pdf_path):
    """Extract text from uploaded PDF file while ignoring images"""
    text = ""
    doc = fitz.open(stream=pdf_path.read(), filetype="pdf")

    for page in doc:
        for block in page.get_text("blocks"):
            if block[6] == 0:  # Ensure only text blocks are considered (not images)
                text += block[4] + "\n"
    return text


def main():
    st.title("📄 AI-Powered MCQ Generator")
    st.write("Upload a PDF, generate questions, and create a QTI file for your quiz!")

    uploaded_file = st.file_uploader("Upload your document (PDF)", type=["pdf"])
    num_mc = st.number_input("Number of multiple-choice questions", min_value=1, max_value=20, value=5)
    total_marks = st.number_input("Total marks for the quiz", min_value=1, value=10)

    # New widget: Number of attempts allowed (defaults to 1 if not provided)
    attempts_allowed = st.number_input("Maximum attempts allowed", min_value=1, value=1)

    if uploaded_file is not None and st.button("Generate Questions"):
        text = extract_text_from_pdf(uploaded_file)
        st.write("✅ Document uploaded successfully! Generating questions...")
        questions = generate_mc_questions(text, num_mc)
        marks_per_question = round(total_marks / num_mc, 2)

        data = []
        for question, options, correct_answer in questions:
            row = ["MC", "", marks_per_question, question, correct_answer] + options + [""]
            data.append(row)
        columns = ["Type", "Unused", "Points", "Question", "CorrectAnswer",
                   "Option A", "Option B", "Option C", "Option D", "Option E"]
        df = pd.DataFrame(data, columns=columns)
        st.session_state.df = df

    if "df" in st.session_state:
        st.write("✏️ Edit the table below before downloading:")
        edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")
        st.session_state.df = edited_df

        # Convert the DataFrame to QTI XML content, using the attempts_allowed value

        qti_content = convert_df_to_qti(edited_df, attempts_allowed)
        zip_buffer = create_zip(qti_content)

        st.download_button(
            label="📥 Download QTI as ZIP",
            data=zip_buffer,
            file_name="quiz.zip",
            mime="application/zip"
        )


if __name__ == "__main__":
    main()
