import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import pandas as pd
from create_zip import create_zip
from convert_df_to_qti import convert_df_to_qti
from generate_mc_questions import generate_mc_questions
import tiktoken
import random

def extract_text_chunks_from_pdf(pdf_file, pages_per_chunk=5):
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

    chunks = []
    current_chunk = ""

    for i, page in enumerate(doc, start=1):
        current_chunk += page.get_text() + "\n"
        if i % pages_per_chunk == 0:
            chunks.append(current_chunk.strip())
            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def chunk_text_by_tokens(text, max_tokens=1000):
    encoder = tiktoken.get_encoding("gpt2")
    tokens = encoder.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks

def main():
    st.title("📄 AI-Powered MCQ Generator")
    st.write("Upload a PDF, generate questions, and create a QTI file for your quiz!")

    uploaded_file = st.file_uploader("Upload your document (PDF)", type=["pdf"])
    num_mc = st.number_input("Number of multiple-choice questions", min_value=1, max_value=50)
    total_marks = st.number_input("Total marks for the quiz", min_value=1)
    attempts_allowed = st.number_input("Maximum attempts allowed", min_value=1, value=1)

    col1, col2 = st.columns(2)
    with col1:
        simple_pct = st.slider("Percentage of Simple Questions", 0, 100, 20)
    with col2:
        complex_pct = 100 - simple_pct
        st.markdown(f"**Percentage of Complex Questions:** {complex_pct}%")

    if uploaded_file is not None and st.button("Generate Questions"):
        # Step 1: Break PDF into token-based chunks
        page_chunks = extract_text_chunks_from_pdf(uploaded_file, pages_per_chunk=5)
        text_chunks = page_chunks

        # Step 2: Generate questions from each chunk
        all_candidates = []

        for chunk in text_chunks:
            num_simple = max(1, int((simple_pct / 100) * num_mc))
            num_complex = num_mc - num_simple

            simple_questions = generate_mc_questions(chunk, num_simple, force_simple=True)
            complex_questions = generate_mc_questions(chunk, num_complex, force_simple=False)

            for q in simple_questions:
                all_candidates.append((*q, "Simple"))
            for q in complex_questions:
                all_candidates.append((*q, "Complex"))

        st.session_state.all_candidates = all_candidates  # Save for shuffling

    if "all_candidates" in st.session_state and st.button("🔀 Shuffle and Select Questions"):
        all_candidates = st.session_state.all_candidates
        random.shuffle(all_candidates)
        total_simple_needed = max(1, int((simple_pct / 100) * num_mc))
        total_complex_needed = num_mc - total_simple_needed

        final_simple = [q for q in all_candidates if q[-1] == "Simple"][:total_simple_needed]
        final_complex = [q for q in all_candidates if q[-1] == "Complex"][:total_complex_needed]

        final_questions = final_simple + final_complex
        random.shuffle(final_questions)

        st.write(f"✅ Final selection: {len(final_simple)} simple, {len(final_complex)} complex")

        # Convert to DataFrame
        data = []
        for question, options, correct_answer, difficulty in final_questions:
            while len(options) < 5:
                options.append("")  # pad options to always have 5 (A–E)
            row = ["MC", "", total_marks / num_mc, question, correct_answer] + options + [difficulty]
            data.append(row)

        columns = ["Type", "Unused", "Points", "Question", "CorrectAnswer",
                   "Option A", "Option B", "Option C", "Option D", "Option E", "Difficulty"]
        df = pd.DataFrame(data, columns=columns)
        st.session_state.df = df

    if "df" in st.session_state:
        st.write("✍️ Edit the table below before downloading:")
        edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")
        st.session_state.df = edited_df

        qti_content = convert_df_to_qti(edited_df, attempts_allowed)
        zip_buffer = create_zip(qti_content)

        st.download_button(
            label="📅 Download QTI as ZIP",
            data=zip_buffer,
            file_name="quiz.zip",
            mime="application/zip"
        )

if __name__ == "__main__":
    main()