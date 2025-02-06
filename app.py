import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import openai

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database Credentials
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
TABLE_NAME = "exercise_store" 

# OpenAI API Key (Store securely)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Create Database Engine
engine = create_engine(
    f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    pool_size=10,
    max_overflow=5,
    pool_recycle=1800,
    pool_pre_ping=True
)
@app.route('/feedback', methods=['POST'])
def feedback_response():
    """
    API endpoint to receive student attempts and provide feedback.

    Expected JSON Payload:
    {
        "file_name": "hw03",
        "exercise_number": "1",
        "student_attempt": "def student_code():\n    return None"
    }
    """
    try:
        data = request.get_json()
        file_name = data.get("file_name")
        exercise_number = data.get("exercise_number")
        student_attempt = data.get("student_attempt")

        if not file_name or not exercise_number or not student_attempt:
            return jsonify({'error': 'Missing required parameters'}), 400

        context_question, answer = get_exercise_details(file_name, exercise_number)
        if not context_question or not answer:
            return jsonify({'error': 'Exercise details not found'}), 404

        # Define user Prompt
        prompt = f"""
        A student was presented with the following question:
        ```
        {context_question}
        ```

        The actual (correct) solution to the question is given below:
        ```
        {answer}
        ```

        To this end, they provided the following function as their response (attempt). Student's attempt:
        ```
        {student_code}
        ```

        Compare the students attempt to the correct solution and provide feedback to the student.
        - Explain the mistake and give a hint to help them fix it, without revealing the correct solution.
        - You can only claim that a student is yet to attempt the problem if the placeholders i.e ellipsis still exists in the function block instead of an answer attempt.
        - The correct answer must not be referenced if a students gets the answer wrong. Instead prompt them to try again by highlighting subtle hints in the fault of their approach or response.
        - Don't refer to the document. The student don't need to know that you are sourcing from a document.
        - Speak in the first person to the student as a tutor or reviewer.
        """

        feedback = chatcompletion(prompt)
        return jsonify({'response': feedback})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
