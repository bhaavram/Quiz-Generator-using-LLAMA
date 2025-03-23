from langchain_ollama import ChatOllama
from process_response import process_response


def generate_mc_questions(text, num_mc):
    """Generate multiple-choice questions ensuring 20% are simple and all answers are 100% correct."""
    model = ChatOllama(model="llama3", base_url="http://localhost:11434/",temperature=0.3)

    # Calculate the number of simple and complex questions
    num_simple = max(1, int(num_mc * 0.2))  # Ensure at least 1 simple question
    num_complex = num_mc - num_simple

    def generate_questions(sub_text, complexity, num_questions):
        """Helper function to generate questions with specified complexity."""
        mc_prompt = (
            f"From the following academic text, generate exactly {num_questions} "
            f"{'simple' if complexity == 'simple' else 'complex'} multiple-choice questions.\n"
            "These questions must be 100% based on the text and the correct answers must be accurate.\n"
            "- Simple questions should focus on direct facts from the text.\n"
            "- Complex questions should require critical thinking and deeper understanding.\n"
            "- Include exactly four unique and plausible options.\n"
            "- Ensure the correct answer is explicitly labeled as A, B, C, or D.\n"
            "- Avoid ambiguity and irrelevant information.\n\n"
            "Text:\n{text}\n\n"
            "Example Format:\n"
            "Q: What is the main purpose of version control?\n"
            "A) To track and manage changes to files over time.\n"
            "B) To compile code efficiently.\n"
            "C) To secure the code from unauthorized access.\n"
            "D) To automatically fix code errors.\n"
            "Correct Answer: A\n\n"
            "Now, generate the questions accordingly."
        )

        formatted_prompt = mc_prompt.format(text=sub_text)
        mc_response = model.invoke(formatted_prompt)
        return process_response(mc_response.content, expected_count=num_questions)

    # Generate simple and complex questions separately
    simple_questions = generate_questions(text, 'simple', num_simple)
    complex_questions = generate_questions(text, 'complex', num_complex)

    # Combine and ensure uniqueness
    combined_questions = []
    seen_questions = set()

    for q in simple_questions + complex_questions:
        if q[0] not in seen_questions:
            combined_questions.append(q)
            seen_questions.add(q[0])

        if len(combined_questions) == num_mc:
            break

    return combined_questions
