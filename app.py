import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import pandas as pd
from create_zip import create_zip
from convert_df_to_qti import convert_df_to_qti
from generate_mc_questions import generate_mc_questions
import tiktoken  # For token-based text chunking


def extract_text_chunks_from_pdf(pdf_file, pages_per_chunk=5):
    """Extract text from a PDF file in chunks of a specified number of pages."""
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
    """Chunk text based on token count to fit within the model's limit."""
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
    num_mc = st.number_input("Number of multiple-choice questions", min_value=1, max_value=20, value=5)
    total_marks = st.number_input("Total marks for the quiz", min_value=1, value=10)

    # New widget: Number of attempts allowed (defaults to 1 if not provided)
    attempts_allowed = st.number_input("Maximum attempts allowed", min_value=1, value=1)

    if uploaded_file is not None and st.button("Generate Questions"):
        # Step 1: Extract PDF text in page chunks
        page_chunks = extract_text_chunks_from_pdf(uploaded_file, pages_per_chunk=5)

        all_questions = []
        seen_questions = set()  # To ensure uniqueness
        total_chunks = len(page_chunks)

        # Step 2: Calculate minimum questions per chunk
        min_questions_per_chunk = max(1, num_mc // total_chunks)
        remaining_questions = num_mc

        # Step 3: First attempt to generate questions per chunk
        for page_chunk in page_chunks:
            text_chunks = chunk_text_by_tokens(page_chunk, max_tokens=1000)

            for text_chunk in text_chunks:
                questions_to_generate = min(min_questions_per_chunk, remaining_questions)
                questions = generate_mc_questions(text_chunk, questions_to_generate)

                # Filter and add unique questions
                for question in questions:
                    if question[0] not in seen_questions and len(all_questions) < num_mc:
                        all_questions.append(question)
                        seen_questions.add(question[0])

                remaining_questions = num_mc - len(all_questions)

                if remaining_questions <= 0:
                    break

            if remaining_questions <= 0:
                break

        # Step 4: Retry generating remaining questions from the entire PDF if count is short
        if remaining_questions > 0:
            combined_text = " ".join(page_chunks)
            additional_questions = generate_mc_questions(combined_text, remaining_questions)

            for question in additional_questions:
                if question[0] not in seen_questions and len(all_questions) < num_mc:
                    all_questions.append(question)
                    seen_questions.add(question[0])

        st.write(f"✅ Generated {len(all_questions)} questions successfully!")

        # Step 5: Display and edit the questions
        data = []
        for question, options, correct_answer in all_questions:
            row = ["MC", "", 2, question, correct_answer] + options + [""]  # 2 is a placeholder for marks
            data.append(row)

        columns = ["Type", "Unused", "Points", "Question", "CorrectAnswer",
                   "Option A", "Option B", "Option C", "Option D", "Option E"]
        df = pd.DataFrame(data, columns=columns)
        st.session_state.df = df

    if "df" in st.session_state:
        st.write("✏️ Edit the table below before downloading:")
        edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")
        st.session_state.df = edited_df

        # Convert the DataFrame to QTI XML content
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
