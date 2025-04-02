from langchain_ollama import ChatOllama
from process_response import process_response

model = ChatOllama(model="llama3", base_url="http://localhost:11434/", temperature=0.5)


def construct_mcq_prompt(text, complexity, num_questions):
    mc_prompt = f"""
                From the following academic text, generate exactly {num_questions} 
                {'simple' if complexity == 'simple' else 'complex'} multiple-choice questions.
                These questions must be 100% based on the text and the correct answers must be correct for sure.
                - Simple questions should focus on direct facts from the text.
                - Complex questions should require critical thinking and deeper understanding.
                - Include exactly four unique and plausible options.
                - Ensure the correct answer is explicitly labeled as A, B, C, or D.
                - Avoid ambiguity and irrelevant information.
                - Do no use the same format as given examples below, but use the depth of the questions
                - Vary the question phrasing across the set.
                - Do not use "According to the text" and similar phrases in the questions
                - Use scenarios, cause-effect, hypothetical questions, or applied logic.
                - Avoid repeating phrases or formats across questions.
                - Do not start multiple questions with the same wording (e.g., “What is…” or “Which of the following…”).
                - Use a variety of phrasing styles:
                    - ✅ Scenario-based: “A developer needs to...”
                    - ✅ Cause-effect: “What could happen if...”
                    - ✅ Applied reasoning: “Why might a team choose...”
                    - ✅ Instructional: “How should you respond when...”
                    - ✅ Factual: “What does the `git revert` command do?”
                - Maintain clarity and grammar. Avoid ambiguity or overly verbose questions.
                - Keep the tone technical, but conversational if needed.
                - Avoid primary benefit questions. use different phrase instead

                Text:
                {text}

                Example format for simple question:
                Q: What is a commit in Git?
                A) A code review request  
                B) A record of changes made to the repository  
                C) A branch merge failure  
                D) A deletion of a repository  
                Correct Answer: B

                Q: Which design principle states that each class should have only one responsibility?
                A) Open-Closed Principle  
                B) Interface Segregation Principle  
                C) Single Responsibility Principle  
                D) Liskov Substitution Principle  
                Correct Answer: C

                Example Format for Complex question:

                Q: Which of the following scenarios best highlights the advantage of using Git over traditional file storage methods?
                A) Saving a backup copy of a single file on an external drive  
                B) Collaborating on a shared document via email attachments  
                C) Managing concurrent changes to code with a full history of revisions  
                D) Uploading code to a cloud drive for storage  
                Correct Answer: C


                Q: What might be a consequence of neglecting modular design in a large-scale software system?
                A) Faster compile times due to fewer files  
                B) Increased test coverage due to consolidated code  
                C) Higher maintainability due to reduced complexity  
                D) Tight coupling that limits flexibility and reusability  
                Correct Answer: D

                Now, generate the questions accordingly.
                """

    return mc_prompt


def generate_mc_questions(text, num_mc, force_simple=None):
    # print(f"\n🟡 Generating {num_mc} MCQs | force_simple={force_simple}")

    if force_simple is True:
        prompt = construct_mcq_prompt(text, 'simple', num_mc)
        # print("📝 Prompt (Simple):", prompt[:500], "...")
        response = model.invoke(prompt)
        # print("📥 Model response:", response.content[:300])
        return process_response(response.content, expected_count=num_mc)

    else:
        prompt = construct_mcq_prompt(text, 'complex', num_mc)
        # print("📝 Prompt (Complex):", prompt[:500], "...")
        response = model.invoke(prompt)
        # print("📥 Model response:", response.content[:300])
        return process_response(response.content, expected_count=num_mc)


