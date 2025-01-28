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
    reference_solution = get_solution(exercise_number, file_name)

    # Define user Prompt
    prompt = f"""
    A student has written the following code:
    ```
    {student_attempt}
    ```

    The correct (actual) solution can be extracted from the function in the text here:
    ```
    {reference_solution}
    ```

    Compare the students attempt to the correct solution and provide feedback to the student.
    - Explain the mistake and give a hint to help them fix it, without revealing the correct solution.
        - From the correct solution, you should have an idea of the question objective. Use that to provide hints and feedback
        - Neglect the absence of importing modules. You might see some non-standard function like make_array or a previously defined function. No need to raise alarms. Just focus on compairing the student attempt with the actual solution.
    - You can only claim that a student is yet to attempt the problem if the placeholders i.e ellipsis still exists in the function block instead of an answer attempt.
    - The correct answer must not be referenced if a students gets the answer wrong. Instead prompt them to try again by highlighting subtle hints in the fault of their approach or response.
    - Don't refer to the document. The student don't need to know that you are sourcing from a document.
    """

    feedback = chatcompletion(prompt, messages = [], temperature = 0.7, model="gpt-4o")

    # Return the response
    return jsonify({'response': feedback})


if __name__ == '__main__':
    app.run(debug=True)
