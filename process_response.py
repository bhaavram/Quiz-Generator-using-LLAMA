def process_response(response_content, expected_count=0):
    """Process the response and ensure only numbers are in the Correct Answer column."""
    response_lines = response_content.strip().split("\n")
    questions = []
    question, options, correct_answer = None, [], None

    answer_map = {"A": "1", "B": "2", "C": "3", "D": "4"}  # Map letters to numbers

    for line in response_lines:
        line = line.strip()
        if line.startswith("Q:"):
            if question and len(options) == 4 and correct_answer is not None:
                questions.append((question, options, correct_answer))
            question = line[2:].strip()
            options = []
            correct_answer = None
        elif line[:2] in {"A)", "B)", "C)", "D)"}:
            parts = line.split(") ", 1)
            if len(parts) > 1:
                options.append(parts[1].strip())
            else:
                options.append("Option Missing")
        elif line.startswith("Correct Answer:"):
            answer_letter = line.replace("Correct Answer:", "").strip()
            if answer_letter in answer_map:
                correct_answer = answer_map[answer_letter]
            else:
                correct_answer = None  # Don't default to "1", keep it as None if invalid

    # Append the last question if it meets conditions
    if question and len(options) == 4 and correct_answer is not None:
        questions.append((question, options, correct_answer))

    return questions[:expected_count] if expected_count else questions
