from langchain_ollama import ChatOllama
from process_response import process_response

def generate_mc_questions(text, num_mc):
    """Generate multiple-choice questions using LLaMA 3"""
    model = ChatOllama(model="llama3.2:3b", base_url="http://localhost:11434/")
    mc_prompt = (
        f"Generate exactly {num_mc} multiple-choice questions from the following text:\n{text}\n"
        "Ensure the questions and correct answers are directly based on the provided text. Do NOT make up facts.\n"
        "Each question must have 4 answer choices labeled as A, B, C, D, and the correct answer should be explicitly mentioned as A, B, C, or D.\n"
        "Format:\n"
        "Q: <question text>?\n"
        "A) <option 1>\nB) <option 2>\nC) <option 3>\nD) <option 4>\n"
        "Correct Answer: <A, B, C, or D>"
    )
    mcqs = []
    while len(mcqs) < num_mc:
        mc_response = model.invoke(mc_prompt)
        mcqs = process_response(mc_response.content, expected_count=num_mc)
    return mcqs