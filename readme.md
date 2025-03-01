📄 AI-Powered MCQ Generator with LLaMA 3.2-Vision

This Streamlit application allows users to upload a PDF document, extract text (including from images using LLaMA 3.2-Vision), generate Multiple-Choice Questions (MCQs), and export them as a QTI-compliant XML file for Learning Management Systems (LMS).

🚀 Features
* Extract Text from PDFs (including images using LLaMA 3.2-Vision).
* Generate Multiple-Choice Questions (MCQs) using LLaMA 3.2.
* Edit MCQs before exporting.
* Export as QTI XML for importing into LMS platforms (e.g., Canvas, Blackboard, Moodle).

📦 Installation

1️⃣ Clone the Repository

git clone https://github.com/your-repo/ai-mcq-generator.git
cd ai-mcq-generator

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Ensure LLaMA 3.2 is Running
**Download and install Ollama from [ollama.com]()**

* If using Ollama, pull and serve the model:
* ollama pull llama3.2
* ollama serve

🏃‍♂️ Running the App

* streamlit run app.py
* Then, open the Streamlit interface in your browser.

📄 How It Works

* Upload a PDF (text-based or scanned with images).
* Extract text from the document.
* Generate MCQs based on extracted content.
* Edit the MCQs before exporting.
* Download the QTI XML file for LMS import.

