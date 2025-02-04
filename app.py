from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import get_solution, chatcompletion
import openai

# Get the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Pierrepont Student!"

@app.route('/feedback', methods=['POST'])
def feedback_response():
    # Get parameters from the request
    file_name = request.form.get('file_name')
    exercise_number = request.form.get('exercise_number')
    student_attempt = request.form.get('text')
    search_result = get_solution(exercise_number, file_name)

    # Define user Prompt
    prompt = f"""
    A student was presented with the following question:
    ```
    {search_result[0].metadata["context_question"]}
    ```
    
    The actual (correct) solution to the question is given below:
    ```
    {search_result[0].page_content}
    ```
    
    To this end, they provided the following function as their response (attempt). Student's attempt:
    ```
    {student_attempt}
    ```
    
    Compare the students attempt to the correct solution and provide feedback to the student.
    - Explain the mistake and give a hint to help them fix it, without revealing the correct solution.
    - You can only claim that a student is yet to attempt the problem if the placeholders i.e ellipsis still exists in the function block instead of an answer attempt.
    - The correct answer must not be referenced if a students gets the answer wrong. Instead prompt them to try again by highlighting subtle hints in the fault of their approach or response.
    - Don't refer to the document. The student don't need to know that you are sourcing from a document.
    - Speak in the first person to the student as a tutor or reviewer.
    """

    feedback = chatcompletion(prompt, temperature = 0.7, model="gpt-4o")

    # Return the response
    return jsonify({'response': feedback})


if __name__ == '__main__':
    app.run(debug=True)
