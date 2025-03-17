def process_response(response_content, expected_count=0):
    """Process the response and ensure only valid and unique questions are included."""
    response_lines = response_content.strip().split("\n")
    questions = []
    question, options, correct_answer = None, [], None

    answer_map = {"A": "1", "B": "2", "C": "3", "D": "4"}

    for line in response_lines:
        line = line.strip()

        if line.startswith("Q:"):
            if question and len(options) == 4 and correct_answer in answer_map.values():
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
            correct_answer = answer_map.get(answer_letter)

    # Validate the final question and correct answer
    if question and len(options) == 4 and correct_answer in answer_map.values():
        questions.append((question, options, correct_answer))

    # Filter out duplicate questions
    unique_questions = []
    seen = set()
    for q in questions:
        if q[0] not in seen and len(unique_questions) < expected_count:
            unique_questions.append(q)
            seen.add(q[0])

    return unique_questions
