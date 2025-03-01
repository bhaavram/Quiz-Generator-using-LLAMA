def process_response(response_content, expected_count=0):
    """Process the response and ensure only numbers are in the Correct Answer column"""
    response_lines = response_content.split("\n")
    questions = []
    question, options, correct_answer = None, [], None

    answer_map = {"A": "1", "B": "2", "C": "3", "D": "4"}  # Map letters to numbers

    for line in response_lines:
        line = line.strip()
        if line.startswith("Q:"):
            if question and len(options) == 4 and correct_answer:
                questions.append((question, options, correct_answer))
            question = line.replace("Q:", "").strip()
            options = []
            correct_answer = None
        elif line.startswith(("A)", "B)", "C)", "D)")):
            parts = line.split(") ", 1)
            if len(parts) > 1:
                options.append(parts[1])
            else:
                options.append("Option Missing")
        elif line.startswith("Correct Answer:"):
            answer_letter = line.replace("Correct Answer:", "").strip()
            correct_answer = answer_map.get(answer_letter, "1")  # Default to "1" if invalid

    if question and len(options) == 4 and correct_answer:
        questions.append((question, options, correct_answer))
    return questions[:expected_count]