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
    
    Compare the student's attempt to the correct solution and provide clear, actionable feedback based on this comparison. 
    
    - **Explain the Mistake:** Highlight the specific differences between the student's code and the correct solution in a constructive way. Focus on where their logic or implementation diverges and provide clear guidance on how to approach these differences.
      
    - **Provide a Hint to Fix It:** Offer a hint that directly addresses the mistake or misunderstanding, but without revealing the correct solution outright. Use the context of the correct solution to guide your hint, ensuring it aligns with the question's objective.
    
    - **Key Rules for Feedback:**
        - If the student’s function contains placeholders (e.g., ellipsis), assume the student has not yet attempted the problem and encourage them to make an attempt.
        - Avoid mentioning or referencing the document or any external materials. The student should feel that the feedback is derived naturally from their work and the context of the exercise.
        - Do not reference the correct solution explicitly, even if the student’s attempt is incorrect. Instead, guide them toward reevaluating their approach by pointing out key faults or missteps in their code.
        - Focus only on the comparison of the student’s code and the correct solution. Do not raise alarms about missing imports, non-standard functions, or unrelated implementation details unless they are critical to the task.
        
    Your response should aim to educate the student on how to think about the problem, how to analyze their own solution, and how to iterate toward the correct one.
    """

    feedback = chatcompletion(prompt, messages = [], temperature = 0.7, model="gpt-4o")

    # Return the response
    return jsonify({'response': feedback})


if __name__ == '__main__':
    app.run(debug=True)
